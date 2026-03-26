"""
The ASDF Converters to handle the serialization/deseialization of the STNode classes to ASDF.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from asdf.extension import Converter
from astropy.time import Time

from ._registry import (
    LIST_NODE_CLASSES_BY_PATTERN,
    NODE_CLASSES_BY_TAG,
    NODE_CONVERTERS,
    OBJECT_NODE_CLASSES_BY_PATTERN,
    SCALAR_NODE_CLASSES_BY_PATTERN,
    SERIALIZATION_BY_TAG,
)

if TYPE_CHECKING:
    from ._tagged import SerializationTaggedNode, TaggedListNode, TaggedObjectNode, TaggedScalarNode

__all__ = [
    "TaggedListNodeConverter",
    "TaggedObjectNodeConverter",
    "TaggedScalarNodeConverter",
]


class _RomanConverter(Converter):
    """
    Base class for the roman_datamodels converters.
    """

    lazy = True


class SerializationTaggedNodeConverter(_RomanConverter):
    """
    Converter that tags are deferred to so that the correct
    extension can be applied
    """

    def __init__(self, manifest_uri: str, tags: list[str]):
        self._tags = tags
        self._manifest_uri = manifest_uri

    def select_tag(self, obj: SerializationTaggedNode, tags, ctx) -> str:
        return obj.tag

    @property
    def tags(self) -> tuple[str, ...]:
        return tuple(self._tags)

    @property
    def types(self) -> tuple[type[SerializationTaggedNode], ...]:
        return tuple(type_ for tag, type_ in SERIALIZATION_BY_TAG.items() if tag in self._tags)

    def to_yaml_tree(self, obj: SerializationTaggedNode, tag, ctx):
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
    def tags(self) -> tuple:
        return ()

    def to_yaml_tree(self, obj, tag, ctx):
        return SERIALIZATION_BY_TAG[tag](obj)

    def from_yaml_tree(self, node, tag, ctx):
        raise NotImplementedError("Converter deserialization deferred")


class TaggedObjectNodeConverter(_TaggedNodeConverter):
    """
    Converter for all subclasses of TaggedObjectNode.
    """

    @property
    def types(self):
        return tuple(OBJECT_NODE_CLASSES_BY_PATTERN.values())

    def to_yaml_tree(self, obj: TaggedObjectNode, tag, ctx):
        return super().to_yaml_tree(dict(obj._data), obj.tag, ctx)


class TaggedListNodeConverter(_TaggedNodeConverter):
    """
    Converter for all subclasses of TaggedListNode.
    """

    @property
    def types(self):
        return tuple(LIST_NODE_CLASSES_BY_PATTERN.values())

    def to_yaml_tree(self, obj, tag, ctx):
        return super().to_yaml_tree(list(obj), obj.tag, ctx)


class TaggedScalarNodeConverter(_TaggedNodeConverter):
    """
    Converter for all subclasses of TaggedScalarNode.
    """

    @property
    def types(self):
        return list(SCALAR_NODE_CLASSES_BY_PATTERN.values())

    def to_yaml_tree(self, obj, tag, ctx):
        node = type(obj).__bases__[0](obj)

        if "file_date" in obj.tag:
            converter = ctx.extension_manager.get_converter_for_type(type(node))
            node = converter.to_yaml_tree(node, tag, ctx)

        return super().to_yaml_tree(node, obj.tag, ctx)
