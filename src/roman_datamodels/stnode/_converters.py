"""
The ASDF Converters to handle the serialization/deseialization of the STNode classes to ASDF.
"""

from asdf.extension import Converter, ManifestExtension
from astropy.time import Time

from ._registry import (
    LIST_NODE_CLASSES_BY_PATTERN,
    NODE_CLASSES_BY_TAG,
    NODE_CONVERTERS,
    OBJECT_NODE_CLASSES_BY_PATTERN,
    SCALAR_NODE_CLASSES_BY_PATTERN,
)

__all__ = [
    "NODE_EXTENSIONS",
    "TaggedListNodeConverter",
    "TaggedObjectNodeConverter",
    "TaggedScalarNodeConverter",
]


class _RomanConverter(Converter):
    """
    Base class for the roman_datamodels converters.
    """

    lazy = True

    def __init_subclass__(cls, **kwargs) -> None:
        """
        Automatically create the converter objects.
        """
        super().__init_subclass__(**kwargs)

        if not cls.__name__.startswith("_"):
            if cls.__name__ in NODE_CONVERTERS:
                raise ValueError(f"Duplicate converter for {cls.__name__}")

            NODE_CONVERTERS[cls.__name__] = cls()


class TaggedObjectNodeConverter(_RomanConverter):
    """
    Converter for all subclasses of TaggedObjectNode.
    """

    @property
    def tags(self):
        return list(OBJECT_NODE_CLASSES_BY_PATTERN.keys())

    @property
    def types(self):
        return list(OBJECT_NODE_CLASSES_BY_PATTERN.values())

    def select_tag(self, obj, tags, ctx):
        return obj.tag

    def to_yaml_tree(self, obj, tag, ctx):
        return dict(obj._data)

    def from_yaml_tree(self, node, tag, ctx):
        return NODE_CLASSES_BY_TAG[tag](node)


class TaggedListNodeConverter(_RomanConverter):
    """
    Converter for all subclasses of TaggedListNode.
    """

    @property
    def tags(self):
        return list(LIST_NODE_CLASSES_BY_PATTERN.keys())

    @property
    def types(self):
        return list(LIST_NODE_CLASSES_BY_PATTERN.values())

    def select_tag(self, obj, tags, ctx):
        return obj.tag

    def to_yaml_tree(self, obj, tag, ctx):
        return list(obj)

    def from_yaml_tree(self, node, tag, ctx):
        return NODE_CLASSES_BY_TAG[tag](node)


class TaggedScalarNodeConverter(_RomanConverter):
    """
    Converter for all subclasses of TaggedScalarNode.
    """

    @property
    def tags(self):
        return list(SCALAR_NODE_CLASSES_BY_PATTERN.keys())

    @property
    def types(self):
        return list(SCALAR_NODE_CLASSES_BY_PATTERN.values())

    def select_tag(self, obj, tags, ctx):
        return obj.tag

    def to_yaml_tree(self, obj, tag, ctx):
        node = obj.__class__.__bases__[0](obj)

        if "file_date" in tag:
            converter = ctx.extension_manager.get_converter_for_type(type(node))
            node = converter.to_yaml_tree(node, tag, ctx)

        return node

    def from_yaml_tree(self, node, tag, ctx):
        if "file_date" in tag:
            converter = ctx.extension_manager.get_converter_for_type(Time)
            node = converter.from_yaml_tree(node, tag, ctx)
        return NODE_CLASSES_BY_TAG[tag](node)


# Create the ASDF extension for the STNode classes.
NODE_EXTENSIONS = [
    ManifestExtension.from_uri(
        "asdf://stsci.edu/datamodels/roman/manifests/datamodels-2.0.0", converters=NODE_CONVERTERS.values()
    ),
    ManifestExtension.from_uri("asdf://stsci.edu/datamodels/roman/manifests/datamodels-1.0", converters=NODE_CONVERTERS.values()),
]
