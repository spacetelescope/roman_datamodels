from abc import ABC, abstractmethod
from types import MappingProxyType
from typing import Any, TypeVar

from asdf import AsdfFile
from asdf.lazy_nodes import AsdfDictNode, AsdfListNode
from astropy.time import Time

from ..core import DNode, FlushOptions, LNode, classproperty
from ._schema import SchemaListNode, SchemaMixin, SchemaObjectNode, SchemaScalarNode

__all__ = [
    "TagMixin",
    "TaggedListNode",
    "TaggedObjectNode",
    "TaggedScalarNode",
]

_T = TypeVar("_T")


class TagMixin(SchemaMixin, ABC):
    """Mixin for nodes to support linking to a tag."""

    _instance_tag: str | None = None

    @classmethod
    def _asdf_schema_uris(cls) -> tuple[str, ...]:
        """URIs for the schemas that defines this node."""

        return tuple(uri for uri in cls.asdf_tag_uris.values())

    @classmethod
    @abstractmethod
    def _asdf_tag_uris(cls) -> dict[str, str]:
        """Tag of the node."""

    @classproperty
    def asdf_tag_uris(cls) -> MappingProxyType[str, str]:
        """Get the tags for the class."""
        # This is reached by the docs build as it ignores the abstractness of the class
        # which causes a doc failure, the cache makes this irrelevant in general
        if not (uris := cls._asdf_tag_uris()):
            return MappingProxyType({})

        return MappingProxyType(uris)

    @classproperty
    def asdf_tag_uri(cls) -> str:
        """Get the latest tag URI for the node."""
        # This is reached by the docs build as it ignores the abstractness of the class
        # which causes a doc failure, the cache makes this irrelevant in general
        if not cls.asdf_tag_uris:
            return ""

        return list(cls.asdf_tag_uris)[-1]

    # TODO: Should not be hidden, but it breaks something when doing asdf_info
    @property
    def _tag(self) -> str:
        """Get the tag URI for the instance."""
        if self._instance_tag is None:
            self._instance_tag = self.asdf_tag_uri
        return self._instance_tag

    @property
    def schema_uri(self) -> str:
        """Get the schema URI for the instance."""
        return self.asdf_tag_uris[self._tag]


class TaggedObjectNode(SchemaObjectNode, TagMixin, ABC):
    """
    Base class for all objects that are tagged in RAD.
    """

    def __init__(
        self,
        node: dict[str, _T] | AsdfDictNode | DNode[_T] | None = None,
        *,
        tag: str | None = None,
        _array_shape: tuple[int, ...] | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(node=node, _array_shape=_array_shape, **kwargs)
        self._instance_tag = tag


class TaggedListNode(SchemaListNode, TagMixin, ABC):
    """
    Base class for all tagged list nodes defined by RAD
        There will be one of these for any tagged object defined by RAD, which has
        a list base type, or wraps a list base type.
        These will all be in the tagged_lists directory.
    """

    def __init__(self, node: list[Any] | AsdfListNode | LNode[Any] | None = None, *, tag: str | None = None) -> None:
        super().__init__(node=node)
        self._instance_tag = tag


class TaggedScalarNode(SchemaScalarNode, TagMixin, ABC):
    """
    Base class for all tagged scalars defined by RAD
        There will be one of these for any tagged object defined by RAD, which has
        a scalar base type, or wraps a scalar base type.
        These will all be in the tagged_scalars directory.
    """

    def to_asdf_tree(self, ctx: AsdfFile, flush: FlushOptions = FlushOptions.REQUIRED, warn: bool = False) -> Any:
        tree = super().to_asdf_tree(ctx, flush, warn)

        # Special handling for Time objects
        # -> others maybe needed in the future
        if isinstance(tree, Time):
            converter = ctx.extension_manager.get_converter_for_type(Time)
            return converter.to_yaml_tree(tree, self.asdf_tag_uris, ctx)

        return tree
