"""
Proof of concept of using tags with the data model framework
"""

import importlib.resources

import rad.resources
import yaml
from asdf.extension import Converter
from astropy.time import Time

from ._fixed import FileDate
from ._registry import LIST_NODE_CLASSES_BY_TAG, OBJECT_NODE_CLASSES_BY_TAG, SCALAR_NODE_CLASSES_BY_TAG
from ._tagged import TaggedObjectNode, TaggedScalarNode

__all__ = [
    "NODE_CLASSES",
    "TaggedListNodeConverter",
    "TaggedObjectNodeConverter",
    "TaggedScalarNodeConverter",
]


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
