from __future__ import annotations

from collections.abc import Generator
from contextlib import contextmanager
from dataclasses import InitVar, dataclass, field
from functools import cache
from re import fullmatch
from typing import TYPE_CHECKING, Any, Literal, TypeAlias

from asdf import AsdfFile, get_config
from asdf.schema import load_schema
from semantic_version import Version

if TYPE_CHECKING:
    from asdf.extension import Extension, ExtensionManager, TagDefinition

__all__ = ("UriInfo", "get_latest_schema")


_uri_type: TypeAlias = Literal["asdf_tag", "asdf_resource", "not_asdf"]


# TODO: Should we upstream some of this functionality into ASDF itself?
@dataclass(frozen=True, slots=True)
class UriInfo:
    """
    A dataclass to hold the information about a URI and provide useful tools for the URI

    .. note::

        This class accepts uri fragments and patterns, with respect to the URI's version
        number. If the version number is not provided or given as a wildcard, this
        class will assume the version number parts are 0. For example:

            - ``<prefix>``
            - ``<prefix>-*``
            - ``<prefix>-*.*``
            - ``<prefix>-*.*.*``

        will all be treated as if they were ``<prefix>-0.0.0``.

    """

    exact_uri: str
    """
    The exact URI that was provided without any of the parsing and filling of the
        version number. This is useful for error messages and debugging.
    """

    uri_type: InitVar[_uri_type | None] = None
    """
    Flag to manually specify the URI flags.
        This is so that when we directly know the the type of URI we are creating
        (e.g., we know we have a tag or a schema URI) we can just set the flags
        directly instead of making an ASDF query to determine the flags.
    """

    uri: str = field(init=False)
    """
    The full URI, (including the version), related to what was provided.
        It will fill 0 in for each missing part of the semantic version number
        at end of the URI:

            ``<prefix>-<version>``
    """

    prefix: str = field(init=False)
    """
    The part of the URI before the ``-`` separator.
        That is

            ``<prefix>``

        in `UriInfo.uri`.
    """

    version: Version = field(init=False)
    """
    The version of the URI, the part after the ``-`` parsed with `semantic_version.Version`.
        If there is no version number, this will be 0.0.0. This is

            ``<version>``

    in `UriInfo.uri`.
    """

    pattern: str = field(init=False)
    """
    The generalized regex pattern for this URI:
        ``<prefix>-*``
    """

    search_prefix: str = field(init=False)
    """
    The prefix for searching for related URIs in ASDF
    """

    snake_case: str = field(init=False)
    """
    A snake_case version of the URI prefix for use in class names and attributes.
    """

    camel_case: str = field(init=False)
    """
    A CamelCase version of the URI prefix for use in class names.
    """

    is_tag_uri: bool = field(init=False)
    """
    If the URI is registered as a tag URI in ASDF.
    """

    is_resource_uri: bool = field(init=False)
    """
    If the URI is registered as a resource URI in ASDF.
    """

    def __post_init__(self, uri_type: _uri_type | None):
        prefix, version = self._split_uri(self.exact_uri)
        uri = f"{prefix}-{version}"

        # Set the basic computed fields
        object.__setattr__(self, "uri", uri)
        object.__setattr__(self, "prefix", prefix)
        object.__setattr__(self, "version", Version(version))
        object.__setattr__(self, "pattern", f"{prefix}-*")
        object.__setattr__(self, "search_prefix", f"{prefix}-")
        object.__setattr__(self, "snake_case", self._snake_case())
        object.__setattr__(self, "camel_case", self._camel_case())

        match uri_type:
            case "asdf_tag":
                is_tag_uri = True
                is_resource_uri = False
            case "asdf_resource":
                is_tag_uri = False
                is_resource_uri = True
            case "not_asdf":
                is_tag_uri = False
                is_resource_uri = False
            case None:
                is_tag_uri = self._is_tag_uri()
                is_resource_uri = self._is_resource_uri()
            case _:
                raise ValueError(f"Invalid uri_type '{uri_type}' given for URI '{self.exact_uri}'!")
        object.__setattr__(self, "is_tag_uri", is_tag_uri)
        object.__setattr__(self, "is_resource_uri", is_resource_uri)

    @classmethod
    def _split_uri(cls, uri: str) -> tuple[str, str]:
        """
        Helper method to split the URI into the prefix and version parts
        """
        # If the uri has a "-" divider, then we assume it splits into a prefix and version.
        # Otherwise, we assume we were just given the prefix and the version is 0
        prefix, version = uri.rsplit("-", maxsplit=1) if "-" in uri else (uri, "0")

        return prefix, cls._resolve_version(version)

    @staticmethod
    def _resolve_version(version: str) -> str:
        """
        Helper method to resolve the version string into something that semantic_version can parse
        """

        # If "-" in passed in URI, but nothing after it, then version should be assumed to be 0
        version = version or "0"

        # If there are "*" in the version assume those are 0s
        version = version.replace("*", "0")

        # Turn version into a semantic version string by adding ".0" as needed to make it a major.minor.patch
        # If the version is just a `<non-negative integer>`, then we assume that to be the major version
        #   -> add period to the end
        if fullmatch(r"^[0-9]\d*$", version):
            version = f"{version}."

        # If version is just a `<non-negative integer>.`, then we add "0" to make it a major.minor
        #   -> add "0" to the end
        if fullmatch(r"^[0-9]\d*\.$", version):
            version = f"{version}0"

        # If the version is just a `<non-negative integer>.<non-negative integer>`,
        #   then we assume that to be the major.minor version
        #   -> add period to the end
        if fullmatch(r"^[0-9]\d*\.[0-9]\d*$", version):
            version = f"{version}."

        # If version is just a `<non-negative integer>.<non-negative integer>.`,
        #   then we add "0" to make it a major.minor.patch
        #   -> add "0" to the end
        if fullmatch(r"^[0-9]\d*\.[0-9]\d*\.$", version):
            version = f"{version}0"

        # Check if the version is a semantic version
        if not fullmatch(r"^[0-9]\d*\.[0-9]\d*\.[0-9]\d*$", version):
            raise ValueError(f"Invalid version '{version}' in URI!")

        return version

    def _snake_case(self) -> str:
        """Get a snake_case representation of this URI"""
        name = self.prefix.split("/")[-1]

        # Update the name for the FPS/TVAC cases
        if "/fps/" in self.prefix and "fps" not in name:
            name = f"fps_{name}"
        if "/tvac/" in self.prefix and "tvac" not in name:
            name = f"tvac_{name}"

        # Update the name for reference files
        if "/reference_files/" in self.prefix:
            name = f"{name}_ref"

        return name

    def _camel_case(self) -> str:
        """Get a CamelCase representation of this URI"""
        return "".join([p.capitalize() for p in self.snake_case.split("_")])

    @staticmethod
    @contextmanager
    def _extension_manager() -> Generator[ExtensionManager, None, None]:
        """
        Helper to get the ASDF extension manager
        """
        with AsdfFile() as af:
            yield af.extension_manager

    @staticmethod
    def _tag_def_generator(manager: ExtensionManager) -> Generator[TagDefinition, None, None]:
        """
        Helper generator to yield all of the ASDF tag definitions that correspond to this URI
        """
        extension: Extension
        for extension in manager.extensions:
            yield from extension.tags

    def _is_tag_uri(self) -> bool:
        """
        Helper to determine if a URI is handled as a tag URI by ASDF

            .. note::

                ``alternate_uri`` option is because the first RAD manifest
                does not have a semantic version number at the end of its URI.
        """
        with self._extension_manager() as manager:
            # Short cut when we might have a full URI
            for uri_option in (self.uri, self.exact_uri):
                if manager.handles_tag(uri_option):
                    return True

            # Fall back on manually searching through the tags
            for tag_def in self._tag_def_generator(manager):
                if tag_def.tag_uri.startswith(self.search_prefix):
                    return True

        return False

    def _is_resource_uri(self) -> bool:
        """
        Helper to determine if a URI is handled as a resource URI by ASDF

            .. note::

                This is determining if a URI corresponds to some resource file
                (e.g., schema, manifest, ...) that has been registered with ASDF
        """
        for resource_uri in get_config().resource_manager:
            if resource_uri.startswith(self.search_prefix):
                return True

        return False

    @property
    def is_asdf_uri(self) -> bool:
        """Return True if this URI is registered as either a tag or resource URI in ASDF"""
        return self.is_tag_uri or self.is_resource_uri

    @property
    def resource_uri(self) -> UriInfo:
        """
        Return the resource URI for this URI, which is itself if it is a resource URI
        """
        if self.is_resource_uri:
            return self

        if self.is_tag_uri:
            with self._extension_manager() as manager:
                for uri_option in (self.uri, self.exact_uri):
                    if manager.handles_tag(uri_option):
                        tag_def: TagDefinition = manager.get_tag_definition(uri_option)

                        # It is possible that we have multiple schemas that correspond
                        #    to a registered ASDF tag uri, so we just take the first one
                        return UriInfo(tag_def.schema_uris[0], "asdf_resource")

                raise ValueError(f"URI '{self.uri}' is indicated as a tag URI, but ASDF does not handle it!")

        raise ValueError(f"URI '{self.uri}' is not registered as either a tag or resource URI in ASDF")

    @property
    def tag_uri(self) -> UriInfo:
        """
        Return the tag URI for this URI, which is itself if it is a tag URI
        """
        if self.is_tag_uri:
            return self

        if self.is_resource_uri:
            with self._extension_manager() as manager:
                for tag_def in self._tag_def_generator(manager):
                    if self.uri in tag_def.schema_uris or self.exact_uri in tag_def.schema_uris:
                        return UriInfo(tag_def.tag_uri, "asdf_tag")

                raise ValueError(f"ASDF resource URI '{self.uri}' is not associated with any tag URI in ASDF!")

        raise ValueError(f"URI '{self.uri}' is not registered as either a tag or resource URI in ASDF")

    @property
    def schema(self) -> Any:
        """
        Return the schema URI for this URI, which is the latest version of the prefix
        """
        # Again this is to handle the case for the first RAD manifest
        try:
            return load_schema(self.resource_uri.uri, resolve_references=True)
        except FileNotFoundError:
            return load_schema(self.resource_uri.exact_uri, resolve_references=True)

    @property
    def _latest_tag_uri(self) -> UriInfo:
        """
        Find the latest tag URI for this URI
        """
        latest_tag_uri: UriInfo = self

        with AsdfFile() as af:
            manager: ExtensionManager = af.extension_manager

            extension: Extension
            for extension in manager.extensions:
                tag_def: TagDefinition
                for tag_def in extension.tags:
                    if (
                        tag_def.tag_uri.startswith(self.search_prefix)
                        and (new_tag_uri := UriInfo(tag_def.tag_uri, "asdf_tag")).version > latest_tag_uri.version
                    ):
                        latest_tag_uri = new_tag_uri

        return latest_tag_uri

    @property
    def _latest_resource_uri(self) -> UriInfo:
        """
        Find the latest resource URI for this URI
        """
        latest_resource_uri: UriInfo = self
        for resource_uri in get_config().resource_manager:
            if (
                resource_uri.startswith(self.search_prefix)
                and (new_resource_uri := UriInfo(resource_uri, "asdf_resource")).version > latest_resource_uri.version
            ):
                latest_resource_uri = new_resource_uri

        return latest_resource_uri

    @property
    def latest_uri(self) -> UriInfo:
        """
        Return the info for the latest version of this URI
        """
        if self.is_tag_uri:
            return self._latest_tag_uri

        if self.is_resource_uri:
            return self._latest_resource_uri

        raise ValueError(f"URI '{self.uri}' is not registered as either a tag or resource URI in ASDF")


# TODO: should we deprecate this function in favor of just using UriInfo directly?
@cache
def get_latest_schema(uri: str) -> tuple[str, Any]:
    """
    Get the latest version of a schema by URI (or partial URI).
    """
    latest = UriInfo(uri).latest_uri

    return latest.resource_uri.uri, latest.schema
