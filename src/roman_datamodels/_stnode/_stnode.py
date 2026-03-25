"""
Dynamic creation of STNode classes from the RAD manifest.
    This module will create all the STNode based classes used by roman_datamodels.
    Unfortunately, this is a dynamic process which occurs at first import time because
    roman_datamodels cannot predict what STNode objects will be in the version of RAD
    used by the user.
"""

from ._factories import stnode_factory
from ._registry import (
    DATAMODEL_MANIFESTS,
    DATAMODEL_PATTERNS,
    LIST_NODE_CLASSES_BY_PATTERN,
    NODE_CLASSES_BY_TAG,
    OBJECT_NODE_CLASSES_BY_PATTERN,
    SCALAR_NODE_CLASSES_BY_PATTERN,
    SCHEMA_URIS_BY_TAG,
    STATIC_MANIFESTS,
    STATIC_PATTERNS,
)

__all__ = ["DATAMODEL_MANIFESTS", "NODE_CLASSES", "STATIC_MANIFESTS"]


_MANIFESTS = STATIC_MANIFESTS + DATAMODEL_MANIFESTS


def _factory(pattern, latest_manifest, tag_def):
    """
    Wrap the __all__ append and class creation in a function to avoid the linter
        getting upset
    """
    cls = stnode_factory(pattern, latest_manifest, tag_def)

    class_name = cls.__name__
    globals()[class_name] = cls  # Add to namespace of module
    __all__.append(class_name)  # add to __all__ so it's imported with `from . import *`
    return cls


# Main dynamic class creation loop
#   Reads each tag entry from the manifest and creates a class for it
_generated = {}


def _process_manifest(manifest):
    manifest_uri = manifest["id"]
    nodes_by_pattern = {}
    for tag_def in manifest["tags"]:
        SCHEMA_URIS_BY_TAG[tag_def["tag_uri"]] = tag_def["schema_uri"]
        base, _ = tag_def["tag_uri"].rsplit("-", maxsplit=1)

        # make pattern from tag
        pattern = f"{base}-*"
        if pattern not in _generated:
            _generated[pattern] = _factory(pattern, manifest_uri, tag_def)
            nodes_by_pattern[pattern] = _generated[pattern]

        NODE_CLASSES_BY_TAG[tag_def["tag_uri"]] = _generated[pattern]

    return nodes_by_pattern


for manifest in STATIC_MANIFESTS:
    STATIC_PATTERNS.update(_process_manifest(manifest))


for manifest in DATAMODEL_MANIFESTS:
    DATAMODEL_PATTERNS.update(_process_manifest(manifest))


# List of node classes made available by this library.
#   This is part of the public API.
NODE_CLASSES = (
    list(OBJECT_NODE_CLASSES_BY_PATTERN.values())
    + list(LIST_NODE_CLASSES_BY_PATTERN.values())
    + list(SCALAR_NODE_CLASSES_BY_PATTERN.values())
)
