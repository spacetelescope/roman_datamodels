"""
Dynamic creation of STNode classes from the RAD manifest.
    This module will create all the STNode based classes used by roman_datamodels.
    Unfortunately, this is a dynamic process which occurs at first import time because
    roman_datamodels cannot predict what STNode objects will be in the version of RAD
    used by the user.
"""

import importlib.resources

import yaml
from rad import resources

from ._factories import stnode_factory
from ._registry import LIST_NODE_CLASSES_BY_TAG, OBJECT_NODE_CLASSES_BY_TAG, SCALAR_NODE_CLASSES_BY_TAG

__all__ = [
    "NODE_CLASSES",
]


# Load the manifest directly from the rad resources and not from ASDF.
#   This is because the ASDF extensions have to be created before they can be registered
#   and this module creates the classes used by the ASDF extension.
_MANIFEST_DIR = importlib.resources.files(resources) / "manifests"
_MANIFEST_PATHS = [path for path in _MANIFEST_DIR.glob("*.yaml")]
_MANIFESTS = [yaml.safe_load(path.read_bytes()) for path in _MANIFEST_PATHS]


def _factory(tag):
    """
    Wrap the __all__ append and class creation in a function to avoid the linter
        getting upset
    """
    cls = stnode_factory(tag)

    class_name = cls.__name__
    globals()[class_name] = cls  # Add to namespace of module
    __all__.append(class_name)  # add to __all__ so it's imported with `from . import *`


# Main dynamic class creation loop
#   Reads each tag entry from the manifest and creates a class for it
_generated = set()
for manifest in _MANIFESTS:
    for tag in manifest["tags"]:
        base, _ = tag["tag_uri"].rsplit("-", maxsplit=1)
        pattern = f"{base}-*"
        if pattern not in _generated:
            _factory(pattern)
            _generated.add(pattern)


# List of node classes made available by this library.
#   This is part of the public API.
NODE_CLASSES = (
    list(OBJECT_NODE_CLASSES_BY_TAG.values())
    + list(LIST_NODE_CLASSES_BY_TAG.values())
    + list(SCALAR_NODE_CLASSES_BY_TAG.values())
)
