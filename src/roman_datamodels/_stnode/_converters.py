"""
The ASDF Converters to handle the serialization/deseialization of the STNode classes to ASDF.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from asdf.extension import Converter
from astropy.time import Time

from ._registry import (
    LIST_NODE_CLASSES_BY_PATTERN,
    MANIFEST_TAG_REGISTRY,
    NODE_CLASSES_BY_TAG,
    NODE_CONVERTERS,
    OBJECT_NODE_CLASSES_BY_PATTERN,
    SCALAR_NODE_CLASSES_BY_PATTERN,
    SERIALIZATION_BY_MANIFEST,
    TAG_MANIFEST_REGISTRY,
)

if TYPE_CHECKING:
    from ._tagged import SerializationNode, TaggedListNode, TaggedObjectNode, TaggedScalarNode

__all__ = [
    "SerializationNodeConverter",
    "TaggedListNodeConverter",
    "TaggedObjectNodeConverter",
    "TaggedScalarNodeConverter",
]


class _RomanConverter(Converter):
    """
    Base class for the roman_datamodels converters.
    """

    lazy = True
    """
    The converter is lazy, meaning by default it will lazy load from the file
    """


class SerializationNodeConverter(_RomanConverter):
    """
    Converter that tags are deferred to for serialization

    This ensures that the serialization history is handled in a way that
    allows for the correct extension to be recorded.
    """

    def __init__(self, manifest_uri: str):
        self._manifest_uri = manifest_uri

    def select_tag(self, obj: SerializationNode, tags, ctx) -> str:
        return obj.tag

    @property
    def tags(self) -> tuple[str, ...]:
        return tuple(MANIFEST_TAG_REGISTRY[self._manifest_uri])

    @property
    def types(self) -> tuple[type[SerializationNode], ...]:
        return (SERIALIZATION_BY_MANIFEST[self._manifest_uri],)

    def to_yaml_tree(self, obj: SerializationNode, tag, ctx):
        return obj.data

    def from_yaml_tree(self, node, tag, ctx) -> TaggedObjectNode | TaggedListNode | TaggedScalarNode:
        if "file_date" in tag:
            converter = ctx.extension_manager.get_converter_for_type(Time)
            node = converter.from_yaml_tree(node, tag, ctx)

        # TODO: Add method for setting read_tag with some checks
        obj = NODE_CLASSES_BY_TAG[tag](node)
        obj._read_tag = tag
        return obj


class _TaggedNodeConverter(_RomanConverter):
    def __init_subclass__(cls, **kwargs) -> None:
        """
        Automatically create the converter objects.
        """
        super().__init_subclass__(**kwargs)

        if not cls.__name__.startswith("_"):
            if cls.__name__ in NODE_CONVERTERS:
                raise ValueError(f"Duplicate converter for {cls.__name__}")

            NODE_CONVERTERS[cls.__name__] = cls()

    def select_tag(self, obj, tags, ctx):
        return None

    @property
    def tags(self) -> tuple[str, ...]:
        """Return the tags associated with this converter"""
        return ()

    def to_yaml_tree(self, obj, tag, ctx):
        return SERIALIZATION_BY_MANIFEST[TAG_MANIFEST_REGISTRY[tag]](obj, tag)

    def from_yaml_tree(self, node, tag, ctx):
        raise NotImplementedError("Converter deserialization deferred")


class TaggedObjectNodeConverter(_TaggedNodeConverter):
    """
    Converter for all subclasses of TaggedObjectNode
    """

    @property
    def types(self) -> tuple[type[TaggedObjectNode], ...]:
        """Return the types associated with this converter"""
        return tuple(OBJECT_NODE_CLASSES_BY_PATTERN.values())

    def to_yaml_tree(self, obj: TaggedObjectNode, tag, ctx):
        return super().to_yaml_tree(dict(obj._data), obj.tag, ctx)


class TaggedListNodeConverter(_TaggedNodeConverter):
    """
    Converter for all subclasses of TaggedListNode.
    """

    @property
    def types(self) -> tuple[type[TaggedListNode], ...]:
        """Return the types associated with this converter"""
        return tuple(LIST_NODE_CLASSES_BY_PATTERN.values())

    def to_yaml_tree(self, obj, tag, ctx):
        return super().to_yaml_tree(list(obj), obj.tag, ctx)


class TaggedScalarNodeConverter(_TaggedNodeConverter):
    """
    Converter for all subclasses of TaggedScalarNode.
    """

    @property
    def types(self) -> tuple[type[TaggedScalarNode], ...]:
        """Return the types associated with this converter"""
        return tuple(SCALAR_NODE_CLASSES_BY_PATTERN.values())

    def to_yaml_tree(self, obj, tag, ctx):
        node = type(obj).__bases__[0](obj)

        if "file_date" in obj.tag:
            converter = ctx.extension_manager.get_converter_for_type(type(node))
            node = converter.to_yaml_tree(node, tag, ctx)

        return super().to_yaml_tree(node, obj.tag, ctx)
