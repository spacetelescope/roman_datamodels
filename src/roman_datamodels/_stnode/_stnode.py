"""
Dynamic creation of STNode classes from the RAD manifest.
    This module will create all the STNode based classes used by roman_datamodels.
    Unfortunately, this is a dynamic process which occurs at first import time because
    roman_datamodels cannot predict what STNode objects will be in the version of RAD
    used by the user.
"""

from ._factories import stnode_factory
from ._manifest import MANIFESTS

__all__ = ["NODE_CLASSES"]


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
_generated = {}
for manifest in MANIFESTS:
    manifest_uri = manifest["id"]

    for tag_def in manifest["tags"]:
        tag_uri = tag_def["tag_uri"]
        base, _ = tag_uri.rsplit("-", maxsplit=1)

        # make pattern from tag
        pattern = f"{base}-*"
        if pattern not in _generated:
            _generated[pattern] = _factory(pattern, manifest_uri, tag_def)

# List of node classes made available by this library.
NODE_CLASSES = tuple(_generated.values())
