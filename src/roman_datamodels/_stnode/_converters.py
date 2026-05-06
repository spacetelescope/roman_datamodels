"""
The ASDF Converters to handle the serialization/deseialization of the STNode classes to ASDF.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar

from asdf.extension import Converter, SerializationContext

if TYPE_CHECKING:
    from ._manifest import ManifestNode
    from ._tagged import TaggedListNode, TaggedObjectNode, TaggedScalarNode, _TaggedNodeMixin

__all__ = ("ManifestNodeConverter", "TaggedNodeConverter")


class _RomanConverter(Converter):
    """
    Base class for the roman_datamodels converters.
    """

    lazy = True


class ManifestNodeConverter(_RomanConverter):
    """
    Converter that tags are deferred to so that the correct
        extension can recorded in the ASDF file's history section.
    """

    def __init__(self, node_cls: type[ManifestNode]):
        self._node_cls = node_cls

    def select_tag(self, obj: ManifestNode, tags: tuple[str, ...], ctx: SerializationContext) -> str:
        return obj.tag

    @property
    def tags(self) -> tuple[str, ...]:
        from ._registry import MANIFEST_TAG_REGISTRY

        return tuple(MANIFEST_TAG_REGISTRY[self._node_cls.manifest_uri])

    @property
    def types(self) -> tuple[type[ManifestNode], ...]:
        return (self._node_cls,)

    def to_yaml_tree(self, obj: ManifestNode, tag: str, ctx: SerializationContext) -> Any:
        return obj.data

    def from_yaml_tree(
        self, node: dict[str, Any], tag: str, ctx: SerializationContext
    ) -> TaggedObjectNode | TaggedListNode | TaggedScalarNode:
        from astropy.time import Time

        from ._registry import NODE_CLASSES_BY_TAG

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

    def to_yaml_tree(self, obj: _TaggedNodeMixin, tag: str, ctx: SerializationContext) -> ManifestNode:
        return obj.to_asdf_tree(ctx)

    def from_yaml_tree(self, node: dict[str, Any], tag: str, ctx: SerializationContext):
        raise NotImplementedError("Converter deserialization deferred")
