from functools import cache

from asdf import AsdfFile
from asdf.extension import Extension, ExtensionManager, TagDefinition
from asdf.util import uri_match
from semantic_version import Version

__all__ = ("get_default_tag", "get_version")


def get_version(asdf_uri: str) -> Version:
    """Get the version of the of the schema from the ASDF URI"""
    # Pluck the version out of the URI if it has one, otherwise we assume it is
    #    0.0.0
    version = asdf_uri.rsplit("-", maxsplit=1)[-1] if "-" in asdf_uri else "0.0.0"

    # Fix the issue with the first datamodel manifest being 1.0 instead of 1.0.0
    #     which causes issues with semantic_version
    if version == "1.0":
        version = "1.0.0"

    return Version(version)


@cache
def get_default_tag(pattern: str) -> str | None:
    """
    Get the default tag for a given pattern. This is the tag with the latest version.

    Parameters
    ----------
    pattern: str
        A tag pattern/wildcard

    Returns
    -------
    str | None
        The default tag URI for the given pattern
    """
    default_tag: str | None = None
    default_version = Version("0.0.0")

    extension: Extension
    tag_def: TagDefinition
    with AsdfFile() as af:
        manager: ExtensionManager = af.extension_manager

        for extension in manager.extensions:
            for tag_def in extension.tags:
                if uri_match(pattern, tag_def.tag_uri):
                    version = get_version(tag_def.tag_uri)
                    if version > default_version:
                        default_version = version
                        default_tag = tag_def.tag_uri

    return default_tag
