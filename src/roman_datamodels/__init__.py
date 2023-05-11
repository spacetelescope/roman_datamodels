# from .util import open
from ._version import version as __version__
from .datamodels import DataModel
from .datamodels import roman_open as open

__all__ = ["open", "DataModel", "__version__"]
