"""
Factories for creating all the DataModel classes from RAD
    These are used to dynamically create all the DataModels which are actually used.
"""
from roman_datamodels import stnode

from . import _mixins
from ._core import DataModel


def datamodel_names():
    """
    A generator to grab all the datamodel names and base STNode classes from RAD

    Yields
    ------
        node_type, datamodel_name
    """
    for tag in stnode._stnode.DATAMODELS_MANIFEST["tags"]:
        schema = stnode._factories.load_schema_from_uri(tag["schema_uri"])
        if "datamodel_name" in schema:
            yield stnode.OBJECT_NODE_CLASSES_BY_TAG[tag["tag_uri"]], schema["datamodel_name"]


def datamodel_factory(node_type, datamodel_name):
    """
    The factory for dynamically creating a DataModel class from a node_type and datamodel_name
        Note: For DataModels requiring additional functionality, a Mixin must be added to ._mixins.py
            with the name <datamodel_name>Mixin.

    Parameters
    ----------
    node_type : type
        The base STNode class to use as the base for the DataModel
    datamodel_name : str
        The name of the DataModel to create

    Returns
    -------
    A DataModel object class
    """
    if hasattr(_mixins, mixin := f"{datamodel_name}Mixin"):
        class_type = (getattr(_mixins, mixin), DataModel)
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
