"""
Factories for creating Tagged STNode classes from tag_uris.
    These are used to dynamically create classes from the RAD manifest.
"""

from __future__ import annotations

from typing import Any

from ._tagged import (
    TaggedListNode,
    TaggedNode,
    TaggedObjectNode,
    TaggedScalarNode,
    TaggedStrNode,
    TaggedTimeNode,
    class_name_from_tag_uri,
)

__all__ = ("stnode_factory",)

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


def scalar_factory(pattern: str, tag_def: dict[str, Any]) -> type[TaggedScalarNode]:
    """
    Factory to create a TaggedScalarNode class from a tag

    Parameters
    ----------
    pattern: str
        A tag pattern/wildcard

    tag_def: dict
        A tag entry from the RAD manifest

    Returns
    -------
    A dynamically generated TaggedScalarNode subclass
    """

    return type(
        class_name_from_tag_uri(pattern),
        (TaggedTimeNode,) if "file_date" in pattern else (TaggedStrNode,),
        {
            "__module__": "roman_datamodels._stnode",
            "__doc__": docstring_from_tag(tag_def),
        },
    )


def node_factory(pattern: str, tag_def: dict[str, Any]) -> type[TaggedObjectNode | TaggedListNode]:
    """
    Factory to create a TaggedObjectNode or TaggedListNode class from a tag

    Parameters
    ----------
    pattern: str
        A tag pattern/wildcard

    tag_def: dict
        A tag entry from the RAD manifest

    Returns
    -------
    A dynamically generated TaggedObjectNode or TaggedListNode subclass
    """

    return type(
        class_name_from_tag_uri(pattern),
        (TaggedListNode,) if "cal_logs" in pattern else (TaggedObjectNode,),
        {
            "__module__": "roman_datamodels._stnode",
            "__doc__": docstring_from_tag(tag_def),
            "__slots__": (),
        },
    )


def stnode_factory(pattern: str, tag_def: dict[str, Any]) -> type[TaggedNode]:
    """
    Construct a tagged STNode class from a tag

    Parameters
    ----------
    pattern: str
        A tag pattern/wildcard

    tag_def: dict
        A tag entry from the RAD manifest

    Returns
    -------
    A dynamically generated TaggedScalarNode, TaggedObjectNode, or TaggedListNode subclass
    """
    # TaggedScalarNodes are a special case because they are not a subclass of a
    #   _node class, but rather a subclass of the type of the scalar.
    if "tagged_scalar" in tag_def["schema_uri"]:
        return scalar_factory(pattern, tag_def)
    else:
        return node_factory(pattern, tag_def)
