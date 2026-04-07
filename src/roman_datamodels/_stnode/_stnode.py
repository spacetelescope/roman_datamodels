"""
Dynamic creation of STNode classes from the RAD manifest.
    This module will create all the STNode based classes used by roman_datamodels.
    Unfortunately, this is a dynamic process which occurs at first import time because
    roman_datamodels cannot predict what STNode objects will be in the version of RAD
    used by the user.
"""

import importlib.resources
from pathlib import Path
from types import MappingProxyType

import yaml
from rad import resources

from ._factories import stnode_factory
from ._tagged import SerializationNode, TagUriInfo

__all__ = []


# Load the manifest directly from the rad resources and not from ASDF.
#   This is because the ASDF extensions have to be created before they can be registered
#   and this module creates the classes used by the ASDF extension.
_MANIFEST_DIR = Path(str(importlib.resources.files(resources) / "manifests"))
# TODO: We should make this use semantic versioning to sort to ensure we don't get something strange
_DATAMODEL_MANIFEST_PATHS = sorted([path for path in _MANIFEST_DIR.glob("*datamodels-*.yaml")], reverse=True)
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
for _manifest in _MANIFESTS:
    _manifest_uri = _manifest["id"]

    _tag_uris = {}
    tag_patterns = []
    for tag_def in _manifest["tags"]:
        tag_uri = tag_def["tag_uri"]
        tag_pattern = f"{tag_uri.rsplit('-', maxsplit=1)[0]}-*"

        if (node_type := SerializationNode.tag_pattern_type(tag_pattern)) is None:
            tag_patterns.append(tag_pattern)
            node_type = _factory(tag_pattern, _manifest_uri, tag_def)

        if not SerializationNode.serialization_type(tag_uri):
            _tag_uris[tag_uri] = TagUriInfo(schema_uri=tag_def["schema_uri"], type=node_type)

    # Make serialization intermediate
    _add_cls(SerializationNode._factory(_manifest_uri, tuple(tag_patterns), MappingProxyType(_tag_uris)))
