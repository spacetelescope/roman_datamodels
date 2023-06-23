from roman_datamodels import stnode

from . import _mixins
from ._core import DataModel


def datamodel_names():
    for tag in stnode._stnode.DATAMODELS_MANIFEST["tags"]:
        schema = stnode._factories.load_schema_from_uri(tag["schema_uri"])
        if "datamodel_name" in schema:
            yield stnode.OBJECT_NODE_CLASSES_BY_TAG[tag["tag_uri"]], schema["datamodel_name"]


def datamodel_factory(node_type, datamodel_name):
    if hasattr(_mixins, mixin := f"{datamodel_name}Mixin"):
        class_type = (DataModel, getattr(_mixins, mixin))
    else:
        class_type = (DataModel,)

    return type(
        datamodel_name,
        class_type,
        {
            "_node_type": node_type,
            "__module__": "roman_datamodels.datamodels",
            "__doc__": f"Roman {datamodel_name} model",
        },
    )
