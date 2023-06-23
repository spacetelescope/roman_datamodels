"""
The ASDF Converters to handle the serialization/deseialization of the STNode classes to ASDF.
"""
from asdf.extension import Converter
from astropy.time import Time

from ._registry import LIST_NODE_CLASSES_BY_TAG, OBJECT_NODE_CLASSES_BY_TAG, SCALAR_NODE_CLASSES_BY_TAG

__all__ = [
    "TaggedObjectNodeConverter",
    "TaggedListNodeConverter",
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
        from ._stnode import FileDate

        node = obj.__class__.__bases__[0](obj)

        if tag == FileDate._tag:
            converter = ctx.extension_manager.get_converter_for_type(type(node))
            node = converter.to_yaml_tree(node, tag, ctx)

        return node

    def from_yaml_tree(self, node, tag, ctx):
        from ._stnode import FileDate

        if tag == FileDate._tag:
            converter = ctx.extension_manager.get_converter_for_type(Time)
            node = converter.from_yaml_tree(node, tag, ctx)

        return SCALAR_NODE_CLASSES_BY_TAG[tag](node)
