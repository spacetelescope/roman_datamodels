import numpy as np
from astropy.units import Unit

from ._astropy_quantity import AstropyQuantity
from ._astropy_time import AstropyTime
from ._astropy_unit import AstropyUnit, Units
from ._ndarray import NdArray

__all__ = [
    "AstropyTime",
    "AstropyUnit",
    "AstropyQuantity",
    "NdArray",
    "Units",
    "np",
    "Unit",
    "Adaptor",
]

from typing import Protocol, runtime_checkable


@runtime_checkable
class Adaptor(Protocol):
    @classmethod
    def make_default(cls, **kwargs):
        ...
