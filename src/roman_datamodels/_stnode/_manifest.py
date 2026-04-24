"""
Dynamic creation of STNode classes from the RAD manifest.
    This module will create all the STNode based classes used by roman_datamodels.
    Unfortunately, this is a dynamic process which occurs at first import time because
    roman_datamodels cannot predict what STNode objects will be in the version of RAD
    used by the user.
"""

from __future__ import annotations

import importlib.resources
from pathlib import Path

import yaml
from rad import resources

__all__ = ["MANIFESTS", "MANIFEST_TAG_REGISTRY", "SCHEMA_URIS_BY_TAG", "TAG_MANIFEST_REGISTRY"]


# Load the manifest directly from the rad resources and not from ASDF.
#   This is because the ASDF extensions have to be created before they can be registered
#   and this module creates the classes used by the ASDF extension.
_MANIFEST_DIR = Path(str(importlib.resources.files(resources) / "manifests"))
# TODO: We should make this use semantic versioning to sort to ensure we don't get something strange
_DATAMODEL_MANIFEST_PATHS = sorted([path for path in _MANIFEST_DIR.glob("*datamodels-*.yaml")], reverse=True)
DATAMODEL_MANIFESTS = [yaml.safe_load(path.read_bytes()) for path in _DATAMODEL_MANIFEST_PATHS]
# Notice that the static manifests are first so that we defer to them
MANIFESTS = DATAMODEL_MANIFESTS

MANIFEST_TAG_REGISTRY: dict[str, list[str]] = {}
SCHEMA_URIS_BY_TAG: dict[str, str] = {}
TAG_MANIFEST_REGISTRY: dict[str, str] = {}

for manifest in MANIFESTS:
    manifest_uri = manifest["id"]

    MANIFEST_TAG_REGISTRY[manifest_uri] = []
    for tag_def in manifest["tags"]:
        SCHEMA_URIS_BY_TAG[(tag_uri := tag_def["tag_uri"])] = tag_def["schema_uri"]

        # make mapping of tags and manifests
        if tag_uri not in TAG_MANIFEST_REGISTRY:
            TAG_MANIFEST_REGISTRY[tag_uri] = manifest_uri
            MANIFEST_TAG_REGISTRY[manifest_uri].append(tag_uri)
