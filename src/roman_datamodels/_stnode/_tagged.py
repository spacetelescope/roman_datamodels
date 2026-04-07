"""
Base classes for all the tagged objects defined by RAD.
    Each tagged object will be dynamically created at runtime by _stnode.py
    from RAD's manifest.
"""

from __future__ import annotations

import copy
from abc import abstractmethod
from types import MappingProxyType
from typing import TYPE_CHECKING, NamedTuple

from conditional_cache import lru_cache as cache

from ._node import DNode, LNode
from ._schema import _NO_VALUE, Builder, FakeDataBuilder, NodeBuilder, _get_schema_from_tag

if TYPE_CHECKING:
    from collections.abc import Mapping, MutableMapping
    from typing import Any, ClassVar, Self, TypeAlias

    from ._node import _NodeMixin as NodeMixin
else:
    NodeMixin: TypeAlias = object

__all__ = ["SerializationNode", "TaggedListNode", "TaggedObjectNode", "TaggedScalarNode"]


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


class _TaggedNodeMixin(NodeMixin):
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

    _pattern: ClassVar[str]
    _latest_manifest: ClassVar[str]

    _default_tag: ClassVar[str]

    @classmethod
    def _create_minimal(
        cls, defaults: Mapping[str, Any] | None = None, builder: Builder | None = None, *, tag: str | None = None
    ) -> Self:
        builder = builder or Builder()
        new = cls(builder.build(_get_schema_from_tag(tag or cls._default_tag), defaults))

        if tag:
            new._read_tag = tag

        return new

    @classmethod
    def create_minimal(cls, defaults: Mapping[str, Any] | None = None, *, tag: str | None = None) -> Self:
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
            An instance of this class
        """
        return cls._create_minimal(defaults, tag=tag)

    @classmethod
    def _create_fake_data(
        cls,
        defaults: Mapping[str, Any] | None = None,
        shape: tuple[int, ...] | None = None,
        builder: Builder | None = None,
        *,
        tag: str | None = None,
    ) -> Self:
        return cls._create_minimal(defaults, builder or FakeDataBuilder(shape), tag=tag)

    @classmethod
    def create_fake_data(
        cls, defaults: Mapping[str, Any] | None = None, shape: tuple[int, ...] | None = None, *, tag: str | None = None
    ) -> Self:
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
        Self
            An instance of this class
        """
        return cls._create_fake_data(defaults, shape, tag=tag)

    @classmethod
    def _create_from_node(cls, node: MutableMapping[str, Any], builder: Builder | None = None, *, tag: str | None = None) -> Self:
        return cls._create_minimal(node, builder or NodeBuilder(), tag=tag)

    @classmethod
    def create_from_node(cls, node: MutableMapping[str, Any], *, tag: str | None = None) -> Self:
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
        Self
            An instance of this class
        """
        return cls._create_from_node(node, tag=tag)

    @property
    def _tag(self):
        if self._read_tag is None:
            return self._default_tag

        return self._read_tag

    @property
    def tag(self):
        return self._tag

    def get_schema(self):
        """Retrieve the schema associated with this tag"""
        return _get_schema_from_tag(self.tag)

    @abstractmethod
    def _serialize_data(self, ctx):
        """
        Turn the data stored in this node into the untagged object
        that ASDF will tag and write
        """

    def _serialize(self, ctx) -> SerializationNode:
        """
        Create the SerializationNode instance which handles the deferred ASDF
        serialization

        Parameters
        ----------
        ctx :
            The ASDF serialization context

        Return
        ------

            An instance of a serialization node that ASDF will then defer to in
            order to tag it properly
        """

        cls: type[SerializationNode] | None = SerializationNode.serialization_type(self.tag)
        if cls:
            return cls(self._serialize_data(ctx), self.tag)

        raise RuntimeError(f"No node found to serialize tag: {self.tag}")


class TaggedObjectNode(DNode, _TaggedNodeMixin):
    """
    Base class for all tagged objects defined by RAD
        There will be one of these for any tagged object defined by RAD, which has
        base type: object.
    """

    __slots__ = ()

    def _serialize_data(self, ctx):
        return dict(self._data)


class TaggedListNode(LNode, _TaggedNodeMixin):
    """
    Base class for all tagged list defined by RAD
        There will be one of these for any tagged object defined by RAD, which has
        base type: array.
    """

    __slots__ = ()

    def _serialize_data(self, ctx):
        return list(self)


class TaggedScalarNode(_TaggedNodeMixin):
    """
    Base class for all tagged scalars defined by RAD
        There will be one of these for any tagged object defined by RAD, which has
        a scalar base type, or wraps a scalar base type.
        These will all be in the tagged_scalars directory.
    """

    def __asdf_traverse__(self):
        return self

    @classmethod
    def _create_minimal(cls, defaults=None, builder=None, *, tag: str | None = None):
        builder = builder or Builder()
        value = builder.build(_get_schema_from_tag(tag or cls._default_tag), defaults)
        if value is _NO_VALUE:
            return value

        new = cls(value)
        if tag:
            new._read_tag = tag

        return new

    @property
    def _tag(self):
        # _tag is required by asdf to allow __asdf_traverse__
        return getattr(self, "_read_tag", self._default_tag)

    def copy(self):
        return copy.copy(self)

    def _serialize_data(self, ctx):
        data = type(self).__bases__[0](self)

        if "file_date" in self.tag:
            converter = ctx.extension_manager.get_converter_for_type(type(data))
            return converter.to_yaml_tree(data, self.tag, ctx)

        return data


tagged_type: TypeAlias = type[TaggedObjectNode] | type[TaggedListNode] | type[TaggedScalarNode]


class TagUriInfo(NamedTuple):
    schema_uri: str
    type: tagged_type


class SerializationNode:
    """
    Intermediate class used to assist in serialization of Tagged objects
    so that the extension is correctly written.
    """

    __slots__ = ("_data", "_tag")

    manifest_uri: ClassVar[str]
    tag_patterns: ClassVar[tuple[str, ...]]
    tag_uris: ClassVar[MappingProxyType[str, TagUriInfo]]

    def __init__(self, data: Any, tag: str):
        self._data = data
        self._tag = tag

    @property
    def tag(self) -> str:
        return self._tag

    @property
    def data(self) -> Any:
        return self._data

    @staticmethod
    @cache(condition=lambda result: result is not None)
    def serialization_type(tag_uri: str) -> type[SerializationNode] | None:
        """
        Get the SerializationNode class associated with the given tag, if any

            Note this returns a None value so that we can use it to check
            if a tag is already handled by a SerializationNode

        Parameters
        ----------
        tag_uri :
            The tag_uri in question

        Returns
        -------

            The actual SerializationNode subclass that handles the tag
            or None if that node does not exist yet
        """
        subclass: type[SerializationNode]

        for subclass in SerializationNode.__subclasses__():
            if tag_uri in subclass.tag_uris:
                return subclass

        return None

    @staticmethod
    def tag_type(tag_uri: str) -> tagged_type:
        """
        Get the node type that handles a given tag

        Parameters
        ----------
        tag_uri :
            The tag_uri in question

        Returns
        -------
        type
            The Node type that handles the given tag_uri

        Raises
        ------
        RuntimeError
            if no node handles this type
        """
        subclass: type[SerializationNode] | None = SerializationNode.serialization_type(tag_uri)

        if subclass:
            return subclass.tag_uris[tag_uri].type

        raise RuntimeError(f"No SerializationNode class found for tag: {tag_uri}")

    @staticmethod
    @cache(condition=lambda result: result is not None)
    def tag_pattern_type(tag_pattern: str) -> tagged_type | None:
        """
        Get the Node type for the given tag pattern

            Note this returns None if a tag_pattern is not currently being
            handled for purposes of dynamic code generation

        Parameters
        ----------
        tag_pattern :
            <tag_uri_prefix>-* style string

        Returns
        -------
        type | None
            The Node type handling the pattern or None
        """
        subclass: type[SerializationNode]

        for subclass in SerializationNode.__subclasses__():
            if tag_pattern in subclass.tag_patterns:
                return next(
                    uri_info.type
                    for tag_uri, uri_info in subclass.tag_uris.items()
                    if tag_uri.startswith(tag_pattern.rsplit("-", maxsplit=1)[0])
                )

        return None

    @staticmethod
    def schema_uri(tag_uri: str) -> str:
        """
        Get the schema_uri associated with the given tag

            Note this makes it so you don't have to feed tag_uri into this twice

        Parameters
        ----------
        tag_uri :
            The tag_uri in question

        Returns
        -------
        str
            The schema_uri associated with the tag in RAD

        Raises
        ------
        RuntimeError
            if no node handles this type
        """
        subclass: type[SerializationNode] | None = SerializationNode.serialization_type(tag_uri)

        if subclass:
            return subclass.tag_uris[tag_uri].schema_uri

        raise RuntimeError(f"No SerializationNode class found for tag: {tag_uri}")

    @staticmethod
    def _factory(manifest_uri: str, tag_patterns: tuple[str, ...], tag_uris: tuple[str, ...]) -> type[SerializationNode]:
        """Create a subclass of this for the given tag"""
        tag_uri, version = manifest_uri.rsplit("-", maxsplit=1)

        return type(
            f"SerializationNode_{class_name_from_tag_uri(tag_uri)}__{version.replace('.', '_')}",
            (SerializationNode,),
            {
                "manifest_uri": manifest_uri,
                "tag_patterns": tag_patterns,
                "tag_uris": tag_uris,
                "__module__": "roman_datamodels._stnode",
                "__slots__": (),
            },
        )
