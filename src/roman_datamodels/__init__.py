# from .util import open
from ._version import version as __version__
from .datamodels import DataModel, open

__all__ = ["DataModel", "__version__", "open"]
