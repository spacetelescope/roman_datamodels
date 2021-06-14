"""
Proof of concept of using tags with the data model framework
"""

import sys
import warnings
import datetime
from abc import ABCMeta
from asdf.extension import Converter
from collections import UserList
import yaml
import jsonschema
import numpy as np

from astropy.time import Time
import asdf
import asdf.schema as asdfschema
import asdf.yamlutil as yamlutil
from asdf.util import HashableDict
from asdf.tags.core import ndarray
from .validate import _check_type, ValidationWarning, _error_message
import rad.resources
from .stuserdict import STUserDict as UserDict

if sys.version_info < (3, 9):
    import importlib_resources
else:
    import importlib.resources as importlib_resources


__all__ = [
    "set_validate",
    "WfiMode",
    "NODE_CLASSES",
]


validate = True
strict_validation = True


def set_validate(value):
    global validate
    validate = bool(value)


validator_callbacks = HashableDict(asdfschema.YAML_VALIDATORS)
validator_callbacks.update({'type': _check_type})


def _value_change(path, value, schema, pass_invalid_values,
                  strict_validation, ctx):
    """
    Validate a change in value against a schema.
    Trap error and return a flag.
    """
    try:
        _check_value(value, schema, ctx)
        update = True

    except jsonschema.ValidationError as error:
        update = False
        errmsg = _error_message(path, error)
        if pass_invalid_values:
            update = True
        if strict_validation:
            raise jsonschema.ValidationError(errmsg)
        else:
            warnings.warn(errmsg, ValidationWarning)
    return update


def _check_value(value, schema, validator_context):
    """
    Perform the actual validation.
    """

    validator_resolver = validator_context.resolver

    temp_schema = {
        '$schema':
        'http://stsci.edu/schemas/asdf-schema/0.1.0/asdf-schema'}
    temp_schema.update(schema)
    validator = asdfschema.get_validator(temp_schema,
                                         validator_context,
                                         validator_callbacks,
                                         validator_resolver)

    #value = yamlutil.custom_tree_to_tagged_tree(value, validator_context)
    validator.validate(value, _schema=temp_schema)
    validator_context.close()


def _validate(attr, instance, schema, ctx):
    tagged_tree = yamlutil.custom_tree_to_tagged_tree(instance, ctx)
    return _value_change(attr, tagged_tree, schema, False, strict_validation, ctx)


def _get_schema_for_property(schema, attr):
    subschema = schema.get('properties', {}).get(attr, None)
    if subschema is not None:
        return subschema
    for combiner in ['allOf', 'anyOf']:
        for subschema in schema.get(combiner, []):
            subsubschema = _get_schema_for_property(subschema, attr)
            if subsubschema != {}:
                return subsubschema
    return {}


class DNode(UserDict):

    _tag = None
    _ctx = None

    def __init__(self, node=None, parent=None, name=None):

        if node is None:
            self.__dict__['_data'] = {}
        elif isinstance(node, dict):
            self.__dict__['_data'] = node
        else:
            raise ValueError("Initializer only accepts dicts")
        self._x_schema = None
        self._schema_uri = None
        self._parent = parent
        self._name = name
        # else:
        #     self.data = node.data

    # def __iter__(self):
    #     return NodeIterator(self)

    @property
    def ctx(self):
        if self._ctx is None:
            DNode._ctx = asdf.AsdfFile()
        return self._ctx

    def __getattr__(self, key):
        """
        Permit accessing dict keys as attributes, assuming they are legal Python
        variable names.
        """
        if key.startswith('_'):
            raise AttributeError('No attribute {0}'.format(key))
        if key in self._data:
            value = self._data[key]
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
        if key[0] != '_':
            if key in self._data:
                if validate:
                    self._schema()
                    schema = self._x_schema.get('properties')
                    if schema is None:
                        # See if the key is in one of the combiners.
                        # This implementation is not completely general
                        # A more robust one would potentially handle nested
                        # references, though that is probably unlikely
                        # in practical cases.
                        for combiner in ['allOf', 'anyOf']:
                            for subschema in self._x_schema.get(combiner, []):
                                subsubschema = _get_schema_for_property(
                                    subschema, key)
                                if subsubschema != {}:
                                    schema = subsubschema
                                    break
                    else:
                        schema = schema.get(key, None)
                    if _validate(key, value, schema, self.ctx):
                        self._data[key] = value
                self.__dict__['_data'][key] = value
            else:
                raise AttributeError(
                    f"No such attribute ({key}) found in node")
        else:
            self.__dict__[key] = value

    def to_flat_dict(self, include_arrays=True):
        """
        Returns a dictionary of all of the schema items as a flat dictionary.

        Each dictionary key is a dot-separated name.  For example, the
        schema element `meta.observation.date` will end up in the
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
            return dict((key, convert_val(val)) for (key, val) in self.items())
        else:
            return dict((key, convert_val(val)) for (key, val) in self.items()
                        if not isinstance(val, (np.ndarray, ndarray.NDArrayType)))

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
    # def __getindex__(self, key):
    #     return self.data[key]

    # def __setindex__(self, key, value):
    #     self.data[key] = value

class LNode(UserList):

    _tag = None

    def __init__(self, node=None):
        if node is None:
            self.data = []
        elif isinstance(node, list):
            self.data = node
        else:
            raise ValueError("Initalizer only accepts lists")
        # else:
        #     self.data = node.data

    def __getitem__(self, index):
        value = self.data[index]
        if isinstance(value, dict):
            return DNode(value)
        elif isinstance(value, list):
            return LNode(value)
        else:
            return value


_OBJECT_NODE_CLASSES_BY_TAG = {}


class TaggedObjectNodeMeta(ABCMeta):
    """
    Metaclass for TaggedObjectNode that maintains a registry
    of subclasses.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.__name__ != "TaggedObjectNode":
            if self._tag in _OBJECT_NODE_CLASSES_BY_TAG:
                raise RuntimeError(
                    f"TaggedObjectNode class for tag '{self._tag}' has been defined twice")
            _OBJECT_NODE_CLASSES_BY_TAG[self._tag] = self


class TaggedObjectNode(DNode, metaclass=TaggedObjectNodeMeta):
    """
    Expects subclass to define a class instance of _tag
    """

    @property
    def tag(self):
        return self._tag

    def _schema(self):
        if self._x_schema is None:
            self._x_schema = self.get_schema()
        return self._x_schema

    def get_schema(self):
        """Retrieve the schema associated with this tag"""
        extension_manager = self.ctx.extension_manager
        tag_def = extension_manager.get_tag_definition(self.tag)
        schema_uri = tag_def.schema_uri
        schema = asdfschema.load_schema(schema_uri, resolve_references=True)
        return schema


class TaggedListNode(LNode):

    @property
    def tag(self):
        return self._tag


class WfiMode(TaggedObjectNode):
    _tag = "asdf://stsci.edu/datamodels/roman/tags/wfi_mode-1.0.0"

    _GRATING_OPTICAL_ELEMENTS = {"GRISM", "PRISM"}

    @property
    def filter(self):
        if self.optical_element in self._GRATING_OPTICAL_ELEMENTS:
            return None
        else:
            return self.optical_element

    @property
    def grating(self):
        if self.optical_element in self._GRATING_OPTICAL_ELEMENTS:
            return self.optical_element
        else:
            return None


_DATAMODELS_MANIFEST_PATH = importlib_resources.files(
    rad.resources) / "manifests" / "datamodels-1.0.yaml"
_DATAMODELS_MANIFEST = yaml.safe_load(_DATAMODELS_MANIFEST_PATH.read_bytes())


def _class_name_from_tag_uri(tag_uri):
    tag_name = tag_uri.split("/")[-1].split("-")[0]
    class_name = "".join([p.capitalize() for p in tag_name.split("_")])
    if tag_uri.startswith("asdf://stsci.edu/datamodels/roman/tags/reference_files/"):
        class_name += "Ref"
    return class_name


for tag in _DATAMODELS_MANIFEST["tags"]:
    docstring = ""
    if "description" in tag:
        docstring = tag["description"] + "\n\n"
    docstring = docstring + f"Class generated from tag '{tag['tag_uri']}'"

    if tag["tag_uri"] in _OBJECT_NODE_CLASSES_BY_TAG:
        _OBJECT_NODE_CLASSES_BY_TAG[tag["tag_uri"]].__doc__ = docstring
    else:
        class_name = _class_name_from_tag_uri(tag["tag_uri"])

        cls = type(
            class_name,
            (TaggedObjectNode,),
            {"_tag": tag["tag_uri"],
                "__module__": "roman_datamodels.stnode", "__doc__": docstring},
        )
        globals()[class_name] = cls
        __all__.append(class_name)


class TaggedObjectNodeConverter(Converter):
    """
    Converter for all subclasses of TaggedObjectNode.
    """
    @property
    def tags(self):
        return list(_OBJECT_NODE_CLASSES_BY_TAG.keys())

    @property
    def types(self):
        return list(_OBJECT_NODE_CLASSES_BY_TAG.values())

    def select_tag(self, obj, tags, ctx):
        return obj.tag

    def to_yaml_tree(self, obj, tag, ctx):
        return obj._data

    def from_yaml_tree(self, node, tag, ctx):
        return _OBJECT_NODE_CLASSES_BY_TAG[tag](node)


# List of node classes made available by this library.  This is part
# of the public API.
NODE_CLASSES = list(_OBJECT_NODE_CLASSES_BY_TAG.values())
