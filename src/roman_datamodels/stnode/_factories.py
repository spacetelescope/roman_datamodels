"""
Factories for creating Tagged STNode classes from tag_uris.
    These are used to dynamically create classes from the RAD manifest.
"""

from typing import Any

from astropy.time import Time

from . import _mixins
from ._tagged import TaggedListNode, TaggedObjectNode, TaggedScalarNode, name_from_tag_uri

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


def class_name_from_tag_uri(tag_uri: str) -> str:
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
    tag_name = name_from_tag_uri(tag_uri)
    class_name = "".join([p.capitalize() for p in tag_name.split("_")])
    if tag_uri.startswith("asdf://stsci.edu/datamodels/roman/tags/reference_files/"):
        class_name += "Ref"

    return class_name


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
    class_type = _SCALAR_TYPE_BY_PATTERN.get(pattern, str)

    # In special cases one may need to add additional features to a tagged node class.
    #   This is done by creating a mixin class with the name <ClassName>Mixin in _mixins.py
    #   Here we mixin the mixin class if it exists.
    if hasattr(_mixins, mixin := f"{class_name}Mixin"):
        class_type = (class_type, getattr(_mixins, mixin), TaggedScalarNode)
    else:
        class_type = (class_type, TaggedScalarNode)

    return type(
        class_name,
        class_type,
        {
            "_pattern": pattern,
            "_latest_manifest": latest_manifest,
            "_default_tag": tag_def["tag_uri"],
            "__module__": "roman_datamodels.stnode",
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

    class_type = _NODE_TYPE_BY_PATTERN.get(pattern, TaggedObjectNode)

    # In special cases one may need to add additional features to a tagged node class.
    #   This is done by creating a mixin class with the name <ClassName>Mixin in _mixins.py
    #   Here we mixin the mixin class if it exists.
    if hasattr(_mixins, mixin := f"{class_name}Mixin"):
        class_type = (getattr(_mixins, mixin), class_type)
    else:
        class_type = (class_type,)

    return type(
        class_name,
        class_type,
        {
            "_pattern": pattern,
            "_latest_manifest": latest_manifest,
            "_default_tag": tag_def["tag_uri"],
            "__module__": "roman_datamodels.stnode",
            "__doc__": docstring_from_tag(tag_def),
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
