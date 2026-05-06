from __future__ import annotations

from collections.abc import Generator
from functools import cache
from typing import Any

from asdf import AsdfFile, get_config
from asdf.extension import ExtensionManager, TagDefinition
from asdf.resource import ResourceManager
from asdf.schema import load_schema
from asdf.util import uri_match
from semantic_version import Version

__all__ = ("get_default_tag", "get_latest_schema", "get_schema_from_tag", "get_schema_uri", "get_version")


def get_version(asdf_uri: str) -> Version:
    """Get the version of the of the schema from the ASDF URI"""
    # Pluck the version out of the URI if it has one, otherwise we assume it is
    #    0.0.0
    version = asdf_uri.rsplit("-", maxsplit=1)[-1] if "-" in asdf_uri else "0.0.0"

    # Fix the issue with the first data model manifest being 1.0 instead of 1.0.0
    #     which causes issues with semantic_version
    if version == "1.0":
        version = "1.0.0"

    return Version(version)


def _get_latest_uri(pattern: str, uri_source: Generator[str, None, None]) -> str | None:
    """
    Get the latest URI for a given pattern, from the uri source

    Parameters
    ----------
    pattern: str
        A uri, a uri prefix, or a pattern/wildcard to match against the URIs from
        the source
    uri_source: Generator[str, None, None]
        A generator that yields URIs to check against the pattern

    Returns
    -------
    str | None
        The latest URI for the given pattern, or None if no URIs match the pattern
    """
    if "*" not in pattern:
        # Make sure we have a version matching pattern
        pattern = f"{pattern.rsplit('-', maxsplit=1)[0] if '-' in pattern else pattern}-*"

    latest_uri: str | None = None
    latest_version = Version("0.0.0")

    for uri in uri_source:
        if uri_match(pattern, uri):
            if (version := get_version(uri)) > latest_version:
                latest_version = version
                latest_uri = uri

    return latest_uri


@cache
def get_default_tag(pattern: str) -> str | None:
    """
    Get the default tag for a given pattern. This is the tag with the latest version.

    Parameters
    ----------
    pattern: str
        A tag, a tag prefix, or a tag pattern/wildcard to match against the URIs from
        the source

    Returns
    -------
    str | None
        The default tag URI for the given pattern (None if the pattern doesn't match any tags)
    """

    def tag_uri_source() -> Generator[str, None, None]:
        manager: ExtensionManager
        tag_def: TagDefinition

        with AsdfFile() as af:
            manager = af.extension_manager

            for extension in manager.extensions:
                for tag_def in extension.tags:
                    yield tag_def.tag_uri

    return _get_latest_uri(pattern, tag_uri_source())


@cache
def get_latest_schema_uri(pattern: str) -> str | None:
    """
    Get the latest schema URI for a given pattern. This is the schema with the latest version.

    Parameters
    ----------
    pattern: str
        A schema_uri, a schema_uri prefix, or a schema_uri pattern/wildcard to match against the URIs from
        the source

    Returns
    -------
    str | None
        The latest schema URI for the given pattern (None if the pattern doesn't match any schemas)
    """

    def schema_uri_source() -> Generator[str, None, None]:
        manager: ResourceManager = get_config().resource_manager

        yield from manager

    return _get_latest_uri(pattern, schema_uri_source())


@cache
def get_latest_schema(pattern: str) -> tuple[str, Any]:
    """
    Get the latest schema for a given pattern. This is the schema with the latest version.

    Parameters
    ----------
    pattern: str
        A schema_uri, a schema_uri prefix, or a schema_uri pattern/wildcard to match against the URIs from
        the source

    Returns
    -------
    Any
        The latest schema for the given pattern (None if the pattern doesn't match any schemas)
    """
    schema_uri = get_latest_schema_uri(pattern)

    if schema_uri is None:
        raise ValueError(f"No schema URI found for pattern {pattern}")

    return schema_uri, load_schema(schema_uri, resolve_references=True)


@cache
def get_schema_uri(tag_uri: str) -> str:
    """
    Get the schema URI for a given tag URI.

    Parameters
    ----------
    tag_uri: str
        The tag URI to get the schema URIs for.

    Returns
    -------
    Returns the schema URI for the given tag URI.
    """

    manager: ExtensionManager
    tag_def: TagDefinition
    with AsdfFile() as af:
        manager = af.extension_manager

        if manager.handles_tag(tag_uri):
            tag_def = manager.get_tag_definition(tag_uri)
            # Technically there could be more than one schema uri per tag, but for
            #    RAD there should only be one.
            # No type hint for MyPy here
            return tag_def.schema_uris[0]  # type: ignore[no-any-return]

    raise ValueError(f"Tag URI {tag_uri} not found in ASDF extensions.")


@cache
def get_schema_from_tag(tag_uri: str) -> Any:
    """
    Get the schema for a given tag URI.

    Parameters
    ----------
    tag_uri: str
        The tag URI to get the schema for.

    Returns
    -------
    The schema for the given tag URI.
    """

    return load_schema(get_schema_uri(tag_uri), resolve_references=True)
