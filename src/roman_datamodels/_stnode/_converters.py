"""
The ASDF Converters to handle the serialization/deseialization of the STNode classes to ASDF.
"""

from __future__ import annotations

from functools import cached_property
from typing import ClassVar

from asdf.extension import Converter
from astropy.time import Time

from ._tagged import SerializationNode, TaggedListNode, TaggedObjectNode, TaggedScalarNode, tagged_type

__all__ = ("SerializationNodeConverter", "TaggedNodeConverter")


class _RomanConverter(Converter):
    """
    Base class for the roman_datamodels converters.
    """

    lazy = True


class SerializationNodeConverter(_RomanConverter):
    """
    Converter that tags are deferred to so that the correct
    extension can be applied
    """

    def __init__(self, node_cls: type[SerializationNode]):
        self._node_cls = node_cls

    def select_tag(self, obj: SerializationNode, tags, ctx) -> str:
        return obj.tag

    @property
    def tags(self) -> tuple[str, ...]:
        return tuple(self._node_cls.tag_uris)

    @cached_property
    def types(self) -> tuple[type[SerializationNode]]:
        return (self._node_cls,)

    def to_yaml_tree(self, obj: SerializationNode, tag, ctx):
        return obj.data

    def from_yaml_tree(self, node, tag, ctx) -> TaggedObjectNode | TaggedListNode | TaggedScalarNode:
        if "file_date" in tag:
            converter = ctx.extension_manager.get_converter_for_type(Time)
            node = converter.from_yaml_tree(node, tag, ctx)

        # TODO: Add method for setting read_tag with some checks
        obj = SerializationNode.tag_type(tag)(node)
        obj._read_tag = tag
        return obj


class TaggedNodeConverter(_RomanConverter):
    """The converter which handles all Tagged Nodes"""

    _instance: ClassVar[TaggedNodeConverter | None] = None

    # Make a singleton
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)

        return cls._instance

    def select_tag(self, obj, tags, ctx):
        return None

    @property
    def tags(self) -> tuple:
        return ()

    @property
    def types(self) -> tuple[tagged_type, ...]:
        return (*TaggedObjectNode.__subclasses__(), *TaggedListNode.__subclasses__(), *TaggedScalarNode.__subclasses__())

    def to_yaml_tree(self, obj: tagged_type, tag: str, ctx) -> SerializationNode:
        # MyPy is doing something weird and missing the ctx argument
        return obj._serialize(ctx)  # type: ignore[call-arg]

    def from_yaml_tree(self, node, tag, ctx):
        raise NotImplementedError("Converter deserialization deferred")
