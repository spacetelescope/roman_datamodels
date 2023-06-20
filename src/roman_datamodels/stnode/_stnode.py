"""
Proof of concept of using tags with the data model framework
"""

import importlib.resources
from abc import ABCMeta

import asdf
import asdf.schema as asdfschema
import rad.resources
import yaml
from asdf.extension import Converter
from astropy.time import Time

from ._node import DNode, LNode
from ._registry import (
    LIST_NODE_CLASSES_BY_TAG,
    OBJECT_NODE_CLASSES_BY_TAG,
    SCALAR_NODE_CLASSES_BY_KEY,
    SCALAR_NODE_CLASSES_BY_TAG,
)

__all__ = [
    "WfiMode",
    "NODE_CLASSES",
    "CalLogs",
    "FileDate",
    "TaggedObjectNode",
    "TaggedListNode",
    "TaggedScalarNode",
    "TaggedListNodeConverter",
    "TaggedObjectNodeConverter",
    "TaggedScalarNodeConverter",
]


class TaggedObjectNodeMeta(ABCMeta):
    """
    Metaclass for TaggedObjectNode that maintains a registry
    of subclasses.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.__name__ != "TaggedObjectNode":
            if self._tag in OBJECT_NODE_CLASSES_BY_TAG:
                raise RuntimeError(f"TaggedObjectNode class for tag '{self._tag}' has been defined twice")
            OBJECT_NODE_CLASSES_BY_TAG[self._tag] = self


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
        schema_uri = tag_def.schema_uris[0]
        schema = asdfschema.load_schema(schema_uri, resolve_references=True)
        return schema


class TaggedListNodeMeta(ABCMeta):
    """
    Metaclass for TaggedListNode that maintains a registry
    of subclasses.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.__name__ != "TaggedListNode":
            if self._tag in LIST_NODE_CLASSES_BY_TAG:
                raise RuntimeError(f"TaggedListNode class for tag '{self._tag}' has been defined twice")
            LIST_NODE_CLASSES_BY_TAG[self._tag] = self


class TaggedListNode(LNode, metaclass=TaggedListNodeMeta):
    @property
    def tag(self):
        return self._tag


def _scalar_tag_to_key(tag):
    return tag.split("/")[-1].split("-")[0]


class TaggedScalarNodeMeta(ABCMeta):
    """
    Metaclass for TaggedScalarNode that maintains a registry
    of subclasses.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.__name__ != "TaggedScalarNode":
            if self._tag in SCALAR_NODE_CLASSES_BY_TAG:
                raise RuntimeError(f"TaggedScalarNode class for tag '{self._tag}' has been defined twice")
            SCALAR_NODE_CLASSES_BY_TAG[self._tag] = self
            SCALAR_NODE_CLASSES_BY_KEY[_scalar_tag_to_key(self._tag)] = self


class TaggedScalarNode(metaclass=TaggedScalarNodeMeta):
    _tag = None
    _ctx = None

    @property
    def ctx(self):
        if self._ctx is None:
            TaggedScalarNode._ctx = asdf.AsdfFile()
        return self._ctx

    def __asdf_traverse__(self):
        return self

    @property
    def tag(self):
        return self._tag

    @property
    def key(self):
        return _scalar_tag_to_key(self._tag)

    def get_schema(self):
        extension_manager = self.ctx.extension_manager
        tag_def = extension_manager.get_tag_definition(self.tag)
        schema_uri = tag_def.schema_uris[0]
        schema = asdf.schema.load_schema(schema_uri, resolve_references=True)
        return schema

    def copy(self):
        import copy

        return copy.copy(self)


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


class CalLogs(TaggedListNode):
    _tag = "asdf://stsci.edu/datamodels/roman/tags/cal_logs-1.0.0"


class FileDate(Time, TaggedScalarNode):
    _tag = "asdf://stsci.edu/datamodels/roman/tags/file_date-1.0.0"


class TaggedObjectNodeConverter(Converter):
    """
    Converter for all subclasses of TaggedObjectNode.
    """

    @property
    def tags(self):
        return list(OBJECT_NODE_CLASSES_BY_TAG.keys())

    @property
    def types(self):
        return list(OBJECT_NODE_CLASSES_BY_TAG.values())

    def select_tag(self, obj, tags, ctx):
        return obj.tag

    def to_yaml_tree(self, obj, tag, ctx):
        return obj._data

    def from_yaml_tree(self, node, tag, ctx):
        return OBJECT_NODE_CLASSES_BY_TAG[tag](node)


class TaggedListNodeConverter(Converter):
    """
    Converter for all subclasses of TaggedListNode.
    """

    @property
    def tags(self):
        return list(LIST_NODE_CLASSES_BY_TAG.keys())

    @property
    def types(self):
        return list(LIST_NODE_CLASSES_BY_TAG.values())

    def select_tag(self, obj, tags, ctx):
        return obj.tag

    def to_yaml_tree(self, obj, tag, ctx):
        return list(obj)

    def from_yaml_tree(self, node, tag, ctx):
        return LIST_NODE_CLASSES_BY_TAG[tag](node)


class TaggedScalarNodeConverter(Converter):
    """
    Converter for all subclasses of TaggedScalarNode.
    """

    @property
    def tags(self):
        return list(SCALAR_NODE_CLASSES_BY_TAG.keys())

    @property
    def types(self):
        return list(SCALAR_NODE_CLASSES_BY_TAG.values())

    def select_tag(self, obj, tags, ctx):
        return obj.tag

    def to_yaml_tree(self, obj, tag, ctx):
        node = obj.__class__.__bases__[0](obj)

        if tag == FileDate._tag:
            converter = ctx.extension_manager.get_converter_for_type(type(node))
            node = converter.to_yaml_tree(node, tag, ctx)

        return node

    def from_yaml_tree(self, node, tag, ctx):
        if tag == FileDate._tag:
            converter = ctx.extension_manager.get_converter_for_type(Time)
            node = converter.from_yaml_tree(node, tag, ctx)

        return SCALAR_NODE_CLASSES_BY_TAG[tag](node)


_DATAMODELS_MANIFEST_PATH = importlib.resources.files(rad.resources) / "manifests" / "datamodels-1.0.yaml"
_DATAMODELS_MANIFEST = yaml.safe_load(_DATAMODELS_MANIFEST_PATH.read_bytes())


def _class_name_from_tag_uri(tag_uri):
    tag_name = tag_uri.split("/")[-1].split("-")[0]
    class_name = "".join([p.capitalize() for p in tag_name.split("_")])
    if tag_uri.startswith("asdf://stsci.edu/datamodels/roman/tags/reference_files/"):
        class_name += "Ref"
    return class_name


def _class_from_tag(tag, docstring):
    class_name = _class_name_from_tag_uri(tag["tag_uri"])

    schema_uri = tag["schema_uri"]
    if "tagged_scalar" in schema_uri:
        cls = type(
            class_name,
            (str, TaggedScalarNode),
            {"_tag": tag["tag_uri"], "__module__": "roman_datamodels.stnode", "__doc__": docstring},
        )
    else:
        cls = type(
            class_name,
            (TaggedObjectNode,),
            {"_tag": tag["tag_uri"], "__module__": "roman_datamodels.stnode", "__doc__": docstring},
        )

    globals()[class_name] = cls
    __all__.append(class_name)


for tag in _DATAMODELS_MANIFEST["tags"]:
    docstring = ""
    if "description" in tag:
        docstring = tag["description"] + "\n\n"
    docstring = docstring + f"Class generated from tag '{tag['tag_uri']}'"

    if tag["tag_uri"] in OBJECT_NODE_CLASSES_BY_TAG:
        OBJECT_NODE_CLASSES_BY_TAG[tag["tag_uri"]].__doc__ = docstring
    elif tag["tag_uri"] in LIST_NODE_CLASSES_BY_TAG:
        LIST_NODE_CLASSES_BY_TAG[tag["tag_uri"]].__doc__ = docstring
    elif tag["tag_uri"] in SCALAR_NODE_CLASSES_BY_TAG:
        SCALAR_NODE_CLASSES_BY_TAG[tag["tag_uri"]].__doc__ = docstring
    else:
        _class_from_tag(tag, docstring)


# List of node classes made available by this library.  This is part
# of the public API.
NODE_CLASSES = (
    list(OBJECT_NODE_CLASSES_BY_TAG.values())
    + list(LIST_NODE_CLASSES_BY_TAG.values())
    + list(SCALAR_NODE_CLASSES_BY_TAG.values())
)
