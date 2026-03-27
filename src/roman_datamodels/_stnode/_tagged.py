"""
Base classes for all the tagged objects defined by RAD.
    Each tagged object will be dynamically created at runtime by _stnode.py
    from RAD's manifest.
"""

from __future__ import annotations

import copy
from typing import TYPE_CHECKING, Generic, TypeVar

from astropy.time import Time

from . import _mixins
from ._node import DNode, LNode
from ._registry import REGISTRY, ManifestSchema, ManifestTagEntry
from ._schema import Builder, FakeDataBuilder, NodeBuilder
from ._utils import NO_VALUE, class_name_from_tag_uri, docstring_from_tag, get_schema_from_tag

if TYPE_CHECKING:
    from collections.abc import Mapping, MutableMapping
    from typing import Any, ClassVar, Self, TypeAlias

    from ._node import _NodeMixin as NodeMixin

else:
    NodeMixin: TypeAlias = object

__all__ = ["ManifestNode", "TaggedListNode", "TaggedObjectNode", "TaggedScalarNode"]


# Map of scalar types by pattern (str is default)
_SCALAR_TYPE_BY_PATTERN = {
    "asdf://stsci.edu/datamodels/roman/tags/file_date-*": Time,
    "asdf://stsci.edu/datamodels/roman/tags/fps/file_date-*": Time,
    "asdf://stsci.edu/datamodels/roman/tags/tvac/file_date-*": Time,
}
# Map of node types by pattern (TaggedObjectNode is default)
_LIST_NODE_PATTERN = ("asdf://stsci.edu/datamodels/roman/tags/cal_logs-*",)


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
        new = cls(builder.build(get_schema_from_tag(tag or cls._default_tag), defaults))

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
        return get_schema_from_tag(self.tag)

    @classmethod
    def _node_factory(cls, pattern: str, manifest_uri: str, tag_entry: ManifestTagEntry) -> type[Self]:
        """Factory method for dynamically creating a node"""
        if cls not in (TaggedObjectNode, TaggedListNode, TaggedScalarNode):
            raise TypeError("This class does not support the node factory")

        class_name = class_name_from_tag_uri(pattern)

        class_type: tuple[type, type[Self]] | tuple[type[Self]]
        if hasattr(_mixins, mixin := f"{class_name}Mixin"):
            class_type = (getattr(_mixins, mixin), cls)
        else:
            class_type = (cls,)

        return type(
            class_name,
            class_type,
            {
                "_pattern": pattern,
                "_latest_manifest": manifest_uri,
                "_default_tag": tag_entry["tag_uri"],
                "__module__": "roman_datamodels._stnode",
                "__doc__": docstring_from_tag(tag_entry),
                "__slots__": (),
            },
        )


class TaggedObjectNode(DNode, _TaggedNodeMixin):
    """
    Base class for all tagged objects defined by RAD
        There will be one of these for any tagged object defined by RAD, which has
        base type: object.
    """

    __slots__ = ()

    def __init_subclass__(cls, **kwargs) -> None:
        """
        Register any subclasses of this class in the REGISTRY
        """
        super().__init_subclass__(**kwargs)
        if cls.__name__ != "TaggedObjectNode":
            if cls._pattern in REGISTRY.pattern.object:
                raise RuntimeError(f"TaggedObjectNode class for tag '{cls._pattern}' has been defined twice")
            REGISTRY.pattern.object[cls._pattern] = cls


class TaggedListNode(LNode, _TaggedNodeMixin):
    """
    Base class for all tagged list defined by RAD
        There will be one of these for any tagged object defined by RAD, which has
        base type: array.
    """

    __slots__ = ()

    def __init_subclass__(cls, **kwargs) -> None:
        """
        Register any subclasses of this class in the registry
        """
        super().__init_subclass__(**kwargs)
        if cls.__name__ != "TaggedListNode":
            if cls._pattern in REGISTRY.pattern.list:
                raise RuntimeError(f"TaggedListNode class for tag '{cls._pattern}' has been defined twice")
            REGISTRY.pattern.list[cls._pattern] = cls


class TaggedScalarNode(_TaggedNodeMixin):
    """
    Base class for all tagged scalars defined by RAD
        There will be one of these for any tagged object defined by RAD, which has
        a scalar base type, or wraps a scalar base type.
        These will all be in the tagged_scalars directory.
    """

    def __init_subclass__(cls, **kwargs) -> None:
        """
        Register any subclasses of this class in the registry.
        """
        super().__init_subclass__(**kwargs)
        if cls.__name__ != "TaggedScalarNode":
            if cls._pattern in REGISTRY.pattern.scalar:
                raise RuntimeError(f"TaggedScalarNode class for tag '{cls._pattern}' has been defined twice")
            REGISTRY.pattern.scalar[cls._pattern] = cls

    def __asdf_traverse__(self):
        return self

    @classmethod
    def _create_minimal(cls, defaults=None, builder=None, *, tag: str | None = None):
        builder = builder or Builder()
        value = builder.build(get_schema_from_tag(tag or cls._default_tag), defaults)
        if value is NO_VALUE:
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

    @classmethod
    def _node_factory(cls, pattern: str, manifest_uri: str, tag_entry: ManifestTagEntry) -> type[TaggedScalarNode]:
        if cls is not TaggedScalarNode:
            raise TypeError("This class does not support the node factory")

        class_name = class_name_from_tag_uri(pattern)

        # TaggedScalarNode subclasses are really subclasses of the type of the scalar,
        #   with the TaggedScalarNode as a mixin.  This is because the TaggedScalarNode
        #   is supposed to be the scalar, but it needs to be serializable under a specific
        #   ASDF tag.
        # _SCALAR_TYPE_BY_PATTERN will need to be updated as new wrappers of scalar types are added
        #   to the RAD manifest.
        # assume everything is a string if not otherwise defined
        class_type = _SCALAR_TYPE_BY_PATTERN.get(pattern, str)

        # In special cases one may need to add additional features to a tagged node class.
        #   This is done by creating a mixin class with the name <ClassName>Mixin in _mixins.py
        #   Here we mixin the mixin class if it exists.
        if hasattr(_mixins, mixin := f"{class_name}Mixin"):
            class_type = (class_type, getattr(_mixins, mixin), cls)
        else:
            class_type = (class_type, cls)

        return type(
            class_name,
            class_type,
            {
                "_pattern": pattern,
                "_latest_manifest": manifest_uri,
                "_default_tag": tag_entry["tag_uri"],
                "__module__": "roman_datamodels._stnode",
                "__doc__": docstring_from_tag(tag_entry),
            },
        )


_T = TypeVar("_T", bound=TaggedObjectNode | TaggedListNode | TaggedScalarNode)
tagged_type: TypeAlias = type[TaggedObjectNode] | type[TaggedListNode] | type[TaggedScalarNode]


class ManifestNode(Generic[_T]):
    """
    Intermediate class used to assist in serialization of Tagged objects under
    a given manifest
    """

    _manifest_uri: ClassVar[str]

    def __init_subclass__(cls, **kwargs) -> None:
        """
        Register any subclasses of this class in the registry.
        """
        super().__init_subclass__(**kwargs)
        if cls.__name__ != "SerializationTaggedNode":
            if cls._manifest_uri in REGISTRY.manifest.node:
                raise RuntimeError(f"SerializationNode class for '{cls._manifest_uri}' has been defined twice")

            REGISTRY.manifest.node[cls._manifest_uri] = cls

    def __init__(self, data: _T, tag: str):
        self._data = data
        self._tag = tag

    @property
    def tag(self) -> str:
        return self._tag

    @property
    def data(self) -> _T:
        return self._data

    @classmethod
    def _factory(cls, manifest_uri: str) -> type[ManifestNode]:
        """Create a subclass of this for the given tag"""
        tag_uri, version = manifest_uri.rsplit("-", maxsplit=1)

        return type(
            f"SerializationNode_{class_name_from_tag_uri(tag_uri)}__{version.replace('.', '_')}",
            (ManifestNode,),
            {
                "_manifest_uri": manifest_uri,
                "__module__": "roman_datamodels._stnode",
            },
        )

    @classmethod
    def _node_factory(
        cls, pattern: str, manifest_uri: str, tag_entry: ManifestTagEntry
    ) -> type[TaggedObjectNode] | type[TaggedListNode] | type[TaggedScalarNode]:
        if "tagged_scalar" in tag_entry["schema_uri"]:
            return TaggedScalarNode._node_factory(pattern, manifest_uri, tag_entry)

        if pattern in _LIST_NODE_PATTERN:
            return TaggedListNode._node_factory(pattern, manifest_uri, tag_entry)

        return TaggedObjectNode._node_factory(pattern, manifest_uri, tag_entry)

    @classmethod
    def factory(
        cls, manifest: ManifestSchema
    ) -> list[type[TaggedObjectNode] | type[TaggedListNode] | type[TaggedScalarNode] | type[ManifestNode]]:
        """Factory for all objects that should be created from a manifest"""
        nodes: list[type[TaggedObjectNode] | type[TaggedListNode] | type[TaggedScalarNode] | type[ManifestNode]] = [
            cls._factory(manifest_uri := manifest["id"])
        ]
        REGISTRY.manifest.schema[manifest_uri] = manifest

        for tag_entry in manifest["tags"]:
            tag_uri = tag_entry["tag_uri"]
            pattern = f"{tag_uri.rsplit('-', maxsplit=1)[0]}-*"

            # Create a new node for the pattern if it does note exist
            if pattern not in REGISTRY.pattern:
                nodes.append(cls._node_factory(pattern, manifest_uri, tag_entry))

            # Register the node for the given tag
            if tag_uri not in REGISTRY.tag:
                REGISTRY.tag[tag_uri] = (
                    REGISTRY.pattern[pattern],
                    tag_entry["schema_uri"],
                    manifest_uri,
                )
                REGISTRY.manifest.tag[manifest_uri].append(tag_uri)

        return nodes
