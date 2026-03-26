"""
Hold all the registry information for the STNode classes.
    These will be dynamically populated at import time by the subclasses
    whenever they generated.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, NotRequired, TypeAlias, TypedDict

if TYPE_CHECKING:
    from collections.abc import Generator, Iterable

    from ._converters import _RomanConverter
    from ._tagged import ManifestNode, TaggedListNode, TaggedObjectNode, TaggedScalarNode

    tagged_type: TypeAlias = type[TaggedObjectNode] | type[TaggedListNode] | type[TaggedScalarNode]


class ManifestTagEntry(TypedDict):
    tag_uri: str
    schema_uri: str
    description: NotRequired[str]


class ManifestSchema(TypedDict):
    id: str
    tags: list[ManifestTagEntry]


__all__ = ["REGISTRY", "ManifestSchema"]


@dataclass
class PatternRegistry:
    object: dict[str, type[TaggedObjectNode]] = field(default_factory=dict)
    list: dict[str, type[TaggedListNode]] = field(default_factory=dict)
    scalar: dict[str, type[TaggedScalarNode]] = field(default_factory=dict)

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


@dataclass
class TagRegistry:
    node: dict[str, tagged_type] = field(default_factory=dict)
    schema: dict[str, str] = field(default_factory=dict)
    manifest: dict[str, str] = field(default_factory=dict)

    def __contains__(self, tag_uri: str) -> bool:
        return tag_uri in self.node

    def __setitem__(self, tag_uri: str, entry: tuple[tagged_type, str, str]):
        if tag_uri in self:
            raise KeyError(f"tag_uri: {tag_uri} has already been registered")

        self.node[tag_uri] = entry[0]
        self.schema[tag_uri] = entry[1]
        self.manifest[tag_uri] = entry[2]

    def __iter__(self) -> Iterable[str]:
        return iter(self.node.keys())

    def __len__(self) -> int:
        return len(self.node)


@dataclass
class ManifestRegistry:
    node: dict[str, type[ManifestNode]] = field(default_factory=dict)
    tag: dict[str, list[str]] = field(default_factory=lambda: defaultdict(list))
    schema: dict[str, ManifestSchema] = field(default_factory=dict)

    def __iter__(self) -> Iterable[str]:
        return iter(self.node.keys())


@dataclass
class Registry:
    pattern: PatternRegistry = field(default_factory=PatternRegistry)
    tag: TagRegistry = field(default_factory=TagRegistry)
    manifest: ManifestRegistry = field(default_factory=ManifestRegistry)
    converters: dict[str, _RomanConverter] = field(default_factory=dict)

    def __getitem__(self, tag_uri) -> type[ManifestNode]:
        return self.manifest.node[self.tag.manifest[tag_uri]]

    @property
    def object_nodes(self) -> Generator[type[TaggedObjectNode], None, None]:
        yield from self.pattern.object_nodes

    @property
    def list_nodes(self) -> Generator[type[TaggedListNode], None, None]:
        yield from self.pattern.list_nodes

    @property
    def scalar_nodes(self) -> Generator[type[TaggedScalarNode], None, None]:
        yield from self.pattern.scalar_nodes

    @property
    def nodes(self) -> Generator[tagged_type, None, None]:
        yield from self.pattern.nodes


REGISTRY = Registry()
