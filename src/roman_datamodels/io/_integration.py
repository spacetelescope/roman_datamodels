from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from asdf.extension import ManifestExtension


def get_extensions() -> list[ManifestExtension]:
    """
    Get the extension instances for the various astropy
    extensions.  This method is registered with the
    `asdf.extension` entry point.

    """
    from ._converters import NODE_EXTENSIONS

    return NODE_EXTENSIONS
