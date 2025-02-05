# from .util import open
from ._version import version as __version__
from .datamodels import DataModel, open  # type: ignore[attr-defined]

__all__ = ["DataModel", "__version__", "open"]
