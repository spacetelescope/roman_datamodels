import numpy as np
from astropy.units import Unit

from ._adaptor_tags import asdf_tags
from ._astropy_quantity import AstropyQuantity
from ._astropy_time import AstropyTime
from ._astropy_unit import AstropyUnit, Units
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
]

from typing import Protocol, runtime_checkable


def _get_tag_key(value):
    """
    Courtesy of https://stackoverflow.com/a/1176023
    """
    import re

    return re.sub(r"(?<!^)(?=[A-Z])", "_", value).upper()


@runtime_checkable
class Adaptor(Protocol):
    @classmethod
    def make_default(cls, **kwargs):
        ...


ADAPTORS = {
    _get_tag_key(name): name for name, value in locals().items() if value in (AstropyTime, AstropyUnit, AstropyQuantity, NdArray)
}
