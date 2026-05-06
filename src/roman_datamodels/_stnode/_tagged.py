"""
Base classes for all the tagged objects defined by RAD.
    Each tagged object will be dynamically created at runtime by _stnode.py
    from RAD's manifest.
"""

from __future__ import annotations

import copy
from abc import abstractmethod
from typing import TYPE_CHECKING, final

from asdf.extension import SerializationContext
from astropy.time import Time

from ._node import DNode, LNode
from ._schema import Builder, FakeDataBuilder, NodeBuilder, NoValueType
from ._uri import get_schema_from_tag

if TYPE_CHECKING:
    from collections.abc import Mapping, MutableMapping
    from typing import Any, Self, TypeAlias

    from ._manifest import ManifestNode
    from ._node import _NodeMixin as NodeMixin
else:
    NodeMixin: TypeAlias = object

__all__ = (
    "TaggedListNode",
    "TaggedNode",
    "TaggedObjectNode",
    "TaggedScalarNode",
    "TaggedStrNode",
    "TaggedTimeNode",
)


class TaggedNode(NodeMixin):
    """
    Mixin class to provide the common API for all tagged objects.

    Note: the _create_* methods are prefixed with an underscore to prevent them from
        exposing the builder parameter to as part of the public API. They are the real
        implementations of the public create_* methods, which simply call the underscored
        versions without passing a builder. The builder is argument is needed by the Builder
        objects to pass themselves back through the chain of building calls during nested
        building operations.
    """

    __slots__ = ()

    @classmethod
    def from_tag(cls, *, node: Any, tag: str) -> Self:
        """
        Create an instance of this class from a node for a given tag.

        Parameters
        ----------
        node: Any
            The node to create the instance from
        tag: str
            The tag to use when creating the instance.
        """
        new = cls(node)

        # This is a bit hacky, but the TaggedScalar node classes don't have a
        #    easy way to inject the tag into the __init__ method, so we set it
        #    here like this after the fact.
        new._read_tag = tag

        return new

    @staticmethod
    def _build_node(
        *,
        tag: str,
        defaults: Mapping[str, Any] | None,
        builder: Builder | None,
    ) -> Any:
        return (builder or Builder()).build(get_schema_from_tag(tag), defaults)

    @classmethod
    def _create_minimal(
        cls,
        tag: str,
        *,
        defaults: Mapping[str, Any] | None = None,
        builder: Builder | None = None,
    ) -> Self | None:
        return cls.from_tag(node=cls._build_node(tag=tag, defaults=defaults, builder=builder), tag=tag)

    @classmethod
    @final
    def create_minimal(
        cls,
        tag: str,
        defaults: Mapping[str, Any] | None = None,
    ) -> Self | None:
        """
        Create a minimal instance of this class, only things with the attributes
        which have a default value that can be determined.

        Parameters
        ----------
        tag : str
            The tag to use when creating the instance.
        defaults : Mapping[str, Any] | None
            A mapping of default values to use when creating the instance

        Returns
        -------
        Self
            An instance of this class, or None if creation failed
        """
        return cls._create_minimal(tag=tag, defaults=defaults)

    @classmethod
    def _create_fake_data(
        cls,
        tag: str,
        *,
        defaults: Mapping[str, Any] | None = None,
        shape: tuple[int, ...] | None = None,
        builder: Builder | None = None,
    ) -> Self | None:
        return cls._create_minimal(
            tag=tag,
            defaults=defaults,
            builder=(builder or FakeDataBuilder(shape)),
        )

    @classmethod
    @final
    def create_fake_data(
        cls,
        tag: str,
        defaults: Mapping[str, Any] | None = None,
        shape: tuple[int, ...] | None = None,
    ) -> Self | None:
        """
        Create an instance of this class with with all required attributes
        filled in with fake data.

        Parameters
        ----------
        tag: str
            The tag to use when creating the instance.
        defaults: Mapping[str, Any] | None
            A mapping of default values to use when creating the instance
        shape: tuple[int, ...] | None
            The shape of the data to create

        Returns
        -------
        Self | None
            An instance of this class, or None if creation failed
        """
        return cls._create_fake_data(tag=tag, defaults=defaults, shape=shape)

    @classmethod
    def _create_from_node(
        cls,
        tag: str,
        *,
        node: MutableMapping[str, Any],
        builder: Builder | None = None,
    ) -> Self | None:
        return cls._create_minimal(
            tag=tag,
            defaults=node,
            builder=(builder or NodeBuilder()),
        )

    @classmethod
    @final
    def create_from_node(
        cls,
        tag: str,
        node: MutableMapping[str, Any],
    ) -> Self | None:
        """
        Create an instance of this class from a node (dict-like object)

        Parameters
        ----------
        tag: str
            The tag to use when creating the instance.
        node: MutableMapping[str, Any]
            The node to create the instance from

        Returns
        -------
        Self | None
            An instance of this class, or None if creation failed
        """
        return cls._create_from_node(tag=tag, node=node)

    @property
    def _tag(self) -> str:
        """__asdf_traverse__ requires that we have a _tag attribute, so this accommodates that"""
        if self._read_tag is None:
            raise AttributeError("TaggedNode instances must have a _read_tag attribute")

        return self._read_tag

    @property
    def tag(self) -> str:
        """The tag this node is operating under"""
        return self._tag

    def get_schema(self):
        """Retrieve the schema associated with this tag"""
        return get_schema_from_tag(self.tag)

    @abstractmethod
    def _to_asdf_tree(self, ctx: SerializationContext) -> Any:
        """
        Convert this object to a ManifestNode for ASDF serialization.

        Parameters
        ----------
        ctx:
            The ASDF serialization context to use when converting this object to a ManifestNode.
        """

    @final
    def to_asdf_tree(self, ctx: SerializationContext) -> ManifestNode:
        """
        Convert this object to a ManifestNode for ASDF serialization.

        Parameters
        ----------
        ctx:
            The ASDF serialization context to use when converting this object to a ManifestNode.
        """
        from roman_datamodels import Manager

        return Manager().tags[self._tag](data=self._to_asdf_tree(ctx), tag=self._tag)


class TaggedObjectNode(DNode, TaggedNode):
    """
    Base class for all tagged objects defined by RAD
        There will be one of these for any tagged object defined by RAD, which has
        base type: object.
    """

    __slots__ = ()

    def _to_asdf_tree(self, ctx: SerializationContext) -> Any:
        return dict(self._data)


class TaggedListNode(LNode, TaggedNode):
    """
    Base class for all tagged list defined by RAD
        There will be one of these for any tagged object defined by RAD, which has
        base type: array.
    """

    __slots__ = ()

    def _to_asdf_tree(self, ctx: SerializationContext) -> Any:
        return list(self.data)


class TaggedScalarNode(TaggedNode):
    """
    Base class for all tagged scalars defined by RAD
        There will be one of these for any tagged object defined by RAD, which has
        a scalar base type, or wraps a scalar base type.
        These will all be in the tagged_scalars directory.
    """

    def __asdf_traverse__(self):
        return self

    @classmethod
    def _create_minimal(
        cls,
        tag: str,
        *,
        defaults: Mapping[str, Any] | None = None,
        builder: Builder | None = None,
    ) -> Self | None:
        if isinstance(
            value := cls._build_node(tag=tag, defaults=defaults, builder=builder),
            NoValueType,
        ):
            return None

        return cls.from_tag(node=value, tag=tag)

    @property
    def _tag(self) -> str:
        # _tag is required by asdf to allow __asdf_traverse__
        if self._read_tag is None:
            raise AttributeError("TaggedNode instances must have a _read_tag attribute")

        return self._read_tag

    def copy(self):
        return copy.copy(self)


# TODO: MyPy doesn't like the disjoint bases
class TaggedStrNode(str, TaggedScalarNode):  # type: ignore[misc]
    def _to_asdf_tree(self, ctx: SerializationContext) -> Any:
        return str(self)


class TaggedTimeNode(Time, TaggedScalarNode):
    @classmethod
    def _create_minimal(
        cls,
        tag: str,
        *,
        defaults: Mapping[str, Any] | None = None,
        builder: Builder | None = None,
    ) -> Self | None:
        return cls.from_tag(
            node=(cls(defaults) if defaults else cls.now()),
            tag=tag,
        )

    @classmethod
    def _create_fake_data(
        cls,
        tag: str,
        *,
        defaults: Mapping[str, Any] | None = None,
        shape: tuple[int, ...] | None = None,
        builder: Builder | None = None,
    ) -> Self | None:
        return cls.from_tag(
            node=(cls(defaults) if defaults else cls("2020-01-01T00:00:00.0", format="isot", scale="utc")),
            tag=tag,
        )

    def _to_asdf_tree(self, ctx: SerializationContext) -> Any:
        return ctx.extension_manager.get_converter_for_type(Time).to_yaml_tree(self, self._tag, ctx)
