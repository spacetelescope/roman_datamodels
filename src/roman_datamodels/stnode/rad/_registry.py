"""
Hold all the registry information for the STNode classes.
    These will be dynamically populated at import time by the subclasses
    whenever they generated.
"""

from __future__ import annotations

from enum import Enum
from types import MappingProxyType
from typing import TYPE_CHECKING, TypeVar

from ._base import ArrayFieldMixin, RadNodeMixin
from ._enum import IntNodeMixin, SchemaStrNodeMixin, StrNodeMixin, TaggedStrNodeMixin
from ._implied import ImpliedNodeMixin
from ._node import ExtraFieldsMixin, ListNode, ObjectNode, ScalarNode
from ._schema import SchemaListNode, SchemaMixin, SchemaObjectNode, SchemaScalarNode
from ._tagged import TaggedListNode, TaggedObjectNode, TaggedScalarNode, TagMixin
from ._utils import get_all_fields, get_nodes

if TYPE_CHECKING:
    from roman_datamodels.datamodels import DataModel

__all__ = ["RDM_NODE_REGISTRY"]

_T = TypeVar("_T")


class _RdmNodeRegistry:
    _object_nodes: MappingProxyType[str, type] | None = None
    _list_nodes: MappingProxyType[str, type] | None = None
    _scalar_nodes: MappingProxyType[str, type] | None = None
    _all_nodes: MappingProxyType[str, type] | None = None

    _datamodels: MappingProxyType[str, type] | None = None

    _implied_nodes: MappingProxyType[str, type] | None = None
    _enum_nodes: MappingProxyType[str, type] | None = None

    _schema_registry: MappingProxyType[str, type] | None = None
    _tagged_registry: MappingProxyType[str, type] | None = None

    _node_datamodel_mapping: MappingProxyType[type, type] | None = None

    _reseved_fields: tuple[str, ...] | None = None

    def _import_nodes(self) -> None:
        """
        Make sure all the nodes are imported so they can be found
        """
        # Import the nodes here to avoid importing importing all of them
        # until ASDF actually needs them for deserialization they all need
        # to be imported in order for them to exist and be found
        from roman_datamodels import nodes  # noqa: F401

    @property
    def object_nodes(self) -> MappingProxyType[str, type]:
        """
        Get a mapping of all the object nodes,
            Those are all the nodes that represent something marked as ``type: object``
            in the schema.

        Returns
        -------
        MappingProxyType[str, type]
            class_name -> class
        """
        if self._object_nodes is None:
            self._import_nodes()
            self._object_nodes = MappingProxyType(
                {
                    key: value
                    for key, value in get_nodes(
                        ObjectNode, (ObjectNode, SchemaObjectNode, TaggedObjectNode, ExtraFieldsMixin)
                    ).items()
                    if ExtraFieldsMixin not in value.__bases__
                }
            )
        return self._object_nodes

    @property
    def list_nodes(self) -> MappingProxyType[str, type]:
        """
        Get a mapping of all the list nodes,
            Those are all the nodes that represent something marked as ``type: array``
            in the schema.

        Returns
        -------
        MappingProxyType[str, type]
            class_name -> class
        """
        if self._list_nodes is None:
            self._import_nodes()
            self._list_nodes = MappingProxyType({**get_nodes(ListNode, (ListNode, SchemaListNode, TaggedListNode))})
        return self._list_nodes

    @property
    def scalar_nodes(self) -> MappingProxyType[str, type[ScalarNode]]:
        """
        Get a mapping of all the scalar nodes,
            Those are all the nodes that represent a scalar value in the schema.

        Returns
        -------
        MappingProxyType[str, type]
            class_name -> class
        """
        if self._scalar_nodes is None:
            self._import_nodes()
            self._scalar_nodes = MappingProxyType(
                {
                    **get_nodes(
                        ScalarNode,
                        (
                            ScalarNode,
                            SchemaScalarNode,
                            TaggedScalarNode,
                            IntNodeMixin,
                            SchemaStrNodeMixin,
                            StrNodeMixin,
                            TaggedStrNodeMixin,
                        ),
                    )
                }
            )
        return self._scalar_nodes

    @property
    def all_nodes(self) -> MappingProxyType[str, type[RadNodeMixin]]:
        """
        Get a mapping of all the nodes

        Returns
        -------
        MappingProxyType[str, type]
            class_name -> class
        """
        if self._all_nodes is None:
            self._all_nodes = MappingProxyType(
                {
                    **self.object_nodes,
                    **self.list_nodes,
                    **self.scalar_nodes,
                }
            )
        return self._all_nodes

    @property
    def datamodels(self) -> MappingProxyType[str, type[DataModel]]:
        """
        Get all the datamodels
        """
        from roman_datamodels.datamodels import DataModel

        if self._datamodels is None:
            self._datamodels = MappingProxyType({**get_nodes(DataModel, (DataModel,))})

        return self._datamodels

    @property
    def implied_nodes(self) -> MappingProxyType[str, type[ImpliedNodeMixin]]:
        """
        Get a mapping of all the nodes that are implied by the schema in RAD

        Returns
        -------
        MappingProxyType[str, type]
            schema_uri -> class
        """
        if self._implied_nodes is None:
            registry = {}
            for name, node in self.all_nodes.items():
                if issubclass(node, ImpliedNodeMixin):
                    registry[name] = node

            self._implied_nodes = MappingProxyType(registry)

        return self._implied_nodes

    @property
    def enum_nodes(self) -> MappingProxyType[str, type[Enum]]:
        """
        Get a mapping of all the nodes that are enums

        Returns
        -------
        MappingProxyType[str, type]
            schema_uri -> class
        """
        if self._enum_nodes is None:
            registry = {}
            for name, node in self.all_nodes.items():
                if issubclass(node, Enum):
                    registry[name] = node

            self._enum_nodes = MappingProxyType(registry)

        return self._enum_nodes

    @property
    def schema_registry(self) -> MappingProxyType[str, type[SchemaMixin]]:
        """
        Get a mapping of all the nodes that are described by a schema in RAD

        Returns
        -------
        MappingProxyType[str, type]
            schema_uri -> class
        """
        if self._schema_registry is None:
            registry = {}
            for node in self.all_nodes.values():
                if issubclass(node, SchemaMixin) and not node.__name__.endswith("Mixin"):
                    for uri in node.asdf_schema_uris:
                        registry[uri] = node

            self._schema_registry = MappingProxyType(registry)

        return self._schema_registry

    @property
    def tagged_registry(self) -> MappingProxyType[str, type[TagMixin]]:
        """
        Get a mapping of all the nodes that are tagged in

        Returns
        -------
        MappingProxyType[str, type]
            tag_uri -> class
        """
        if self._tagged_registry is None:
            registry = {}
            for node in self.all_nodes.values():
                if issubclass(node, TagMixin) and not node.__name__.endswith("Mixin"):
                    for uri in node.asdf_tag_uris:
                        registry[uri] = node

            self._tagged_registry = MappingProxyType(registry)

        return self._tagged_registry

    @property
    def node_datamodel_mapping(self) -> MappingProxyType[type, type[DataModel]]:
        """
        Get a mapping of all the nodes that are datamodels

        Returns
        -------
        MappingProxyType[str, type]
            schema_uri -> class
        """
        if self._node_datamodel_mapping is None:
            registry = {}
            for dm in self.datamodels.values():
                registry[dm.node_type()] = dm  # type: ignore[attr-defined]
            self._node_datamodel_mapping = MappingProxyType(registry)

        return self._node_datamodel_mapping

    @property
    def reserved_fields(self) -> tuple[str, ...]:
        """
        Get a tuple of all the names that are reserved from being a field in a node
        due to them being used as properties
        """
        from roman_datamodels import datamodels

        if self._reseved_fields is None:
            self._reseved_fields = tuple(
                get_all_fields(ObjectNode)
                | get_all_fields(SchemaObjectNode)
                | get_all_fields(TaggedObjectNode)
                | get_all_fields(ArrayFieldMixin)
                | get_all_fields(datamodels.DataModel)
            )

        return self._reseved_fields


RDM_NODE_REGISTRY = _RdmNodeRegistry()
