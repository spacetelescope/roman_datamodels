from __future__ import annotations

from typing import Generic, TypeVar

import astropy.units as u
import numpy as np

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
