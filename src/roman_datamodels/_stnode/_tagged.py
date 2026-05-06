"""
Base classes for all the tagged objects defined by RAD.
    Each tagged object will be dynamically created at runtime by _stnode.py
    from RAD's manifest.
"""

from __future__ import annotations

import copy
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, final

from asdf.extension import SerializationContext
from astropy.time import Time

from ._node import DNode, LNode
from ._registry import (
    LIST_NODE_CLASSES_BY_PATTERN,
    OBJECT_NODE_CLASSES_BY_PATTERN,
    SCALAR_NODE_CLASSES_BY_PATTERN,
    TAG_MANIFEST_REGISTRY,
)
from ._schema import Builder, FakeDataBuilder, NodeBuilder, NoValueType, _get_schema_from_tag
from ._uri import get_default_tag

if TYPE_CHECKING:
    from collections.abc import Mapping, MutableMapping
    from typing import Any, ClassVar, Self, TypeAlias

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


def name_from_tag_uri(tag_uri: str) -> str:
    """
    Compute the name of the schema from the tag_uri.

    Parameters
    ----------
    tag_uri : str
        The tag_uri to find the name from
    """
    tag_uri_split = tag_uri.split("/")[-1].split("-")[0]
    if "/tvac/" in tag_uri and "tvac" not in tag_uri_split:
        tag_uri_split = "tvac_" + tag_uri.split("/")[-1].split("-")[0]
    elif "/fps/" in tag_uri and "fps" not in tag_uri_split:
        tag_uri_split = "fps_" + tag_uri.split("/")[-1].split("-")[0]
    return tag_uri_split


def class_name_from_tag_uri(tag_uri: str) -> str:
    """
    Construct the class name for the STNode class from the tag_uri

    Parameters
    ----------
    tag_uri : str
        The tag_uri found in the RAD manifest

    Returns
    -------
    string name for the class
    """
    tag_name = name_from_tag_uri(tag_uri)
    class_name = "".join([p.capitalize() for p in tag_name.split("_")])
    if tag_uri.startswith("asdf://stsci.edu/datamodels/roman/tags/reference_files/"):
        class_name += "Ref"

    return class_name


class TaggedNode(ABC, NodeMixin):
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

    _tag_pattern: ClassVar[str]

    @classmethod
    def default_tag(cls) -> str:
        """Get the default tag for this class"""

        if (tag := get_default_tag(cls._tag_pattern)) is None:
            raise RuntimeError(f"No default tag found for pattern '{cls._tag_pattern}'")

        return tag

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
        defaults: Mapping[str, Any] | None = None,
        builder: Builder | None = None,
    ) -> Any:
        return (builder or Builder()).build(_get_schema_from_tag(tag), defaults)

    @classmethod
    def _create_minimal(
        cls,
        *,
        defaults: Mapping[str, Any] | None = None,
        builder: Builder | None = None,
        tag: str | None = None,
    ) -> Self | None:
        tag = tag or cls.default_tag()
        return cls.from_tag(node=cls._build_node(tag=tag, defaults=defaults, builder=builder), tag=tag)

    @classmethod
    @final
    def create_minimal(
        cls,
        defaults: Mapping[str, Any] | None = None,
        *,
        tag: str | None = None,
    ) -> Self | None:
        """
        Create a minimal instance of this class, only things with the attributes
        which have a default value that can be determined.

        Parameters
        ----------
        defaults : Mapping[str, Any] | None
            A mapping of default values to use when creating the instance
        tag : str | None
            The tag to use when creating the instance. If None, the default tag for the class will be used.

        Returns
        -------
        Self
            An instance of this class, or None if creation failed
        """
        return cls._create_minimal(defaults=defaults, tag=tag)

    @classmethod
    def _create_fake_data(
        cls,
        *,
        defaults: Mapping[str, Any] | None = None,
        shape: tuple[int, ...] | None = None,
        builder: Builder | None = None,
        tag: str | None = None,
    ) -> Self | None:
        return cls._create_minimal(
            defaults=defaults,
            builder=(builder or FakeDataBuilder(shape)),
            tag=tag,
        )

    @classmethod
    @final
    def create_fake_data(
        cls,
        defaults: Mapping[str, Any] | None = None,
        shape: tuple[int, ...] | None = None,
        *,
        tag: str | None = None,
    ) -> Self | None:
        """
        Create an instance of this class with with all required attributes
        filled in with fake data.

        Parameters
        ----------
        defaults: Mapping[str, Any] | None
            A mapping of default values to use when creating the instance
        shape: tuple[int, ...] | None
            The shape of the data to create
        tag: str | None
            The tag to use when creating the instance. If None, the default tag for the class will be used.

        Returns
        -------
        Self | None
            An instance of this class, or None if creation failed
        """
        return cls._create_fake_data(defaults=defaults, shape=shape, tag=tag)

    @classmethod
    def _create_from_node(
        cls,
        *,
        node: MutableMapping[str, Any],
        builder: Builder | None = None,
        tag: str | None = None,
    ) -> Self | None:
        return cls._create_minimal(
            defaults=node,
            builder=(builder or NodeBuilder()),
            tag=tag,
        )

    @classmethod
    @final
    def create_from_node(
        cls,
        node: MutableMapping[str, Any],
        *,
        tag: str | None = None,
    ) -> Self | None:
        """
        Create an instance of this class from a node (dict-like object)

        Parameters
        ----------
        node: MutableMapping[str, Any]
            The node to create the instance from
        tag: str | None
            The tag to use when creating the instance. If None, the default tag for the class will be used.

        Returns
        -------
        Self | None
            An instance of this class, or None if creation failed
        """
        return cls._create_from_node(node=node, tag=tag)

    @property
    def _tag(self):
        if self._read_tag is None:
            return self.default_tag()

        return self._read_tag

    @property
    def tag(self):
        return self._tag

    def get_schema(self):
        """Retrieve the schema associated with this tag"""
        return _get_schema_from_tag(self.tag)

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
        return TAG_MANIFEST_REGISTRY[self._tag](data=self._to_asdf_tree(ctx), tag=self._tag)


class TaggedObjectNode(DNode, TaggedNode):
    """
    Base class for all tagged objects defined by RAD
        There will be one of these for any tagged object defined by RAD, which has
        base type: object.
    """

    __slots__ = ()

    def __init_subclass__(cls, **kwargs) -> None:
        """
        Register any subclasses of this class in the OBJECT_NODE_CLASSES_BY_PATTERN
        registry.
        """
        super().__init_subclass__(**kwargs)
        if cls.__name__ != "TaggedObjectNode":
            if cls._tag_pattern in OBJECT_NODE_CLASSES_BY_PATTERN:
                raise RuntimeError(f"TaggedObjectNode class for tag '{cls._tag_pattern}' has been defined twice")

            OBJECT_NODE_CLASSES_BY_PATTERN[cls._tag_pattern] = cls

    def _to_asdf_tree(self, ctx: SerializationContext) -> Any:
        return dict(self._data)


class TaggedListNode(LNode, TaggedNode):
    """
    Base class for all tagged list defined by RAD
        There will be one of these for any tagged object defined by RAD, which has
        base type: array.
    """

    __slots__ = ()

    def __init_subclass__(cls, **kwargs) -> None:
        """
        Register any subclasses of this class in the LIST_NODE_CLASSES_BY_PATTERN
        registry.
        """
        super().__init_subclass__(**kwargs)
        if cls.__name__ != "TaggedListNode":
            if cls._tag_pattern in LIST_NODE_CLASSES_BY_PATTERN:
                raise RuntimeError(f"TaggedListNode class for tag '{cls._tag_pattern}' has been defined twice")
            LIST_NODE_CLASSES_BY_PATTERN[cls._tag_pattern] = cls

    def _to_asdf_tree(self, ctx: SerializationContext) -> Any:
        return list(self.data)


class TaggedScalarNode(TaggedNode):
    """
    Base class for all tagged scalars defined by RAD
        There will be one of these for any tagged object defined by RAD, which has
        a scalar base type, or wraps a scalar base type.
        These will all be in the tagged_scalars directory.
    """

    def __init_subclass__(cls, **kwargs) -> None:
        """
        Register any subclasses of this class in the SCALAR_NODE_CLASSES_BY_PATTERN registry.
        """
        super().__init_subclass__(**kwargs)
        if cls.__name__ not in ("TaggedScalarNode", "TaggedStrNode", "TaggedTimeNode"):
            if cls._tag_pattern in SCALAR_NODE_CLASSES_BY_PATTERN:
                raise RuntimeError(f"TaggedScalarNode class for tag '{cls._tag_pattern}' has been defined twice")
            SCALAR_NODE_CLASSES_BY_PATTERN[cls._tag_pattern] = cls

    def __asdf_traverse__(self):
        return self

    @classmethod
    def _create_minimal(
        cls,
        *,
        defaults: Mapping[str, Any] | None = None,
        builder: Builder | None = None,
        tag: str | None = None,
    ) -> Self | None:
        tag = tag or cls.default_tag()
        if isinstance(
            value := cls._build_node(tag=tag, defaults=defaults, builder=builder),
            NoValueType,
        ):
            return None

        return cls.from_tag(node=value, tag=tag)

    @property
    def _tag(self):
        # _tag is required by asdf to allow __asdf_traverse__
        return getattr(self, "_read_tag", self.default_tag())

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
        *,
        defaults: Mapping[str, Any] | None = None,
        builder: Builder | None = None,
        tag: str | None = None,
    ) -> Self | None:
        return cls.from_tag(
            node=(cls(defaults) if defaults else cls.now()),
            tag=(tag or cls.default_tag()),
        )

    @classmethod
    def _create_fake_data(
        cls,
        *,
        defaults: Mapping[str, Any] | None = None,
        shape: tuple[int, ...] | None = None,
        builder: Builder | None = None,
        tag: str | None = None,
    ) -> Self | None:
        return cls.from_tag(
            node=(cls(defaults) if defaults else cls("2020-01-01T00:00:00.0", format="isot", scale="utc")),
            tag=(tag or cls.default_tag()),
        )

    def _to_asdf_tree(self, ctx: SerializationContext) -> Any:
        return ctx.extension_manager.get_converter_for_type(Time).to_yaml_tree(self, self._tag, ctx)
