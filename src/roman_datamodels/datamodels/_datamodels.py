"""
This module provides all the specific datamodels used by the Roman pipeline.
    These models are what will be read and written by the pipeline to ASDF files.
    Note that we require each model to specify a _node_type, which corresponds to
    the top-level STNode type that the datamodel wraps. This STNode type is derived
    from the schema manifest defined by RAD.
"""


from roman_datamodels import stnode

from . import _mixins
from ._core import DataModel

__all__ = []


class _DataModel(DataModel):
    """
    Exists only to populate the __all__ for this file automatically
        This is something which is easily missed, but is important for the automatic
        documentation generation to work properly.
    """

    def __init_subclass__(cls, **kwargs):
        """Register each subclass in the __all__ for this module"""
        super().__init_subclass__(**kwargs)
        if cls.__name__ in __all__:
            raise ValueError(f"Duplicate model type {cls.__name__}")

        __all__.append(cls.__name__)


def datamodel_names():
    for tag in stnode._stnode.DATAMODELS_MANIFEST["tags"]:
        schema = stnode._factories.load_schema_from_uri(tag["schema_uri"])
        if "datamodel_name" in schema:
            yield stnode.OBJECT_NODE_CLASSES_BY_TAG[tag["tag_uri"]], schema["datamodel_name"]


def datamodel_factory(node_type, datamodel_name):
    if hasattr(_mixins, mixin := f"{datamodel_name}Mixin"):
        class_type = (_DataModel, getattr(_mixins, mixin))
    else:
        class_type = (_DataModel,)

    cls = type(
        datamodel_name,
        class_type,
        {
            "_node_type": node_type,
            "__module__": "roman_datamodels.datamodels",
            "__doc__": f"Roman {datamodel_name} model",
        },
    )
    globals()[datamodel_name] = cls


for node_type, datamodel_name in datamodel_names():
    datamodel_factory(node_type, datamodel_name)
