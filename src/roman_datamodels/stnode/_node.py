"""
Base node classes for all STNode classes.
    These are the base classes for the data objects used by the datamodels package.
"""
import datetime
import re
import warnings
from collections import UserList
from collections.abc import MutableMapping

import asdf
import asdf.schema as asdfschema
import asdf.yamlutil as yamlutil
import numpy as np
from asdf.exceptions import ValidationError
from asdf.tags.core import ndarray
from asdf.util import HashableDict
from astropy.time import Time

from roman_datamodels.validate import ValidationWarning, _check_type, _error_message, will_strict_validate, will_validate

from ._registry import SCALAR_NODE_CLASSES_BY_KEY

__all__ = ["DNode", "LNode"]

validator_callbacks = HashableDict(asdfschema.YAML_VALIDATORS)
validator_callbacks.update({"type": _check_type})


def _value_change(path, value, schema, pass_invalid_values, strict_validation, ctx):
    """
    Validate a change in value against a schema.
    Trap error and return a flag.
    """
    try:
        _check_value(value, schema, ctx)
        update = True

    except ValidationError as error:
        update = False
        errmsg = _error_message(path, error)
        if pass_invalid_values:
            update = True
        if strict_validation:
            raise ValidationError(errmsg)
        else:
            warnings.warn(errmsg, ValidationWarning)
    return update


def _check_value(value, schema, validator_context):
    """
    Perform the actual validation.
    """

    temp_schema = {"$schema": "http://stsci.edu/schemas/asdf-schema/0.1.0/asdf-schema"}
    temp_schema.update(schema)
    validator = asdfschema.get_validator(temp_schema, validator_context, validator_callbacks)

    validator.validate(value, _schema=temp_schema)
    validator_context.close()


def _validate(attr, instance, schema, ctx):
    tagged_tree = yamlutil.custom_tree_to_tagged_tree(instance, ctx)
    return _value_change(attr, tagged_tree, schema, False, will_strict_validate(), ctx)


def _get_schema_for_property(schema, attr):
    # Check if attr is a property
    subschema = schema.get("properties", {}).get(attr, None)

    # Check if attr is a pattern property
    props = schema.get("patternProperties", {})
    for key, value in props.items():
        if re.match(key, attr):
            subschema = value
            break

    if subschema is not None:
        return subschema
    for combiner in ["allOf", "anyOf"]:
        for subschema in schema.get(combiner, []):
            subsubschema = _get_schema_for_property(subschema, attr)
            if subsubschema != {}:
                return subsubschema

    return {}


class DNode(MutableMapping):
    """
    Base class describing all "object" (dict-like) data nodes for STNode classes.
    """

    _tag = None
    _ctx = None

    def __init__(self, node=None, parent=None, name=None):
        if node is None:
            self.__dict__["_data"] = {}
        elif isinstance(node, dict):
            self.__dict__["_data"] = node
        else:
            raise ValueError("Initializer only accepts dicts")
        self._x_schema = None
        self._schema_uri = None
        self._parent = parent
        self._name = name

    @property
    def ctx(self):
        if self._ctx is None:
            DNode._ctx = asdf.AsdfFile()
        return self._ctx

    @staticmethod
    def _convert_to_scalar(key, value):
        if key in SCALAR_NODE_CLASSES_BY_KEY:
            value = SCALAR_NODE_CLASSES_BY_KEY[key](value)

        return value

    def __getattr__(self, key):
        """
        Permit accessing dict keys as attributes, assuming they are legal Python
        variable names.
        """
        if key.startswith("_"):
            raise AttributeError(f"No attribute {key}")
        if key in self._data:
            value = self._convert_to_scalar(key, self._data[key])
            if isinstance(value, dict):
                return DNode(value, parent=self, name=key)
            elif isinstance(value, list):
                return LNode(value)
            else:
                return value
        else:
            raise AttributeError(f"No such attribute ({key}) found in node")

    def __setattr__(self, key, value):
        """
        Permit assigning dict keys as attributes.
        """
        if key[0] != "_":
            value = self._convert_to_scalar(key, value)
            if key in self._data:
                if will_validate():
                    schema = _get_schema_for_property(self._schema(), key)

                    if schema == {} or _validate(key, value, schema, self.ctx):
                        self._data[key] = value
                self.__dict__["_data"][key] = value
            else:
                raise AttributeError(f"No such attribute ({key}) found in node")
        else:
            self.__dict__[key] = value

    def to_flat_dict(self, include_arrays=True):
        """
        Returns a dictionary of all of the schema items as a flat dictionary.

        Each dictionary key is a dot-separated name.  For example, the
        schema element ``meta.observation.date`` will end up in the
        dictionary as::

            { "meta.observation.date": "2012-04-22T03:22:05.432" }

        """

        def convert_val(val):
            if isinstance(val, datetime.datetime):
                return val.isoformat()
            elif isinstance(val, Time):
                return str(val)
            return val

        if include_arrays:
            return {key: convert_val(val) for (key, val) in self.items()}
        else:
            return {
                key: convert_val(val) for (key, val) in self.items() if not isinstance(val, (np.ndarray, ndarray.NDArrayType))
            }

    def _schema(self):
        """
        If not overridden by a subclass, it will search for a schema from
        the parent class, recursing if necessary until one is found.
        """
        if self._x_schema is None:
            parent_schema = self._parent._schema()
            # Extract the subschema corresponding to this node.
            subschema = _get_schema_for_property(parent_schema, self._name)
            self._x_schema = subschema

        return self._x_schema

    def __asdf_traverse__(self):
        return dict(self)

    def __len__(self):
        return len(self._data)

    def __getitem__(self, key):
        if key in self._data:
            return self._data[key]

        raise KeyError(f"No such key ({key}) found in node")

    def __setitem__(self, key, value):
        value = self._convert_to_scalar(key, value)
        if isinstance(value, dict):
            for sub_key, sub_value in value.items():
                value[sub_key] = self._convert_to_scalar(sub_key, sub_value)
        self._data[key] = value

    def __delitem__(self, key):
        del self._data[key]

    def __iter__(self):
        return iter(self._data)

    def __repr__(self):
        return repr(self._data)

    def copy(self):
        instance = self.__class__.__new__(self.__class__)
        instance.__dict__.update(self.__dict__.copy())
        instance.__dict__["_data"] = self.__dict__["_data"].copy()

        return instance


class LNode(UserList):
    """
    Base class describing all "array" (list-like) data nodes for STNode classes.
    """

    _tag = None

    def __init__(self, node=None):
        if node is None:
            self.data = []
        elif isinstance(node, list):
            self.data = node
        elif isinstance(node, self.__class__):
            self.data = node.data
        else:
            raise ValueError("Initializer only accepts lists")

    def __getitem__(self, index):
        value = self.data[index]
        if isinstance(value, dict):
            return DNode(value)
        elif isinstance(value, list):
            return LNode(value)
        else:
            return value

    def __asdf_traverse__(self):
        return list(self)
