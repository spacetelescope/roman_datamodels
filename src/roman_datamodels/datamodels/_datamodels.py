"""
This module dynamically creates all the DataModels from metadata in RAD.
    - These models are what will be read and written by the pipeline to ASDF files.
    - Note that the DataModels which require additional functionality to the base
      DataModel class will have a Mixin defined. This Mixin contains all the additional
      functionality and is dynamically added to the DataModel class.
    - Unfortunately, this is a dynamic process which occurs at first import time
      because roman_datamodels cannot predict what DataModels will be in the version
      of RAD used by the user.
"""

from ._factory import datamodel_factory, datamodel_names

__all__ = []


def _factory(node_type, datamodel_name):
    """
    Wrap the __all__ append and class creation in a function to avoid the linter
        getting upset
    """
    globals()[datamodel_name] = datamodel_factory(node_type, datamodel_name)  # Add to namespace of module
    __all__.append(datamodel_name)  # add to __all__ so it's imported with `from . import *`


# Main dynamic class creation loop
#   Locates each not_type/datamodel_name pair and creates a DataModel class for it
for node_type, datamodel_name in datamodel_names():
    _factory(node_type, datamodel_name)
