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
from .datamodels import DataModel

if TYPE_CHECKING:
    from semantic_version import Version


class _TagDef(TypedDict):
    tag_uri: str
    schema_uri: str
    description: str | None


class _ManifestDef(TypedDict):
    id: str
    tags: list[_TagDef]


def _docstring_from_tag(tag_def: _TagDef) -> str:
    """
    Read the docstring (if it exists) from the RAD manifest and generate a docstring
        for the dynamically generated class.

    Parameters
    ----------
    tag_def: _TagDef
        A tag entry from the RAD manifest

    Returns
    -------
    A docstring for the class based on the tag
    """
    docstring = f"{tag_def['description']}\n\n" if "description" in tag_def else ""

    return docstring + f"Class generated from tag '{tag_def['tag_uri']}'"


def _name_from_tag_uri(tag_uri: str) -> str:
    """
    Compute the name of the schema from the tag_uri.

    Parameters
    ----------
    tag_uri : str
        The tag_uri to find the name from
    """
    tag_uri_split = tag_uri.split("/")[-1].split("-")[0]
    if "/tvac/" in tag_uri and "tvac" not in tag_uri_split:
        tag_uri_split = "tvac_" + tag_uri.split("/")[-1].split("-")[0]
    elif "/fps/" in tag_uri and "fps" not in tag_uri_split:
        tag_uri_split = "fps_" + tag_uri.split("/")[-1].split("-")[0]
    return tag_uri_split


def _class_name_from_tag_uri(tag_uri: str) -> str:
    """
    Construct the class name for the STNode class from the tag_uri

    Parameters
    ----------
    tag_uri : str
        The tag_uri found in the RAD manifest

    Returns
    -------
    string name for the class
    """
    tag_name = _name_from_tag_uri(tag_uri)
    class_name = "".join([p.capitalize() for p in tag_name.split("_")])
    if tag_uri.startswith("asdf://stsci.edu/datamodels/roman/tags/reference_files/"):
        class_name += "Ref"

    return class_name


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

    patterns: MappingProxyType[str, type[TaggedNode]] = field(init=False)
    """A mapping between the tag URI pattern and the TaggedNode class that manages it"""

    data_models: MappingProxyType[str, type[DataModel]] = field(init=False)
    """A mapping between tag patterns and the DataModel class that wraps nodes following those patterns"""

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
        patterns: dict[str, type[TaggedNode]] = {}

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
                pattern = f"{tag_def['tag_uri'].rsplit('-', 1)[0]}-*"
                if pattern not in patterns:
                    patterns[pattern] = self._select_tagged_type(tag_def["tag_uri"], tag_def["schema_uri"])

                # Only add a tag to the ones managed by this manifest if it hasn't already been
                #    assigned to an earlier manifest.
                if (tag_uri := tag_def["tag_uri"]) not in tags:
                    tag_uris[tag_uri] = patterns[pattern]

            # Update the maps with the newly computed information
            manifests[manifest_uri] = ManifestNode.factory(manifest_uri, tag_uris)
            tags.update(dict.fromkeys(tag_uris, manifests[manifest_uri]))

        # Finally, turn all the mutable fields into immutable versions and assign
        #   them carefully to the instance using object.__setattr__ as this is a
        #   frozen dataclass.
        object.__setattr__(self, "manifests", MappingProxyType(manifests))
        object.__setattr__(self, "tags", MappingProxyType(tags))
        object.__setattr__(self, "patterns", MappingProxyType(patterns))

        object.__setattr__(
            self,
            "data_models",
            MappingProxyType({cls.tag_pattern: cls for cls in DataModel.__subclasses__() if hasattr(cls, "tag_pattern")}),
        )

        super().__setattr__(
            "data_models",
            MappingProxyType({cls.tag_pattern: cls for cls in DataModel.__subclasses__() if hasattr(cls, "tag_pattern")}),
        )

    @staticmethod
    def _select_tagged_type(tag_uri: str, schema_uri: str) -> type[TaggedNode]:
        """
        A helper function to select the appropriate TaggedNode subclass based on the
            the uris from the tag definition

        Notes
        -----
        - This is for legacy support as post datamodels-1.4.0 manifest all tags
            should only be TaggedObjectNodes
        """
        if "tagged_scalar" in schema_uri:
            return TaggedTimeNode if "file_date" in tag_uri else TaggedStrNode

        if "cal_logs" in tag_uri:
            return TaggedListNode

        return TaggedObjectNode

    def get_node_class(self, tag_uri: str) -> type[TaggedNode] | None:
        """
        Get the TaggedNode class that manages the given tag URI, or None if it is not
            registered in any manifest.
        """
        if (node := self.tags.get(tag_uri)) is None:
            return None

        return node.tag_uris[tag_uri]

    def get_data_model(self, tag_uri: str) -> type[DataModel] | None:
        """
        Get the DataModel class that manages the given tag URI, or None if it is not
            registered in any manifest.

        Parameters
        ----------
        tag_uri: str
            The tag URI to get the DataModel class for.

        Returns
        -------
        type[DataModel] | None
            The DataModel class that manages the given tag URI, or None if it is not
            associated with any DataModel.
        """
        return self.data_models.get(f"{tag_uri.rsplit('-', 1)[0]}-*")


# Go ahead and build the singleton instance for the first time so that it's available
#    and no one can mess with maps by accident during other imports
_ = Manager()
