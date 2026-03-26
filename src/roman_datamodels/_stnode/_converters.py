"""
The ASDF Converters to handle the serialization/deseialization of the STNode classes to ASDF.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from asdf.extension import Converter
from astropy.time import Time

from ._registry import REGISTRY

if TYPE_CHECKING:
    from ._tagged import ManifestNode, TaggedListNode, TaggedObjectNode, TaggedScalarNode

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


class ManifestNodeConverter(_RomanConverter):
    """
    Converter for the ManifestNode objects so that tags can be deferred to
        this converter so that the correct extension will be recorded.
    """

    def __init__(self, manifest_uri: str):
        self._manifest_uri = manifest_uri

    def select_tag(self, obj: ManifestNode, tags, ctx) -> str:
        return obj.tag

    @property
    def tags(self) -> tuple[str, ...]:
        return tuple(REGISTRY.manifest.tag[self._manifest_uri])

    @property
    def types(self) -> tuple[type[ManifestNode], ...]:
        return (REGISTRY.manifest.node[self._manifest_uri],)

    def to_yaml_tree(self, obj: ManifestNode, tag, ctx):
        return obj.data

    def from_yaml_tree(self, node, tag, ctx) -> TaggedObjectNode | TaggedListNode | TaggedScalarNode:
        if "file_date" in tag:
            converter = ctx.extension_manager.get_converter_for_type(Time)
            node = converter.from_yaml_tree(node, tag, ctx)

        # TODO: Add method for setting read_tag with some checks
        obj = REGISTRY.tag.node[tag](node)
        obj._read_tag = tag
        return obj


class _TaggedNodeConverter(_RomanConverter):
    """
    Base converter for all of the node types.
    """

    def __init_subclass__(cls, **kwargs) -> None:
        """
        Automatically create the converter objects.
        """
        super().__init_subclass__(**kwargs)

        if not cls.__name__.startswith("_"):
            if cls.__name__ in REGISTRY.converters:
                raise ValueError(f"Duplicate converter for {cls.__name__}")

            REGISTRY.converters[cls.__name__] = cls()

    # This is what triggers the converter deferral
    def select_tag(self, obj, tags, ctx):
        return None

    #  If select tag is None, then we cannot have tags
    @property
    def tags(self) -> tuple:
        return ()

    def to_yaml_tree(self, obj, tag, ctx):
        return REGISTRY[tag](obj, tag)

    def from_yaml_tree(self, node, tag, ctx):
        raise NotImplementedError("Converter deserialization deferred")


class TaggedObjectNodeConverter(_TaggedNodeConverter):
    """
    Converter for all subclasses of TaggedObjectNode.
        -> defers serialization of node to the ManifestNodeConverter
    """

    @property
    def types(self):
        return tuple(REGISTRY.pattern.object.values())

    def to_yaml_tree(self, obj: TaggedObjectNode, tag, ctx):
        return super().to_yaml_tree(dict(obj._data), obj.tag, ctx)


class TaggedListNodeConverter(_TaggedNodeConverter):
    """
    Converter for all subclasses of TaggedListNode.
        -> defers serialization of node to the ManifestNodeConverter
    """

    @property
    def types(self):
        return tuple(REGISTRY.pattern.list.values())

    def to_yaml_tree(self, obj, tag, ctx):
        return super().to_yaml_tree(list(obj), obj.tag, ctx)


class TaggedScalarNodeConverter(_TaggedNodeConverter):
    """
    Converter for all subclasses of TaggedScalarNode.
        -> defers serialization of node to the ManifestNodeConverter
    """

    @property
    def types(self):
        return tuple(REGISTRY.pattern.scalar.values())

    def to_yaml_tree(self, obj, tag, ctx):
        node = type(obj).__bases__[0](obj)

        if "file_date" in obj.tag:
            converter = ctx.extension_manager.get_converter_for_type(type(node))
            node = converter.to_yaml_tree(node, tag, ctx)

        return super().to_yaml_tree(node, obj.tag, ctx)
