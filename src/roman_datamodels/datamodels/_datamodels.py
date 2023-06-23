"""
This module provides all the specific datamodels used by the Roman pipeline.
    These models are what will be read and written by the pipeline to ASDF files.
    Note that we require each model to specify a _node_type, which corresponds to
    the top-level STNode type that the datamodel wraps. This STNode type is derived
    from the schema manifest defined by RAD.
"""

from ._factory import datamodel_factory, datamodel_names

__all__ = []


def _factory(node_type, datamodel_name):
    """
    Wrap the __all__ append and class creation in a function to avoid the linter
        getting upset
    """
    globals()[datamodel_name] = datamodel_factory(node_type, datamodel_name)
    __all__.append(datamodel_name)


for node_type, datamodel_name in datamodel_names():
    _factory(node_type, datamodel_name)
