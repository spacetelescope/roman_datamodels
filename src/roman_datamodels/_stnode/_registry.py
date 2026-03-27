"""
Hold all the registry information for the STNode classes.
    These will be dynamically populated at import time by the subclasses
    whenever they generated.
"""

from __future__ import annotations

from collections.abc import MutableMapping, MutableSet
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, ClassVar, NotRequired, TypeAlias, TypedDict, TypeVar

if TYPE_CHECKING:
    from collections.abc import Generator, Iterator

    from asdf.extension import ManifestExtension

    from ._converters import _RomanConverter
    from ._mixins import _BaseForNodeMixin
    from ._tagged import ManifestNode, TaggedListNode, TaggedObjectNode, TaggedScalarNode

    tagged_type: TypeAlias = type[TaggedObjectNode] | type[TaggedListNode] | type[TaggedScalarNode]

_T = TypeVar("_T")


class ManifestTagEntry(TypedDict):
    tag_uri: str
    schema_uri: str
    description: NotRequired[str]


class ManifestSchema(TypedDict):
    id: str
    tags: list[ManifestTagEntry]


__all__ = ["REGISTRY", "ManifestSchema", "ManifestTagEntry"]


@dataclass(frozen=True, slots=True)
class RegistryMap(MutableMapping[str, _T]):
    _registry: dict[str, _T] = field(default_factory=dict)

    def __getitem__(self, key: str) -> _T:
        return self._registry[key]

    def __setitem__(self, key: str, value: _T):
        if key in self._registry:
            raise KeyError(f"Cannot overwrite an existing item in the registry for {key}")

        self._registry[key] = value

    def __delitem__(self, key: str):
        raise NotImplementedError("Cannot delete item from the registry")

    def __iter__(self) -> Iterator[str]:
        return iter(self._registry)

    def __len__(self) -> int:
        return len(self._registry)


@dataclass(frozen=True, slots=True)
class RegistrySet(MutableSet[_T]):
    _registry: set[_T] = field(default_factory=set)

    def __contains__(self, value) -> bool:
        return value in self._registry

    def __iter__(self) -> Iterator[_T]:
        return iter(self._registry)

    def __len__(self) -> int:
        return len(self._registry)

    def add(self, value: _T):
        if value in self._registry:
            raise ValueError(f"Cannot add existing value {value} to the registry")

        self._registry.add(value)

    def discard(self, value: _T):
        raise NotImplementedError("Cannot discard values from the registry")


@dataclass(frozen=True, slots=True)
class RegistryMapSet(RegistryMap[RegistrySet[_T]]):
    def __getitem__(self, key: str) -> RegistrySet[_T]:
        if key not in self._registry:
            self._registry[key] = RegistrySet()

        return self._registry[key]

    def __setitem__(self, key: str, value: RegistrySet[_T]):
        raise NotImplementedError("Cannot directly add item to registry")


@dataclass(frozen=True, slots=True)
class TagPatternRegistry:
    """
    Class to hold lookup Registries of Nodes based on tag-patterns

        Note: a tag-pattern can only exist in one of the three maps
            in this registry so we can treat it like a categorized
            map for general access purposes

    Parameters
    ----------
    object:
        The map from tag-pattern to corresponding object Node

    list:
        The map from tag-pattern to corresponding list Node

    scalar:
        The map from tag-pattern to corresponding scalar Node
    """

    object: RegistryMap[type[TaggedObjectNode]] = field(default_factory=RegistryMap)
    list: RegistryMap[type[TaggedListNode]] = field(default_factory=RegistryMap)
    scalar: RegistryMap[type[TaggedScalarNode]] = field(default_factory=RegistryMap)

    def __contains__(self, pattern: str) -> bool:
        return (pattern in self.object) or (pattern in self.list) or (pattern in self.scalar)

    def __getitem__(self, pattern: str) -> tagged_type:
        if pattern in self.object:
            return self.object[pattern]

        if pattern in self.list:
            return self.list[pattern]

        if pattern in self.scalar:
            return self.scalar[pattern]

        raise KeyError(f"Pattern: {pattern} not registered!")

    @property
    def object_nodes(self) -> Generator[type[TaggedObjectNode], None, None]:
        """Generator for object nodes"""
        yield from self.object.values()

    @property
    def list_nodes(self) -> Generator[type[TaggedListNode], None, None]:
        """Generator for list nodes"""
        yield from self.list.values()

    @property
    def scalar_nodes(self) -> Generator[type[TaggedScalarNode], None, None]:
        """Generator for all scalar nodes"""
        yield from self.scalar.values()

    @property
    def nodes(self) -> Generator[tagged_type, None, None]:
        """Generator for all the nodes"""

        yield from self.object_nodes
        yield from self.list_nodes
        yield from self.scalar_nodes


@dataclass(frozen=True, slots=True)
class TagUriRegistry:
    """
    Class to hold Registries to look up information using the tag_uris

        Note: Every tag_uri will have an entry in every map of this registry

    Parameters
    ----------
    node:
        The map from tag_uri to Node class

    schema_uri:
        The map from tag_uri to schema_uri

    manifest_uri:
        The map from tag_uri to manifest_uri
    """

    node: RegistryMap[tagged_type] = field(default_factory=RegistryMap)
    schema_uri: RegistryMap[str] = field(default_factory=RegistryMap)
    manifest_uri: RegistryMap[str] = field(default_factory=RegistryMap)

    def __contains__(self, tag_uri: str) -> bool:
        return tag_uri in self.node

    def __setitem__(self, tag_uri: str, entry: tuple[tagged_type, str, str]):
        if tag_uri in self:
            raise KeyError(f"tag_uri: {tag_uri} has already been registered")

        self.node[tag_uri] = entry[0]
        self.schema_uri[tag_uri] = entry[1]
        self.manifest_uri[tag_uri] = entry[2]

    def __iter__(self) -> Iterator[str]:
        return iter(self.node)

    def __len__(self) -> int:
        return len(self.node)


@dataclass(frozen=True, slots=True)
class ManifestUriRegistry:
    """
    Class to hold Registries to look up information using the manifest_uris

        Note: Once stnode fully initializes there will be an entry in each
            map corresponding to each manifest_uri

    Parameters
    ----------
    node:
        The map from manifest_uri to the ManifestNode type handling that node

    tag_uri:
        The map from manifest_uri to the list of tag_uris that are associated with it

    asdf_schema:
        The map from manifest_uri to the parsed contents of the manifest's schema
    """

    node: RegistryMap[type[ManifestNode]] = field(default_factory=RegistryMap)
    tag_uri: RegistryMapSet[str] = field(default_factory=RegistryMapSet)
    asdf_extension: RegistryMap[ManifestExtension] = field(default_factory=RegistryMap)

    def __iter__(self) -> Iterator[str]:
        return iter(self.node)


@dataclass(frozen=True, slots=True)
class Registry:
    """
    Class to hold all the Registries used by stnode
        Note: This class is a singleton so it will always be the same object

    Parameters
    ----------
    tag_pattern:
        The tag_pattern registry

    tag_uri:
        The tag_uri registry

    manifest_uri:
        The manifest_uri registry

    converters:
        The asdf_converter registry
    """

    _instance: ClassVar[Registry | None] = None

    tag_pattern: TagPatternRegistry = field(default_factory=TagPatternRegistry)
    tag_uri: TagUriRegistry = field(default_factory=TagUriRegistry)
    manifest_uri: ManifestUriRegistry = field(default_factory=ManifestUriRegistry)
    mixins: RegistryMap[type[_BaseForNodeMixin]] = field(default_factory=RegistryMap)
    asdf_converter: RegistryMap[_RomanConverter] = field(default_factory=RegistryMap)

    # Turn this object into a singleton
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Registry, cls).__new__(cls, *args, **kwargs)

        return cls._instance

    def __getitem__(self, tag_uri) -> type[ManifestNode]:
        return self.manifest_uri.node[self.tag_uri.manifest_uri[tag_uri]]

    @property
    def object_nodes(self) -> Generator[type[TaggedObjectNode], None, None]:
        yield from self.tag_pattern.object_nodes

    @property
    def list_nodes(self) -> Generator[type[TaggedListNode], None, None]:
        yield from self.tag_pattern.list_nodes

    @property
    def scalar_nodes(self) -> Generator[type[TaggedScalarNode], None, None]:
        yield from self.tag_pattern.scalar_nodes

    @property
    def nodes(self) -> Generator[tagged_type, None, None]:
        yield from self.tag_pattern.nodes

    @property
    def asdf_extensions(self) -> list[ManifestExtension]:
        return list(self.manifest_uri.asdf_extension.values())


REGISTRY = Registry()
