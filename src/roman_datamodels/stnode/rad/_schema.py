from abc import ABC, abstractmethod

from ..core import classproperty
from ._asdf_schema import SCHEMA_REGISTRY, RadSchema
from ._base import RadNodeMixin
from ._node import ListNode, ObjectNode, ScalarNode

__all__ = [
    "SchemaListNode",
    "SchemaMixin",
    "SchemaObjectNode",
    "SchemaScalarNode",
]


class SchemaMixin(RadNodeMixin, ABC):
    """Mixin for nodes to support linking to a schema."""

    @classmethod
    @abstractmethod
    def _asdf_schema_uris(cls) -> tuple[str, ...]:
        """URIs for the schemas that defines this node."""

    @classproperty
    def asdf_schema_uris(cls) -> tuple[str, ...]:
        """
        The URIs of the schemas for this class.
        """
        return cls._asdf_schema_uris()

    @classproperty
    def asdf_schema_uri(cls) -> str:
        """
        The latest schema for this class.
        """
        # This is reached by the docs build as it ignores the abstractness of the class
        # which causes a doc failure, the cache makes this irrelevant in general
        if not cls.asdf_schema_uris:
            return ""
        return cls.asdf_schema_uris[-1]

    @property
    def schema_uri(self) -> str:
        """
        The schema_uri for this instance.
            Note: we cannot determine the schema_uri for an untagged node from
            the asdf file.
        """
        return self.asdf_schema_uri

    @classmethod
    def _asdf_schema(cls) -> RadSchema:
        """
        The latest schema for this class.
        """
        return SCHEMA_REGISTRY.get_schema(cls.asdf_schema_uri)

    @property
    def schema(self) -> RadSchema:
        """
        The schema for this instance.
        """
        return SCHEMA_REGISTRY.get_schema(self.schema_uri)


class SchemaObjectNode(ObjectNode, SchemaMixin, ABC):
    """
    Base class for all objects described by their own schema in RAD.
    """


class SchemaListNode(ListNode, SchemaMixin, ABC):
    """
    Base class for all list nodes described by their own schema in RAD.
    """


class SchemaScalarNode(ScalarNode, SchemaMixin, ABC):
    """
    Base class for all scalars that are described by their own schema in RAD.
    """
