"""
Factories for creating Tagged STNode classes from tag_uris.
    These are used to dynamically create classes from the RAD manifest.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ._tagged import TaggedListNode, TaggedObjectNode, TaggedScalarNode, class_name_from_tag_uri

if TYPE_CHECKING:
    pass

__all__ = ["stnode_factory"]

# Map of node types by pattern (TaggedObjectNode is default)
_NODE_TYPE_BY_PATTERN = {
    "asdf://stsci.edu/datamodels/roman/tags/cal_logs-*": TaggedListNode,
}


def docstring_from_tag(tag_def: dict[str, Any]) -> str:
    """
    Read the docstring (if it exists) from the RAD manifest and generate a docstring
        for the dynamically generated class.

    Parameters
    ----------
    tag_def: dict
        A tag entry from the RAD manifest

    Returns
    -------
    A docstring for the class based on the tag
    """
    docstring = f"{tag_def['description']}\n\n" if "description" in tag_def else ""

    return docstring + f"Class generated from tag '{tag_def['tag_uri']}'"


def scalar_factory(pattern: str, latest_manifest: str, tag_def: dict[str, Any]) -> type[TaggedScalarNode]:
    """
    Factory to create a TaggedScalarNode class from a tag

    Parameters
    ----------
    pattern: str
        A tag pattern/wildcard

    latest_manifest: str
        URI for the latest manifest

    tag_def: dict
        A tag entry from the RAD manifest

    Returns
    -------
    A dynamically generated TaggedScalarNode subclass
    """

    if pattern in TaggedScalarNode.tag_pattern_map():
        cls = TaggedScalarNode.tag_pattern_map()[pattern]
        cls.__doc__ = docstring_from_tag(tag_def)
        return cls

    return type(
        class_name_from_tag_uri(pattern),
        (str, TaggedScalarNode),
        {
            "_tag_pattern": pattern,
            "_latest_manifest": latest_manifest,
            "_default_tag": tag_def["tag_uri"],
            "__module__": "roman_datamodels._stnode",
            "__doc__": docstring_from_tag(tag_def),
        },
    )


def node_factory(pattern: str, latest_manifest: str, tag_def: dict[str, Any]) -> type[TaggedObjectNode | TaggedListNode]:
    """
    Factory to create a TaggedObjectNode or TaggedListNode class from a tag

    Parameters
    ----------
    pattern: str
        A tag pattern/wildcard

    latest_manifest: str
        URI for the latest manifest

    tag_def: dict
        A tag entry from the RAD manifest

    Returns
    -------
    A dynamically generated TaggedObjectNode or TaggedListNode subclass
    """
    if pattern in TaggedObjectNode.tag_pattern_map():
        cls = TaggedObjectNode.tag_pattern_map()[pattern]
        cls.__doc__ = docstring_from_tag(tag_def)

        # The source catalog nodes are still being updated, so for now
        #    we just set the default tag on the class dynamically here.
        if "source_catalog" in pattern:
            cls._latest_manifest = latest_manifest
            cls._default_tag = tag_def["tag_uri"]

        return cls

    return type(
        class_name_from_tag_uri(pattern),
        (TaggedListNode,) if "cal_logs" in pattern else (TaggedObjectNode,),
        {
            "_tag_pattern": pattern,
            "_latest_manifest": latest_manifest,
            "_default_tag": tag_def["tag_uri"],
            "__module__": "roman_datamodels._stnode",
            "__doc__": docstring_from_tag(tag_def),
            "__slots__": (),
        },
    )


def stnode_factory(
    pattern: str, latest_manifest: str, tag_def: dict[str, Any]
) -> type[TaggedObjectNode | TaggedListNode | TaggedScalarNode]:
    """
    Construct a tagged STNode class from a tag

    Parameters
    ----------
    pattern: str
        A tag pattern/wildcard

    latest_manifest: str
        URI for the latest manifest

    tag_def: dict
        A tag entry from the RAD manifest

    Returns
    -------
    A dynamically generated TaggedScalarNode, TaggedObjectNode, or TaggedListNode subclass
    """
    # TaggedScalarNodes are a special case because they are not a subclass of a
    #   _node class, but rather a subclass of the type of the scalar.
    if "tagged_scalar" in tag_def["schema_uri"]:
        return scalar_factory(pattern, latest_manifest, tag_def)
    else:
        return node_factory(pattern, latest_manifest, tag_def)
