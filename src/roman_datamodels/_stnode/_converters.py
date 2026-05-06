"""
The ASDF Converters to handle the serialization/deseialization of the STNode classes to ASDF.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar

from asdf.extension import Converter, SerializationContext
from astropy.time import Time

from ._registry import MANIFEST_TAG_REGISTRY, NODE_CLASSES_BY_TAG, SERIALIZATION_BY_MANIFEST

if TYPE_CHECKING:
    from ._tagged import SerializationNode, TaggedListNode, TaggedObjectNode, TaggedScalarNode, _TaggedNodeMixin

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


class TaggedNodeConverter(_RomanConverter):
    """
    The converter which handles all Tagged Nodes
        This converter will defer final ASDF serialization to the ManifestNodeConverter
        so that the extensions recorded in the ASDF file's history section are property
        attributed to the correct manifest.
    """

    _instance: ClassVar[TaggedNodeConverter | None] = None

    # Make a singleton
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)

        return cls._instance

    def select_tag(self, obj: _TaggedNodeMixin, tags: tuple[str, ...], ctx: SerializationContext) -> None:
        return None

    @property
    def tags(self) -> tuple:
        return ()

    @property
    def types(self) -> tuple[type[_TaggedNodeMixin], ...]:
        from ._stnode import NODE_CLASSES

        return tuple(NODE_CLASSES)

    def to_yaml_tree(self, obj: _TaggedNodeMixin, tag: str, ctx: SerializationContext) -> SerializationNode:
        return obj.to_asdf_tree(ctx)

    def from_yaml_tree(self, node: dict[str, Any], tag: str, ctx: SerializationContext):
        raise NotImplementedError("Converter deserialization deferred")
