"""
Hold all the registry information for the STNode classes.
    These will be dynamically populated at import time by the subclasses
    whenever they generated.
"""

from __future__ import annotations

import importlib.resources
from pathlib import Path
from typing import TYPE_CHECKING

import yaml
from rad import resources

if TYPE_CHECKING:
    from ._converters import _RomanConverter
    from ._tagged import TaggedListNode, TaggedObjectNode, TaggedScalarNode, tagged_type

# Load the manifest directly from the rad resources and not from ASDF.
#   This is because the ASDF extensions have to be created before they can be registered
#   and this module creates the classes used by the ASDF extension.
_MANIFEST_DIR = Path(str(importlib.resources.files(resources) / "manifests"))
# sort manifests by version (newest first)
_STATIC_MANIFEST_PATHS = sorted([path for path in _MANIFEST_DIR.glob("*static-*.yaml")], reverse=True)
STATIC_MANIFESTS = [yaml.safe_load(path.read_bytes()) for path in _STATIC_MANIFEST_PATHS]
_DATAMODEL_MANIFEST_PATHS = sorted([path for path in _MANIFEST_DIR.glob("*datamodels-*.yaml")], reverse=True)
DATAMODEL_MANIFESTS = [yaml.safe_load(path.read_bytes()) for path in _DATAMODEL_MANIFEST_PATHS]

OBJECT_NODE_CLASSES_BY_PATTERN: dict[str, type[TaggedObjectNode]] = {}
LIST_NODE_CLASSES_BY_PATTERN: dict[str, type[TaggedListNode]] = {}
SCALAR_NODE_CLASSES_BY_PATTERN: dict[str, type[TaggedScalarNode]] = {}
STATIC_CONVERTERS: dict[str, type[_RomanConverter]] = {}
DATAMODEL_CONVERTERS: dict[str, type[_RomanConverter]] = {}
NODE_CLASSES_BY_TAG: dict[str, tagged_type] = {}
SCHEMA_URIS_BY_TAG: dict[str, str] = {}
STATIC_PATTERNS: dict[str, tagged_type] = {}
DATAMODEL_PATTERNS: dict[str, tagged_type] = {}
