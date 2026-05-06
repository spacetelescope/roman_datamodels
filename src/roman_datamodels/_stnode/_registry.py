"""
Hold all the registry information for the STNode classes.
    These will be dynamically populated at import time by the subclasses
    whenever they generated.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._manifest import ManifestNode
    from ._tagged import TaggedListNode, TaggedNode, TaggedObjectNode, TaggedScalarNode

OBJECT_NODE_CLASSES_BY_PATTERN: dict[str, type[TaggedObjectNode]] = {}
LIST_NODE_CLASSES_BY_PATTERN: dict[str, type[TaggedListNode]] = {}
SCALAR_NODE_CLASSES_BY_PATTERN: dict[str, type[TaggedScalarNode]] = {}
NODES_BY_PATTERN: dict[str, type[TaggedNode]] = {}
NODE_CLASSES_BY_TAG: dict[str, type[TaggedNode]] = {}
MANIFEST_TAG_REGISTRY: dict[str, list[str]] = {}
TAG_MANIFEST_REGISTRY: dict[str, type[ManifestNode]] = {}
