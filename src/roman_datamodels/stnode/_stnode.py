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
DATAMODELS_MANIFEST_PATH = importlib.resources.files(resources) / "manifests" / "datamodels-1.0.yaml"
DATAMODELS_MANIFEST = yaml.safe_load(DATAMODELS_MANIFEST_PATH.read_bytes())


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
for tag in DATAMODELS_MANIFEST["tags"]:
    _factory(tag)


# List of node classes made available by this library.
#   This is part of the public API.
NODE_CLASSES = (
    list(OBJECT_NODE_CLASSES_BY_TAG.values())
    + list(LIST_NODE_CLASSES_BY_TAG.values())
    + list(SCALAR_NODE_CLASSES_BY_TAG.values())
)
