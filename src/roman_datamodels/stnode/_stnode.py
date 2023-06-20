"""
Proof of concept of using tags with the data model framework
"""

import importlib.resources

import rad.resources
import yaml
from astropy.time import Time

from . import _mixins
from ._registry import LIST_NODE_CLASSES_BY_TAG, OBJECT_NODE_CLASSES_BY_TAG, SCALAR_NODE_CLASSES_BY_TAG
from ._tagged import TaggedListNode, TaggedObjectNode, TaggedScalarNode, name_from_tag_uri

__all__ = [
    "NODE_CLASSES",
]


SCALAR_TYPE_MAP = {
    "string": str,
    "http://stsci.edu/schemas/asdf/time/time-1.1.0": Time,
}


DATAMODELS_MANIFEST_PATH = importlib.resources.files(rad.resources) / "manifests" / "datamodels-1.0.yaml"
DATAMODELS_MANIFEST = yaml.safe_load(DATAMODELS_MANIFEST_PATH.read_bytes())

BASE_SCHEMA_PATH = importlib.resources.files(rad.resources) / "schemas"


def _load_schema_from_uri(schema_uri):
    filename = f"{schema_uri.split('/')[-1]}.yaml"

    if "reference_files" in schema_uri:
        schema_path = BASE_SCHEMA_PATH / "reference_files" / filename
    elif "tagged_scalars" in schema_uri:
        schema_path = BASE_SCHEMA_PATH / "tagged_scalars" / filename
    else:
        schema_path = BASE_SCHEMA_PATH / filename

    return yaml.safe_load(schema_path.read_bytes())


def _class_name_from_tag_uri(tag_uri):
    tag_name = name_from_tag_uri(tag_uri)
    class_name = "".join([p.capitalize() for p in tag_name.split("_")])
    if tag_uri.startswith("asdf://stsci.edu/datamodels/roman/tags/reference_files/"):
        class_name += "Ref"
    return class_name


def _scalar_class(tag, class_name, docstring):
    schema = _load_schema_from_uri(tag["schema_uri"])

    if "type" in schema:
        type_ = schema["type"]
    elif "allOf" in schema:
        type_ = schema["allOf"][0]["$ref"]
    else:
        raise RuntimeError(f"Unknown schema type: {schema}")

    return type(
        class_name,
        (SCALAR_TYPE_MAP[type_], TaggedScalarNode),
        {"_tag": tag["tag_uri"], "__module__": "roman_datamodels.stnode", "__doc__": docstring},
    )


def _node_class(tag, class_name, docstring):
    schema = _load_schema_from_uri(tag["schema_uri"])

    if schema["type"] == "object":
        class_type = TaggedObjectNode
    elif schema["type"] == "array":
        class_type = TaggedListNode
    else:
        raise RuntimeError(f"Unknown schema type: {schema['type']}")

    if hasattr(_mixins, mixin := f"{class_name}Mixin"):
        class_type = (class_type, getattr(_mixins, mixin))
    else:
        class_type = (class_type,)

    return type(
        class_name,
        class_type,
        {"_tag": tag["tag_uri"], "__module__": "roman_datamodels.stnode", "__doc__": docstring},
    )


def _class_from_tag(tag, docstring):
    class_name = _class_name_from_tag_uri(tag["tag_uri"])

    if "tagged_scalar" in tag["schema_uri"]:
        cls = _scalar_class(tag, class_name, docstring)
    else:
        cls = _node_class(tag, class_name, docstring)

    globals()[class_name] = cls
    __all__.append(class_name)


for tag in DATAMODELS_MANIFEST["tags"]:
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
