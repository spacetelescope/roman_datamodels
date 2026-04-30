"""
Factories for creating Tagged STNode classes from tag_uris.
    These are used to dynamically create classes from the RAD manifest.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from astropy.time import Time

from ._mixins import BaseForMixin
from ._tagged import TaggedListNode, TaggedObjectNode, TaggedScalarNode, class_name_from_tag_uri

if TYPE_CHECKING:
    pass

__all__ = ["stnode_factory"]

# Map of scalar types by pattern (str is default)
_SCALAR_TYPE_BY_PATTERN = {
    "asdf://stsci.edu/datamodels/roman/tags/file_date-*": Time,
    "asdf://stsci.edu/datamodels/roman/tags/fps/file_date-*": Time,
    "asdf://stsci.edu/datamodels/roman/tags/tvac/file_date-*": Time,
}
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
    class_name = class_name_from_tag_uri(pattern)

    # TaggedScalarNode subclasses are really subclasses of the type of the scalar,
    #   with the TaggedScalarNode as a mixin.  This is because the TaggedScalarNode
    #   is supposed to be the scalar, but it needs to be serializable under a specific
    #   ASDF tag.
    # _SCALAR_TYPE_BY_PATTERN will need to be updated as new wrappers of scalar types are added
    #   to the RAD manifest.
    # assume everything is a string if not otherwise defined
    scalar_type = _SCALAR_TYPE_BY_PATTERN.get(pattern, str)

    # In special cases one may need to add additional features to a tagged node class.
    #   This is done by creating a mixin class with the name <ClassName>Mixin in _mixins.py
    #   Here we mixin the mixin class if it exists.
    class_type: (
        tuple[type[str | Time], type[BaseForMixin], type[TaggedScalarNode]] | tuple[type[str | Time], type[TaggedScalarNode]]
    )
    if pattern in BaseForMixin.tag_pattern_map():
        class_type = (scalar_type, BaseForMixin.tag_pattern_map()[pattern], TaggedScalarNode)
    else:
        class_type = (scalar_type, TaggedScalarNode)

    return type(
        class_name,
        class_type,
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
    class_name = class_name_from_tag_uri(pattern)

    base_class_type = _NODE_TYPE_BY_PATTERN.get(pattern, TaggedObjectNode)

    # In special cases one may need to add additional features to a tagged node class.
    #   This is done by creating a mixin class with the name <ClassName>Mixin in _mixins.py
    #   Here we mixin the mixin class if it exists.
    class_type: (
        tuple[type[BaseForMixin], type[TaggedObjectNode | TaggedListNode]] | tuple[type[TaggedObjectNode | TaggedListNode]]
    )
    if pattern in BaseForMixin.tag_pattern_map():
        class_type = (BaseForMixin.tag_pattern_map()[pattern], base_class_type)
    else:
        class_type = (base_class_type,)

    return type(
        class_name,
        class_type,
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
