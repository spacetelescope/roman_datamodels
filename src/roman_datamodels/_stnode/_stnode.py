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

from ._converters import ManifestNodeConverter
from ._registry import REGISTRY
from ._tagged import ManifestNode

__all__ = []


# Load the manifest directly from the rad resources and not from ASDF.
#   This is because the ASDF extensions have to be created before they can be registered
#   and this module creates the classes used by the ASDF extension.
_MANIFEST_DIR = Path(str(importlib.resources.files(resources) / "manifests"))
# TODO: We should make this use semantic versioning to sort to ensure we don't get something strange
_DATAMODEL_MANIFEST_PATHS = sorted([path for path in _MANIFEST_DIR.glob("*datamodels-*.yaml")], reverse=True)
DATAMODEL_MANIFESTS = [yaml.safe_load(path.read_bytes()) for path in _DATAMODEL_MANIFEST_PATHS]


for manifest in DATAMODEL_MANIFESTS:
    for node in ManifestNode.factory(manifest):
        globals()[node.__name__] = node
        __all__.append(node.__name__)

# Create the ASDF extension for the STNode classes.
#    ASDF extension is setup here so that it is after the dynamic object creation
for manifest_uri in REGISTRY.manifest_uri:
    REGISTRY.manifest_uri.asdf_extension[manifest_uri] = ManifestExtension.from_uri(
        manifest_uri, converters=(ManifestNodeConverter(manifest_uri), *tuple(REGISTRY.asdf_converter.values()))
    )

__all__ = tuple(__all__)
