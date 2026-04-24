"""
The ASDF Converters to handle the serialization/deseialization of the STNode classes to ASDF.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from asdf.extension import Converter
from astropy.time import Time

from ._manifest import TAG_MANIFEST_REGISTRY

if TYPE_CHECKING:
    from ._tagged import SerializationNode

__all__ = [
    "TaggedNodeConverter",
]


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

    def __init__(self, serialization_node: type[SerializationNode], tags: tuple[str, ...]):
        self._serialization_node = serialization_node
        self._tags = tags

    def select_tag(self, obj: SerializationNode, tags, ctx):
        return obj.tag

    @property
    def tags(self) -> tuple[str, ...]:
        return self._tags

    @property
    def types(self) -> tuple[type[SerializationNode], ...]:
        return (self._serialization_node,)

    def to_yaml_tree(self, obj: SerializationNode, tag, ctx):
        return obj.serialize_data(ctx)

    def from_yaml_tree(self, node, tag, ctx):
        if "file_date" in tag:
            converter = ctx.extension_manager.get_converter_for_type(Time)
            node = converter.from_yaml_tree(node, tag, ctx)

        # this local import is only to appease mypy, it works at the top of this file
        from ._stnode import NODE_CLASSES_BY_TAG

        # TODO: Add method for setting read_tag with some checks
        obj = NODE_CLASSES_BY_TAG[tag](node)
        obj._read_tag = tag
        return obj


class TaggedNodeConverter(_RomanConverter):
    def __init__(self, serialization_node_by_manifest):
        self._serialization_node_by_manifest = serialization_node_by_manifest

    def select_tag(self, obj, tags, ctx):
        return None

    @property
    def tags(self) -> tuple:
        return ()

    @property
    def types(self):
        # this local import is only to appease mypy, it works at the top of this file
        from ._stnode import NODE_CLASSES

        return NODE_CLASSES

    def to_yaml_tree(self, obj, tag, ctx):
        return self._serialization_node_by_manifest[TAG_MANIFEST_REGISTRY[obj.tag]](obj)

    def from_yaml_tree(self, node, tag, ctx):
        raise NotImplementedError("Converter deserialization deferred")
