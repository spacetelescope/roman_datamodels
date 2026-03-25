"""
The ASDF Converters to handle the serialization/deseialization of the STNode classes to ASDF.
"""

from __future__ import annotations

from typing import ClassVar, Generic, TypeVar

from asdf.extension import Converter, ManifestExtension
from astropy.time import Time

from ._registry import (
    DATAMODEL_CONVERTERS,
    DATAMODEL_MANIFESTS,
    DATAMODEL_PATTERNS,
    LIST_NODE_CLASSES_BY_PATTERN,
    NODE_CLASSES_BY_TAG,
    OBJECT_NODE_CLASSES_BY_PATTERN,
    SCALAR_NODE_CLASSES_BY_PATTERN,
    STATIC_CONVERTERS,
    STATIC_MANIFESTS,
    STATIC_PATTERNS,
)
from ._tagged import TaggedListNode, TaggedObjectNode, TaggedScalarNode, tagged_type

_T = TypeVar("_T")

__all__ = [
    "NODE_EXTENSIONS",
    "TaggedListNodeConverter",
    "TaggedObjectNodeConverter",
    "TaggedScalarNodeConverter",
]


class _RomanConverter(Converter, Generic[_T]):
    """
    Base class for the roman_datamodels converters.
    """

    lazy = True

    _node_registry: ClassVar[dict[str, _T]]

    def __init_subclass__(cls, **kwargs) -> None:
        """
        Automatically create the converter objects.
        """
        super().__init_subclass__(**kwargs)

        if not cls.__name__.startswith("_"):
            if (static_name := f"static_{cls.__name__}") in STATIC_CONVERTERS:
                raise ValueError(f"Duplicate converter for {static_name}")

            STATIC_CONVERTERS[static_name] = cls(STATIC_PATTERNS)

            if (datamodel_name := f"datamodel_{cls.__name__}") in DATAMODEL_CONVERTERS:
                raise ValueError(f"Duplicate converter for {datamodel_name}")

            DATAMODEL_CONVERTERS[datamodel_name] = cls(DATAMODEL_PATTERNS)

    def __init__(self, patterns: dict[str, tagged_type]):
        super().__init__()

        self._patterns = patterns

    @property
    def tags(self) -> tuple[str, ...]:
        return tuple(pattern for pattern in self._node_registry if pattern in self._patterns)

    @property
    def types(self) -> tuple[_T, ...]:
        return tuple(type_ for pattern, type_ in self._node_registry.items() if pattern in self._patterns)

    def select_tag(self, obj, tags, ctx):
        return obj.tag

    def from_yaml_tree(self, node, tag, ctx):
        obj = NODE_CLASSES_BY_TAG[tag](node)
        obj._read_tag = tag
        return obj


class TaggedObjectNodeConverter(_RomanConverter[type[TaggedObjectNode]]):
    """
    Converter for all subclasses of TaggedObjectNode.
    """

    _node_registry = OBJECT_NODE_CLASSES_BY_PATTERN

    def to_yaml_tree(self, obj, tag, ctx):
        return dict(obj._data)


class TaggedListNodeConverter(_RomanConverter[type[TaggedListNode]]):
    """
    Converter for all subclasses of TaggedListNode.
    """

    _node_registry = LIST_NODE_CLASSES_BY_PATTERN

    def to_yaml_tree(self, obj, tag, ctx):
        return list(obj)


class TaggedScalarNodeConverter(_RomanConverter[type[TaggedScalarNode]]):
    """
    Converter for all subclasses of TaggedScalarNode.
    """

    _node_registry = SCALAR_NODE_CLASSES_BY_PATTERN

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
        return super().from_yaml_tree(node, tag, ctx)


# Create the ASDF extension for the STNode classes.
NODE_EXTENSIONS = {
    **{
        manifest["id"]: ManifestExtension.from_uri(manifest["id"], converters=STATIC_CONVERTERS.values())
        for manifest in STATIC_MANIFESTS
    },
    **{
        manifest["id"]: ManifestExtension.from_uri(manifest["id"], converters=DATAMODEL_CONVERTERS.values())
        for manifest in DATAMODEL_MANIFESTS
    },
}
