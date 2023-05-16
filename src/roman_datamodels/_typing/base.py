from __future__ import annotations

import sys
from typing import Generic, TypeVar

import astropy.units as u
import numpy as np

if sys.version_info < (3, 10):
    raise ImportError("Python 3.10+ is required to use the typing module features")

# Create type variables for generic types
U = TypeVar("U", bound=u.UnitBase)
A = TypeVar("A", bound=np.ndarray)


class Quantity(Generic[A, U]):
    """
    Generic type for astropy quantities.
        Needed to hold the unit AND the full array information (rank, dtype)
    """

    pass


class Unit(Generic[U]):
    """
    Generic wrapper type for astropy units.
        Needed because there is not a common base class for all astropy units.
    """

    pass
