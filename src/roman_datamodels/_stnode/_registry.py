"""
Hold all the registry information for the STNode classes.
    These will be dynamically populated at import time by the subclasses
    whenever they generated.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._manifest import ManifestNode

TAG_MANIFEST_REGISTRY: dict[str, type[ManifestNode]] = {}
