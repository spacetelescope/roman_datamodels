"""
Hold all the registry information for the STNode classes.
    These will be dynamically populated at import time by the subclasses
    whenever they generated.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._converters import _RomanConverter
    from ._tagged import SerializationNode, TaggedListNode, TaggedNode, TaggedObjectNode, TaggedScalarNode

OBJECT_NODE_CLASSES_BY_PATTERN: dict[str, type[TaggedObjectNode]] = {}
LIST_NODE_CLASSES_BY_PATTERN: dict[str, type[TaggedListNode]] = {}
SCALAR_NODE_CLASSES_BY_PATTERN: dict[str, type[TaggedScalarNode]] = {}
NODES_BY_PATTERN: dict[str, type[TaggedNode]] = {}
NODE_CONVERTERS: dict[str, type[_RomanConverter]] = {}
NODE_CLASSES_BY_TAG: dict[str, type[TaggedNode]] = {}
SCHEMA_URIS_BY_TAG: dict[str, str] = {}
SERIALIZATION_BY_MANIFEST: dict[str, type[SerializationNode]] = {}
MANIFEST_TAG_REGISTRY: dict[str, list[str]] = {}
TAG_MANIFEST_REGISTRY: dict[str, str] = {}
