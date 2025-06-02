"""
Base node classes for all STNode classes.
    These are the base classes for the data objects used by the datamodels package.
"""

import datetime
from collections import UserList
from collections.abc import MutableMapping

import numpy as np
from asdf.lazy_nodes import AsdfDictNode, AsdfListNode
from asdf.tags.core import ndarray
from astropy.time import Time

from ._registry import SCALAR_NODE_CLASSES_BY_KEY

__all__ = ["DNode", "LNode"]


class DNode(MutableMapping):
    """
    Base class describing all "object" (dict-like) data nodes for STNode classes.
    """

    _pattern = None

    def __init__(self, node=None, parent=None, name=None):
        # Handle if we are passed different data types
        if node is None:
            self.__dict__["_data"] = {}
        elif isinstance(node, dict | AsdfDictNode):
            self.__dict__["_data"] = node
        else:
            raise ValueError("Initializer only accepts dicts")

        # Set the metadata tracked by the node
        self._parent = parent
        self._name = name

    @staticmethod
    def _convert_to_scalar(key, value, ref=None):
        """Find and wrap scalars in the appropriate class, if its a tagged one."""
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
            if isinstance(value, dict | AsdfDictNode):
                return DNode(value, parent=self, name=key)

            elif isinstance(value, list | AsdfListNode):
                return LNode(value)

            else:
                return value

        # Raise the correct error for the attribute not being found
        raise AttributeError(f"No such attribute ({key}) found in node")

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
            self.__dict__[key] = value

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
        instance.__dict__.update(self.__dict__.copy())
        instance.__dict__["_data"] = self.__dict__["_data"].copy()

        return instance


class LNode(UserList):
    """
    Base class describing all "array" (list-like) data nodes for STNode classes.
    """

    _pattern = None

    def __init__(self, node=None):
        if node is None:
            self.data = []
        elif isinstance(node, list | AsdfListNode):
            self.data = node
        elif isinstance(node, self.__class__):
            self.data = node.data
        else:
            raise ValueError("Initializer only accepts lists")

    def __getitem__(self, index):
        value = self.data[index]
        if isinstance(value, dict | AsdfDictNode):
            return DNode(value)
        elif isinstance(value, list | AsdfListNode):
            return LNode(value)
        else:
            return value

    def __asdf_traverse__(self):
        return list(self)
