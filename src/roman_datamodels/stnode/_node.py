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
from semantic_version import Version

from ._registry import INTERNAL_WRAP_LIMITS, SCALAR_NODE_CLASSES_BY_KEY

if TYPE_CHECKING:
    from typing import ClassVar

__all__ = ["DNode", "LNode", "TaggedScalarDNode"]


def _convert_to_scalar(key, value, ref=None):
    """Wrap scalars in into a tagged scalar object"""
    from ._tagged import TaggedScalarNode

    if isinstance(ref, TaggedScalarNode):
        # we want the exact class (not possible subclasses)
        if type(value) == type(ref):  # noqa: E721
            return value
        return type(ref)(value)

    if isinstance(value, TaggedScalarNode):
        return value

    if key in SCALAR_NODE_CLASSES_BY_KEY:
        value = SCALAR_NODE_CLASSES_BY_KEY[key](value)

    return value


class DNode(MutableMapping):
    """
    Base class describing all "object" (dict-like) data nodes for STNode classes.
    """

    __slots__ = ("_data", "_name", "_parent", "_read_tag")

    _pattern: ClassVar[str]
    _latest_manifest: ClassVar[str]

    def __init__(self, node=None, parent=None, name=None):
        # Handle if we are passed different data types
        if node is None:
            self._data = {}
        elif isinstance(node, dict | AsdfDictNode):
            self._data = node
        else:
            raise ValueError("Initializer only accepts dicts")

        # Set the metadata tracked by the node
        self._parent = parent
        self._name = name
        self._read_tag = None

    def _convert_to_scalar(self, key, value, ref=None):
        """Find and wrap scalars in the appropriate class, if its a tagged one."""
        if self._read_tag is not None:
            base_tag, version = self._read_tag.rsplit("-", maxsplit=1)
            if (limit := INTERNAL_WRAP_LIMITS.get(base_tag)) is not None and Version(version) <= limit:
                return _convert_to_scalar(key, value, ref)

        return value

    def _wrap_value(self, key, value):
        # Return objects as node classes, if applicable
        if isinstance(value, dict | AsdfDictNode):
            return DNode(value, parent=self, name=key)

        if isinstance(value, list | AsdfListNode):
            return LNode(value)

        return value

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
            # Cast the value into the appropriate tagged scalar class
            value = self._convert_to_scalar(key, self._data[key])

            # Return objects as node classes, if applicable
            return self._wrap_value(key, value)

        # Raise the correct error for the attribute not being found
        raise AttributeError(f"No such attribute ({key}) found in node: {type(self)}")

    def __setattr__(self, key, value):
        """
        Permit assigning dict keys as attributes.
        """

        # Private keys should just be in the normal __dict__
        if key[0] != "_":
            # Wrap things in the tagged scalar classes if necessary
            value = self._convert_to_scalar(key, value, self._data.get(key))

            # Finally set the value
            self._data[key] = value
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

        # Convert the value to a tagged scalar if necessary
        value = self._convert_to_scalar(key, value, self._data.get(key))

        # If the value is a dictionary, loop over its keys and convert them to tagged scalars
        if isinstance(value, dict | AsdfDictNode):
            for sub_key, sub_value in value.items():
                value[sub_key] = self._convert_to_scalar(sub_key, sub_value)

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

        instance._parent = self._parent
        instance._name = self._name
        instance._read_tag = self._read_tag
        instance._data = self._data.copy()

        return instance


class TaggedScalarDNode(DNode):
    """Legacy class for nodes that have tagged scalars"""

    __slots__ = ()

    def _convert_to_scalar(self, key, value, ref=None):
        return _convert_to_scalar(key, value, ref)

    def _wrap_value(self, key, value):
        # Return objects as node classes, if applicable
        if isinstance(value, dict | AsdfDictNode):
            return TaggedScalarDNode(value, parent=self, name=key)

        if isinstance(value, list | AsdfListNode):
            return LNode(value)

        return value


class LNode(MutableSequence):
    """
    Base class describing all "array" (list-like) data nodes for STNode classes.
    """

    __slots__ = ("_read_tag", "data")

    _pattern: ClassVar[str]
    _latest_manifest: ClassVar[str]

    def __init__(self, node=None):
        if node is None:
            self.data = []
        elif isinstance(node, list | AsdfListNode):
            self.data = node
        elif isinstance(node, self.__class__):
            self.data = node.data
        else:
            raise ValueError("Initializer only accepts lists")

        self._read_tag = None

    def __getitem__(self, index):
        value = self.data[index]
        if isinstance(value, dict | AsdfDictNode):
            return DNode(value)
        elif isinstance(value, list | AsdfListNode):
            return LNode(value)
        else:
            return value

    def __setitem__(self, index, value):
        self.data[index] = value

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
