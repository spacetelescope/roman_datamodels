"""
Dynamic creation of STNode classes from the RAD manifest.
    This module will create all the STNode based classes used by roman_datamodels.
    Unfortunately, this is a dynamic process which occurs at first import time because
    roman_datamodels cannot predict what STNode objects will be in the version of RAD
    used by the user.
"""

from types import MappingProxyType

from asdf import get_config
from asdf.extension import ManifestExtension

from ._converters import SerializationNodeConverter
from ._factories import stnode_factory
from ._registry import (
    LIST_NODE_CLASSES_BY_PATTERN,
    MANIFEST_TAG_REGISTRY,
    NODE_CLASSES_BY_TAG,
    NODE_CONVERTERS,
    OBJECT_NODE_CLASSES_BY_PATTERN,
    SCALAR_NODE_CLASSES_BY_PATTERN,
    TAG_MANIFEST_REGISTRY,
)
from ._tagged import SerializationNode
from ._uri import UriInfo

__all__ = ["NODE_CLASSES", "NODE_EXTENSIONS"]


MANIFEST_PREFIX = "asdf://stsci.edu/datamodels/roman/manifests/datamodels"
_manifest_version_uri = MappingProxyType(
    {
        (uri_info := UriInfo(uri, "asdf_resource")).version: uri_info
        for uri in get_config().resource_manager
        if uri.startswith(MANIFEST_PREFIX)
    }
)


def _add_cls(cls):
    class_name = cls.__name__
    globals()[class_name] = cls  # Add to namespace of module
    __all__.append(class_name)  # add to __all__ so it's imported with `from . import *`
    return cls


def _factory(tag_info, latest_manifest, tag_def):
    """
    Wrap the __all__ append and class creation in a function to avoid the linter
        getting upset
    """
    return _add_cls(stnode_factory(tag_info, latest_manifest, tag_def))


# Main dynamic class creation loop
#   Reads each tag entry from the manifest and creates a class for it
_generated = {}
_MANIFESTS = []
for version in sorted(_manifest_version_uri, reverse=True):
    manifest = _manifest_version_uri[version].schema
    _MANIFESTS.append(manifest)

    _add_cls(SerializationNode._factory(manifest_uri := manifest["id"]))

    MANIFEST_TAG_REGISTRY[manifest_uri] = []
    for tag_def in manifest["tags"]:
        tag_info = UriInfo(tag_def["tag_uri"], "asdf_tag")

        if tag_info.pattern not in _generated:
            _generated[tag_info.pattern] = _factory(tag_info, manifest_uri, tag_def)
        NODE_CLASSES_BY_TAG[tag_info.uri] = _generated[tag_info.pattern]

        # Make serialization intermediate
        if tag_info.uri not in TAG_MANIFEST_REGISTRY:
            TAG_MANIFEST_REGISTRY[tag_info.uri] = manifest_uri
            MANIFEST_TAG_REGISTRY[manifest_uri].append(tag_info.uri)


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
