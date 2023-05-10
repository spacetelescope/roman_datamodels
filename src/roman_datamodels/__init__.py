# from .util import open
from ._version import version as __version__
from .datamodels import DataModel, get_datamodel

__all__ = ["get_datamodel", "DataModel", "__version__"]
