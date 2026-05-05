"""
Dynamic creation of STNode classes from the RAD manifest.
    This module will create all the STNode based classes used by roman_datamodels.
    Unfortunately, this is a dynamic process which occurs at first import time because
    roman_datamodels cannot predict what STNode objects will be in the version of RAD
    used by the user.
"""

import importlib.resources
from pathlib import Path

import yaml
from asdf.extension import ManifestExtension
from rad import resources

from ._converters import SerializationNodeConverter
from ._factories import stnode_factory
from ._registry import (
    LIST_NODE_CLASSES_BY_PATTERN,
    MANIFEST_TAG_REGISTRY,
    NODE_CLASSES_BY_TAG,
    NODE_CONVERTERS,
    NODES_BY_PATTERN,
    OBJECT_NODE_CLASSES_BY_PATTERN,
    SCALAR_NODE_CLASSES_BY_PATTERN,
    SCHEMA_URIS_BY_TAG,
    TAG_MANIFEST_REGISTRY,
)
from ._tagged import SerializationNode

__all__ = ["NODE_CLASSES", "NODE_EXTENSIONS"]


# Load the manifest directly from the rad resources and not from ASDF.
#   This is because the ASDF extensions have to be created before they can be registered
#   and this module creates the classes used by the ASDF extension.
_MANIFEST_DIR = Path(str(importlib.resources.files(resources) / "manifests"))
_DATAMODEL_MANIFEST_PATHS = sorted(
    [path for path in _MANIFEST_DIR.glob("*datamodels-*.yaml")],
    reverse=True,
    key=lambda v: tuple(int(i) for i in v.stem.rsplit("-")[-1].split(".")),
)
DATAMODEL_MANIFESTS = [yaml.safe_load(path.read_bytes()) for path in _DATAMODEL_MANIFEST_PATHS]
# Notice that the static manifests are first so that we defer to them
_MANIFESTS = DATAMODEL_MANIFESTS


def _add_cls(cls):
    class_name = cls.__name__
    globals()[class_name] = cls  # Add to namespace of module
    __all__.append(class_name)  # add to __all__ so it's imported with `from . import *`
    return cls


def _factory(pattern, latest_manifest, tag_def):
    """
    Wrap the __all__ append and class creation in a function to avoid the linter
        getting upset
    """
    return _add_cls(stnode_factory(pattern, latest_manifest, tag_def))


# Main dynamic class creation loop
#   Reads each tag entry from the manifest and creates a class for it
for manifest in _MANIFESTS:
    _add_cls(SerializationNode._factory(manifest_uri := manifest["id"]))

    MANIFEST_TAG_REGISTRY[manifest_uri] = []
    for tag_def in manifest["tags"]:
        SCHEMA_URIS_BY_TAG[(tag_uri := tag_def["tag_uri"])] = tag_def["schema_uri"]
        base, _ = tag_uri.rsplit("-", maxsplit=1)

        # make pattern from tag
        pattern = f"{base}-*"
        if pattern not in NODES_BY_PATTERN:
            NODES_BY_PATTERN[pattern] = _factory(pattern, manifest_uri, tag_def)
        NODE_CLASSES_BY_TAG[tag_uri] = NODES_BY_PATTERN[pattern]

        # Make serialization intermediate
        if tag_uri not in TAG_MANIFEST_REGISTRY:
            TAG_MANIFEST_REGISTRY[tag_uri] = manifest_uri
            MANIFEST_TAG_REGISTRY[manifest_uri].append(tag_uri)


# Create the ASDF extension for the STNode classes.
#    ASDF extension is setup here so that it is after the dynamic object creation
NODE_EXTENSIONS = {
    manifest_uri: ManifestExtension.from_uri(
        manifest_uri, converters=(SerializationNodeConverter(manifest_uri), *tuple(NODE_CONVERTERS.values()))
    )
    for manifest_uri in MANIFEST_TAG_REGISTRY
}


# List of node classes made available by this library.
#   This is part of the public API.
NODE_CLASSES = (
    list(OBJECT_NODE_CLASSES_BY_PATTERN.values())
    + list(LIST_NODE_CLASSES_BY_PATTERN.values())
    + list(SCALAR_NODE_CLASSES_BY_PATTERN.values())
)
