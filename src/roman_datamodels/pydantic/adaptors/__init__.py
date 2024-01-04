"""
This package enables us to use some third party ASDF related types with Pydantic.
"""
import numpy as np
from astropy.units import Unit

from ._adaptor_tags import asdf_tags
from ._astropy_quantity import AstropyQuantity
from ._astropy_time import AstropyTime
from ._astropy_unit import AstropyUnit, Units
from ._base import Adaptor, get_adaptor, is_adaptor
from ._ndarray import NdArray

__all__ = [
    "AstropyTime",
    "AstropyUnit",
    "AstropyQuantity",
    "asdf_tags",
    "NdArray",
    "Units",
    "np",
    "Unit",
    "Adaptor",
    "ADAPTORS",
    "is_adaptor",
    "get_adaptor",
]


# Auto build map from tag key to adaptor name
ADAPTORS = {asdf_tags.get_tag_key(name): name for name, value in locals().items() if is_adaptor(value)}
