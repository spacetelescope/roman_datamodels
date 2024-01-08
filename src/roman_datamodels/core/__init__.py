"""
This represents the public interface for the roman_datamodels.core sub-package
"""
__all__ = [
    "BaseDataModel",
    "DataModel",
    "ExtendedDataModel",
    "Archive",
    "open",
]

from ._base import BaseDataModel
from ._extended import ExtendedDataModel
from ._metadata import Archive
from ._model import DataModel
from ._open import rdm_open as open
