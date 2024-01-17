"""
This package enables us to use some third party ASDF related types with Pydantic.
"""
__all__ = [
    "AstropyTime",
    "AstropyUnit",
    "AstropyQuantity",
    "NdArray",
    "Units",
    "np",
    "Unit",
    "Adaptor",
    "ADAPTORS",
    "is_adaptor",
    "get_adaptor",
]

import numpy as np
from astropy.units import Unit

from ._astropy_quantity import AstropyQuantity
from ._astropy_time import AstropyTime
from ._astropy_unit import AstropyUnit, Units
from ._base import Adaptor, get_adaptor, is_adaptor
from ._ndarray import NdArray

# Auto build map from tag key to adaptor name
ADAPTORS = {value.tags(): value for value in locals().values() if is_adaptor(value)}
