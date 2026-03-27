"""
The STNode classes and supporting objects generated dynamically at import time
    from RAD's manifest.
"""

from __future__ import annotations

from asdf import get_config
from asdf.extension import ManifestExtension
from asdf.schema import load_schema

from ._converters import ManifestNodeConverter
from ._mixins import ImageSourceCatalogMixin
from ._node import DNode, LNode
from ._registry import REGISTRY
from ._tagged import ManifestNode, TaggedListNode, TaggedObjectNode, TaggedScalarNode
from ._utils import get_latest_schema, get_version

__all__ = (
    "REGISTRY",
    "DNode",
    "ImageSourceCatalogMixin",
    "LNode",
    "TaggedListNode",
    "TaggedObjectNode",
    "TaggedScalarNode",
    "get_latest_schema",
)

# Find the RAD datamodels manifest URIs registered with ASDF by the RAD package.
_MANIFEST_PREFIX = "asdf://stsci.edu/datamodels/roman/manifests/datamodels-"
_manifest_uris = {get_version(uri): uri for uri in get_config().resource_manager if uri.startswith(_MANIFEST_PREFIX)}

# Reverse sort the manifest_uris so that the latest version is first, then loop
#    through them to create the STNode classes dynamically.
# Note this forces tags into the LATEST extension for which that tag is listed
#    in its respective manifest, this means that if a file is made with the latest
#    RAD version, it will only have a single asdf extension for Roman listed in
#    its history section. Indeed files made with tags from datamodels-1.4.0 or
#    later will only have a single Roman extension listed in their history section.
# Note that the keys of the dict being looped through are semantic_version.Version
#    objects, so they will always be sorted correctly
_all_nodes: list[str] = []
for _version in sorted(_manifest_uris, reverse=True):
    for _node in ManifestNode.factory(load_schema(_manifest_uris[_version])):
        globals()[_node.__name__] = _node
        _all_nodes.append(_node.__name__)

# Create the ASDF extension for the STNode classes.
#    ASDF extension is setup here so that we ensure that all of the dynamically
#    generated STNode classes are available when ASDF goes to use the ROMAN
#    extensions provided by roman_datamodels.
for _manifest_uri in REGISTRY.manifest_uri:
    REGISTRY.manifest_uri.asdf_extension[_manifest_uri] = ManifestExtension.from_uri(
        _manifest_uri, converters=(ManifestNodeConverter(_manifest_uri), *tuple(REGISTRY.asdf_converter.values()))
    )

__all__ += tuple(_all_nodes)
