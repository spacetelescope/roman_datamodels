from typing import cast

import numpy as np
from astropy.units import DN, Quantity, s  # type: ignore[attr-defined]

from roman_datamodels.stnode import rad

__all__ = ["TvacStatistics"]


class TvacStatistics(rad.TaggedObjectNode):
    @classmethod
    def _asdf_tag_uris(cls) -> dict[str, str]:
        return {
            "asdf://stsci.edu/datamodels/roman/tags/tvac/statistics-1.0.0": "asdf://stsci.edu/datamodels/roman/schemas/tvac/statistics-1.0.0"
        }

    @rad.field
    def mean_counts_per_sec(self) -> Quantity | None:
        return cast(Quantity, rad.NONUM * (DN / s))

    @rad.field
    def median_counts_per_sec(self) -> Quantity | None:
        return cast(Quantity, rad.NONUM * (DN / s))

    @rad.field
    def max_counts(self) -> Quantity | None:
        return Quantity(rad.NONUM, DN, dtype=np.int32)

    @rad.field
    def min_counts(self) -> Quantity | None:
        return Quantity(rad.NONUM, DN, dtype=np.int32)
