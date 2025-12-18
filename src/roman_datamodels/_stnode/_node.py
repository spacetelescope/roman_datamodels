"""
Base node classes for all STNode classes.
    These are the base classes for the data objects used by the datamodels package.
"""

from __future__ import annotations

import datetime
from collections.abc import MutableMapping, MutableSequence
from typing import TYPE_CHECKING

import numpy as np
from asdf.lazy_nodes import AsdfDictNode, AsdfListNode
from asdf.tags.core import ndarray
from astropy.time import Time

__all__ = ["DNode", "LNode"]


def _wrap(value):
    """
    Convert dict to DNode and list to LNode
    """
    # Return objects as node classes, if applicable
    if isinstance(value, dict | AsdfDictNode):
        return DNode(value)

    if isinstance(value, list | AsdfListNode):
        return LNode(value)

    return value


def _unwrap(value):
    """
    Convert DNode to dict and LNode to list
    """
    # use "type(...) is" so that we don't unwrap subclasses
    if type(value) is DNode:
        return value._data

    if type(value) is LNode:
        return value.data

    return value


class _NodeMixin:
    """
    Mixin class to provide the common API for all Node objects
    """

    # This is a hack to avoid mypy and __slots__ inheritance issues concerning `_read_tag`
    #    ideally we would just define `_read_tag` like we did below, but mypy gets upset because
    #    __slots__ is defined so that the subclasses will be fully slotted. You can't have the
    #    same slot attributed defined in both parent classes when they are mixed together.
    if TYPE_CHECKING:
        __slots__ = ("_read_tag",)
    else:
        __slots__ = ()

    _read_tag: str | None

    def __init__(self, *args, **kwargs):
        self._read_tag = None


class DNode(MutableMapping, _NodeMixin):
    """
    Base class describing all "object" (dict-like) data nodes for STNode classes.
    """

    __slots__ = ("_data", "_read_tag")

    def __init__(self, node=None):
        super().__init__(node)

        # Handle if we are passed different data types
        if node is None:
            self._data = {}
        elif isinstance(node, dict | AsdfDictNode):
            self._data = node
        else:
            raise ValueError("Initializer only accepts dicts")

    def __getattr__(self, key):
        """
        Permit accessing dict keys as attributes, assuming they are legal Python
        variable names.
        """
        # Private values should have already been handled by the __getattribute__ method
        #   bail out if we are falling back on this method
        if key.startswith("_"):
            raise AttributeError(f"No attribute {key}")

        # If the key is in the schema, then we can return the value
        if key in self._data:
            # Return objects as node classes, if applicable
            return _wrap(self._data[key])

        # Raise the correct error for the attribute not being found
        raise AttributeError(f"No such attribute ({key}) found in node: {type(self)}")

    def __setattr__(self, key, value):
        """
        Permit assigning dict keys as attributes.
        """

        # Private keys should just be in the normal __dict__
        if key[0] != "_":
            # Finally set the value
            self._data[key] = _unwrap(value)
        else:
            if key in DNode.__slots__:
                DNode.__dict__[key].__set__(self, value)
            else:
                raise AttributeError(f"Cannot set private attribute {key}, only allowed are {DNode.__slots__}")

    def __delattr__(self, name):
        if name in self.__slots__:
            super().__delattr__(name)

        elif name[0] != "_":
            self.__delitem__(name)

        else:
            raise AttributeError(f"No such attribute ({name}) found in node")

    def _recursive_items(self):
        def recurse(tree, path=None):
            path = path or []  # Avoid mutable default arguments
            if isinstance(tree, DNode | dict | AsdfDictNode):
                for key, val in tree.items():
                    yield from recurse(val, [*path, key])
            elif isinstance(tree, LNode | list | tuple | AsdfListNode):
                for i, val in enumerate(tree):
                    yield from recurse(val, [*path, i])
            elif tree is not None:
                yield (".".join(str(x) for x in path), tree)

        yield from recurse(self)

    def to_flat_dict(self, include_arrays=True, recursive=False):
        """
        Returns a dictionary of all of the schema items as a flat dictionary.

        Each dictionary key is a dot-separated name.  For example, the
        schema element ``meta.observation.date`` will end up in the
        dictionary as::

            { "meta.observation.date": "2012-04-22T03:22:05.432" }

        """

        def convert_val(val):
            """
            Unwrap the tagged scalars if necessary.
            """
            if isinstance(val, datetime.datetime):
                return val.isoformat()
            elif isinstance(val, Time):
                return str(val)
            return val

        item_getter = self._recursive_items if recursive else self.items

        if include_arrays:
            return {key: convert_val(val) for (key, val) in item_getter()}
        else:
            return {
                key: convert_val(val) for (key, val) in item_getter() if not isinstance(val, np.ndarray | ndarray.NDArrayType)
            }

    def __asdf_traverse__(self):
        """Asdf traverse method for things like info/search"""
        return dict(self)

    def __len__(self):
        """Define length of the node"""
        return len(self._data)

    def __getitem__(self, key):
        """Dictionary style access data"""
        if key in self._data:
            return self._data[key]

        raise KeyError(f"No such key ({key}) found in node")

    def __setitem__(self, key, value):
        """Dictionary style access set data"""
        self._data[key] = value

    def __delitem__(self, key):
        """Dictionary style access delete data"""
        del self._data[key]

    def __dir__(self):
        return set(super().__dir__()) | set(self._data.keys())

    def __iter__(self):
        """Define iteration"""
        return iter(self._data)

    def __repr__(self):
        """Define a representation"""
        return repr(self._data)

    def copy(self):
        """Handle copying of the node"""
        instance = self.__class__.__new__(self.__class__)

        instance._read_tag = self._read_tag
        instance._data = self._data.copy()

        return instance


class LNode(MutableSequence, _NodeMixin):
    """
    Base class describing all "array" (list-like) data nodes for STNode classes.
    """

    __slots__ = ("_read_tag", "data")

    def __init__(self, node=None):
        super().__init__(node=node)

        if node is None:
            self.data = []
        elif isinstance(node, list | AsdfListNode):
            self.data = node
        elif isinstance(node, self.__class__):
            self.data = node.data
        else:
            raise ValueError("Initializer only accepts lists")

    def __getitem__(self, index):
        return _wrap(self.data[index])

    def __setitem__(self, index, value):
        self.data[index] = _unwrap(value)

    def __delitem__(self, index):
        del self.data[index]

    def __len__(self):
        return len(self.data)

    def insert(self, index, value):
        self.data.insert(index, value)

    def __asdf_traverse__(self):
        return list(self)

    def __setattr__(self, key, value):
        if key in LNode.__slots__:
            LNode.__dict__[key].__set__(self, value)
        else:
            raise AttributeError(f"Cannot set attribute {key}, only allowed are {LNode.__slots__}")

    def __eq__(self, other):
        if isinstance(other, LNode):
            return self.data == other.data
        elif isinstance(other, list | AsdfListNode):
            return self.data == other
        else:
            return False

    def copy(self):
        """Handle copying of the node"""
        instance = self.__class__.__new__(self.__class__)

        instance.data = self.data.copy()
        instance._read_tag = self._read_tag
        return instance
