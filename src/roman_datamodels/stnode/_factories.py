"""
Factories for creating Tagged STNode classes from tag_uris.
    These are used to dynamically create classes from the RAD manifest.
"""

import importlib.resources

from astropy.time import Time
from rad import resources

from . import _mixins
from ._tagged import TaggedListNode, TaggedObjectNode, TaggedScalarNode, name_from_tag_uri

__all__ = ["stnode_factory"]

# Map of scalar types by pattern (str is default)
_SCALAR_TYPE_BY_PATTERN = {
    "asdf://stsci.edu/datamodels/roman/tags/file_date-*": Time,
    "asdf://stsci.edu/datamodels/roman/tags/fps/file_date-": Time,
    "asdf://stsci.edu/datamodels/roman/tags/tvac/file_date-": Time,
}
# Map of node types by pattern (TaggedObjectNode is default)
_NODE_TYPE_BY_PATTERN = {
    "asdf://stsci.edu/datamodels/roman/tags/cal_logs-*": TaggedListNode,
}

_SCALAR_TAG_BASES = {
    "calibration_software_name",
    "calibration_software_version",
    "product_type",
    "filename",
    "file_date",
    "model_type",
    "origin",
    "prd_version",
    "sdf_software_version",
    "telescope",
    "prd_software_version",  # for tvac and fps
}

BASE_SCHEMA_PATH = importlib.resources.files(resources) / "schemas"


def is_tagged_scalar_pattern(pattern):
    tag_base = pattern.rsplit("-", maxsplit=1)[0].rsplit("/", maxsplit=1)[1]
    return tag_base in _SCALAR_TAG_BASES


def class_name_from_tag_uri(tag_uri):
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


def docstring_from_tag(pattern):
    """
    Read the docstring (if it exists) from the RAD manifest and generate a docstring
        for the dynamically generated class.

    Parameters
    ----------
    tag: dict
        A tag entry from the RAD manifest

    Returns
    -------
    A docstring for the class based on the tag
    """
    # TODO broken for now
    # docstring = f"{tag['description']}\n\n" if "description" in tag else ""

    # return docstring + f"Class generated from tag '{tag['tag_uri']}'"
    return f"Class generated from tag '{pattern}'"


def scalar_factory(pattern):
    """
    Factory to create a TaggedScalarNode class from a tag

    Parameters
    ----------
    tag: dict
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
    type_ = _SCALAR_TYPE_BY_PATTERN.get(pattern, str)

    return type(
        class_name,
        (type_, TaggedScalarNode),
        {"_tag": pattern, "__module__": "roman_datamodels.stnode", "__doc__": docstring_from_tag(pattern)},
    )


def node_factory(pattern):
    """
    Factory to create a TaggedObjectNode or TaggedListNode class from a tag

    Parameters
    ----------
    tag: dict
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
        class_type = (class_type, getattr(_mixins, mixin))
    else:
        class_type = (class_type,)

    return type(
        class_name,
        class_type,
        {"_tag": pattern, "__module__": "roman_datamodels.stnode", "__doc__": docstring_from_tag(pattern)},
    )


def stnode_factory(pattern):
    """
    Construct a tagged STNode class from a tag

    Parameters
    ----------
    tag: dict
        A tag entry from the RAD manifest

    Returns
    -------
    A dynamically generated TaggedScalarNode, TaggedObjectNode, or TaggedListNode subclass
    """
    # TaggedScalarNodes are a special case because they are not a subclass of a
    #   _node class, but rather a subclass of the type of the scalar.
    if is_tagged_scalar_pattern(pattern):
        return scalar_factory(pattern)
    else:
        return node_factory(pattern)
