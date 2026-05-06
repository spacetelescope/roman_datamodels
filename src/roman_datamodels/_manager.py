from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import TYPE_CHECKING, ClassVar, TypedDict

from asdf import get_config
from asdf.schema import load_schema

from ._stnode import (
    ManifestNode,
    TaggedListNode,
    TaggedNode,
    TaggedObjectNode,
    TaggedStrNode,
    TaggedTimeNode,
    get_version,
)

if TYPE_CHECKING:
    from semantic_version import Version


class _TagDef(TypedDict):
    tag_uri: str
    schema_uri: str


class _ManifestDef(TypedDict):
    id: str
    tags: list[_TagDef]


@dataclass(frozen=True, slots=True, kw_only=True)
class Manager:
    """
    A dataclass to manage the relationships between the various tag uris and their
    associated manifests

    Notes
    -----
    - This class is constructed as a singleton since we should only ever need to
        compute these relationships once (at import time).
    - This class is frozen to prevent accidental overwriting of the maps after they
        are created at import time.
    - The maps are all MappingProxyTypes to prevent accidental modification of
        any elements after creation.
    """

    _instance: ClassVar[Manager | None] = None
    _manifest_prefix: ClassVar[str] = "asdf://stsci.edu/datamodels/roman/manifests/datamodels-"

    # This turns the Manager class into a singleton
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            # Avoid issues with inheritance and the dataclass __new__ method by
            #   directly calling it
            cls._instance = super(Manager, cls).__new__(cls, *args, **kwargs)

        return cls._instance

    # These are the pre-computed maps that we will carefully save at the end of
    #    the __post_init__ method.
    manifests: MappingProxyType[str, type[ManifestNode]] = field(init=False)
    """A mapping between the manifest URI and the ManifestNode class that manages it"""

    tags: MappingProxyType[str, type[ManifestNode]] = field(init=False)
    """A mapping between the tag URI and the ManifestNode class that manages it"""

    def __post_init__(self) -> None:
        # To allow for the ManifestManager's singleton instance to be accessible
        #    via ManifestNode() we need to add a small protection to avoid
        #    computing all of these maps as __post_init__ is called on a dataclass
        #    after __new__. We simply check if one of the maps is an attribute,
        #    as field(init=False) does not even add the attribute before it's meant
        #    to be set in __post_init__.
        if hasattr(self, "manifests"):  # --> already computed if true
            return

        # Set of mutable maps
        manifests: dict[str, type[ManifestNode]] = {}
        tags: dict[str, type[ManifestNode]] = {}

        # Start computing the maps from the resources that RAD has registered
        #   with ASDF.
        # We index them by their semantic version number so we can order them
        manifest_map: dict[Version, str] = {
            get_version(uri): uri for uri in get_config().resource_manager if uri.startswith(self._manifest_prefix)
        }

        # We go in reverse order (latest to earliest) so that a tag is handled
        #    by the latest manifest that records it.
        for version in sorted(manifest_map, reverse=True):
            manifest: _ManifestDef = load_schema(manifest_map[version])
            manifest_uri = manifest["id"]

            # Start a map of the tags for the current manifest being processed
            tag_uris: dict[str, type[TaggedNode]] = {}

            for tag_def in manifest["tags"]:
                # Only add a tag to the ones managed by this manifest if it hasn't already been
                #    assigned to an earlier manifest.
                if (tag_uri := tag_def["tag_uri"]) not in tags:
                    # tag_uris[tag_uri] = self._select_tagged_type(tag_uri, tag_def["schema_uri"])
                    tag_uris[tag_uri] = self._select_tagged_type(tag_uri, tag_def)

            # Update the maps with the newly computed information
            manifests[manifest_uri] = ManifestNode.factory(manifest_uri, MappingProxyType(tag_uris))
            tags.update(dict.fromkeys(tag_uris, manifests[manifest_uri]))

        # Finally, turn all the mutable fields into immutable versions and assign
        #   them carefully to the instance using object.__setattr__ as this is a
        #   frozen dataclass.
        super().__setattr__("manifests", MappingProxyType(manifests))
        super().__setattr__("tags", MappingProxyType(tags))

    @staticmethod
    def _select_tagged_type(tag_uri: str, tag_def: _TagDef) -> type[TaggedNode]:
        """
        A helper function to select the appropriate TaggedNode subclass based on the
            the uris from the tag definition
        """
        from ._stnode._factories import class_name_from_tag_uri, docstring_from_tag

        pattern = f"{tag_uri.rsplit('-', 1)[0]}-*"

        if "tagged_scalar" in tag_def["schema_uri"]:
            return type(
                class_name_from_tag_uri(pattern),
                (TaggedTimeNode,) if "file_date" in pattern else (TaggedStrNode,),
                {
                    "__module__": "roman_datamodels._stnode",
                    "__doc__": docstring_from_tag(tag_def),  # type: ignore[arg-type]
                },
            )

        return type(
            class_name_from_tag_uri(pattern),
            (TaggedListNode,) if "cal_logs" in pattern else (TaggedObjectNode,),
            {
                "__module__": "roman_datamodels._stnode",
                "__doc__": docstring_from_tag(tag_def),  # type: ignore[arg-type]
                "__slots__": (),
            },
        )

    # TODO: Below is an implementation of the _select_tagged_type when the nodes are not dynamic classes
    # @staticmethod
    # def _select_tagged_type(tag_uri: str, schema_uri: str) -> type[TaggedNode]:
    #     """
    #     A helper function to select the appropriate TaggedNode subclass based on the
    #         the uris from the tag definition

    #     Notes
    #     -----
    #     - This is for legacy support as post datamodels-1.4.0 manifest all tags
    #         should only be TaggedObjectNodes
    #     """
    #     if "tagged_scalar" in schema_uri:
    #         return TaggedTimeNode if "file_date" in tag_uri else TaggedStrNode

    #     if "cal_logs" in tag_uri:
    #         return TaggedListNode

    #     return TaggedObjectNode

    def get_node_class(self, tag_uri: str) -> type[TaggedNode] | None:
        """
        Get the TaggedNode class that manages the given tag URI, or None if it is not
            registered in any manifest.
        """
        if (node := self.tags.get(tag_uri)) is None:
            return None

        return node.tag_uris[tag_uri]


# # Go ahead and build the singleton instance for the first time so that it's available
# #    and no one can mess with maps by accident during other imports
# _ = Manager()
