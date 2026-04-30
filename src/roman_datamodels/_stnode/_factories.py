"""
Factories for creating Tagged STNode classes from tag_uris.
    These are used to dynamically create classes from the RAD manifest.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from astropy.time import Time

from . import _mixins
from ._tagged import TaggedListNode, TaggedObjectNode, TaggedScalarNode

if TYPE_CHECKING:
    from ._tagged import tagged_type
    from ._uri import UriInfo

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


def scalar_factory(tag_info: UriInfo, latest_manifest: str, tag_def: dict[str, Any]) -> type[TaggedScalarNode]:
    """
    Factory to create a TaggedScalarNode class from a tag

    Parameters
    ----------
    tag_info: UriInfo
        A UriInfo object containing the tag_uri and pattern for the tag

    latest_manifest: str
        URI for the latest manifest

    tag_def: dict
        A tag entry from the RAD manifest

    Returns
    -------
    A dynamically generated TaggedScalarNode subclass
    """
    # TaggedScalarNode subclasses are really subclasses of the type of the scalar,
    #   with the TaggedScalarNode as a mixin.  This is because the TaggedScalarNode
    #   is supposed to be the scalar, but it needs to be serializable under a specific
    #   ASDF tag.
    # _SCALAR_TYPE_BY_PATTERN will need to be updated as new wrappers of scalar types are added
    #   to the RAD manifest.
    # assume everything is a string if not otherwise defined
    class_type = _SCALAR_TYPE_BY_PATTERN.get(tag_info.pattern, str)

    # In special cases one may need to add additional features to a tagged node class.
    #   This is done by creating a mixin class with the name <ClassName>Mixin in _mixins.py
    #   Here we mixin the mixin class if it exists.
    if hasattr(_mixins, mixin := f"{tag_info.camel_case}Mixin"):
        class_type = (class_type, getattr(_mixins, mixin), TaggedScalarNode)
    else:
        class_type = (class_type, TaggedScalarNode)

    return type(
        tag_info.camel_case,
        class_type,
        {
            "_pattern": tag_info.pattern,
            "_latest_manifest": latest_manifest,
            "_default_tag": tag_info.uri,
            "__module__": "roman_datamodels._stnode",
            "__doc__": docstring_from_tag(tag_def),
        },
    )


def node_factory(tag_info: UriInfo, latest_manifest: str, tag_def: dict[str, Any]) -> type[TaggedObjectNode | TaggedListNode]:
    """
    Factory to create a TaggedObjectNode or TaggedListNode class from a tag

    Parameters
    ----------
    tag_info: UriInfo
        A UriInfo object containing the tag_uri and pattern for the tag

    latest_manifest: str
        URI for the latest manifest

    tag_def: dict
        A tag entry from the RAD manifest

    Returns
    -------
    A dynamically generated TaggedObjectNode or TaggedListNode subclass
    """

    base_class_type = _NODE_TYPE_BY_PATTERN.get(tag_info.pattern, TaggedObjectNode)

    # In special cases one may need to add additional features to a tagged node class.
    #   This is done by creating a mixin class with the name <ClassName>Mixin in _mixins.py
    #   Here we mixin the mixin class if it exists.
    class_type: tuple[Any, tagged_type] | tuple[tagged_type]
    if hasattr(_mixins, mixin := f"{tag_info.camel_case}Mixin"):
        class_type = (getattr(_mixins, mixin), base_class_type)
    else:
        class_type = (base_class_type,)

    return type(
        tag_info.camel_case,
        class_type,
        {
            "_pattern": tag_info.pattern,
            "_latest_manifest": latest_manifest,
            "_default_tag": tag_info.uri,
            "__module__": "roman_datamodels._stnode",
            "__doc__": docstring_from_tag(tag_def),
            "__slots__": (),
        },
    )


def stnode_factory(
    tag_info: UriInfo, latest_manifest: str, tag_def: dict[str, Any]
) -> type[TaggedObjectNode | TaggedListNode | TaggedScalarNode]:
    """
    Construct a tagged STNode class from a tag

    Parameters
    ----------
    tag_info: UriInfo
        A UriInfo object containing the tag_uri and pattern for the tag

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
        return scalar_factory(tag_info, latest_manifest, tag_def)
    else:
        return node_factory(tag_info, latest_manifest, tag_def)
