"""
Hold all the registry information for the STNode classes.
    These will be dynamically populated at import time by the subclasses
    whenever they generated.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._tagged import tagged_type

NODE_CLASSES_BY_TAG: dict[str, tagged_type] = {}
SCHEMA_URIS_BY_TAG: dict[str, str] = {}
MANIFEST_TAG_REGISTRY: dict[str, list[str]] = {}
TAG_MANIFEST_REGISTRY: dict[str, str] = {}
