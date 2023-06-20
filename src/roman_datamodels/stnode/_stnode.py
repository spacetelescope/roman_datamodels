"""
Proof of concept of using tags with the data model framework
"""

import importlib.resources

import rad.resources
import yaml

from ._registry import LIST_NODE_CLASSES_BY_TAG, OBJECT_NODE_CLASSES_BY_TAG, SCALAR_NODE_CLASSES_BY_TAG
from ._tagged import TaggedObjectNode, TaggedScalarNode

__all__ = [
    "NODE_CLASSES",
]


_DATAMODELS_MANIFEST_PATH = importlib.resources.files(rad.resources) / "manifests" / "datamodels-1.0.yaml"
_DATAMODELS_MANIFEST = yaml.safe_load(_DATAMODELS_MANIFEST_PATH.read_bytes())


def _class_name_from_tag_uri(tag_uri):
    tag_name = tag_uri.split("/")[-1].split("-")[0]
    class_name = "".join([p.capitalize() for p in tag_name.split("_")])
    if tag_uri.startswith("asdf://stsci.edu/datamodels/roman/tags/reference_files/"):
        class_name += "Ref"
    return class_name


def _class_from_tag(tag, docstring):
    class_name = _class_name_from_tag_uri(tag["tag_uri"])

    schema_uri = tag["schema_uri"]
    if "tagged_scalar" in schema_uri:
        cls = type(
            class_name,
            (str, TaggedScalarNode),
            {"_tag": tag["tag_uri"], "__module__": "roman_datamodels.stnode", "__doc__": docstring},
        )
    else:
        cls = type(
            class_name,
            (TaggedObjectNode,),
            {"_tag": tag["tag_uri"], "__module__": "roman_datamodels.stnode", "__doc__": docstring},
        )

    globals()[class_name] = cls
    __all__.append(class_name)


for tag in _DATAMODELS_MANIFEST["tags"]:
    docstring = ""
    if "description" in tag:
        docstring = tag["description"] + "\n\n"
    docstring = docstring + f"Class generated from tag '{tag['tag_uri']}'"

    if tag["tag_uri"] in OBJECT_NODE_CLASSES_BY_TAG:
        OBJECT_NODE_CLASSES_BY_TAG[tag["tag_uri"]].__doc__ = docstring
    elif tag["tag_uri"] in LIST_NODE_CLASSES_BY_TAG:
        LIST_NODE_CLASSES_BY_TAG[tag["tag_uri"]].__doc__ = docstring
    elif tag["tag_uri"] in SCALAR_NODE_CLASSES_BY_TAG:
        SCALAR_NODE_CLASSES_BY_TAG[tag["tag_uri"]].__doc__ = docstring
    else:
        _class_from_tag(tag, docstring)


# List of node classes made available by this library.  This is part
# of the public API.
NODE_CLASSES = (
    list(OBJECT_NODE_CLASSES_BY_TAG.values())
    + list(LIST_NODE_CLASSES_BY_TAG.values())
    + list(SCALAR_NODE_CLASSES_BY_TAG.values())
)
