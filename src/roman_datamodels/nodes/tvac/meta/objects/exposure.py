import numpy as np
from astropy.time import Time

from roman_datamodels.stnode import core, rad

from ..scalars import TvacExposureType

__all__ = ["TvacExposure"]


class TvacExposure(rad.TaggedObjectNode):
    @classmethod
    def _asdf_tag_uris(cls) -> dict[str, str]:
        return {
            "asdf://stsci.edu/datamodels/roman/tags/tvac/exposure-1.0.0": "asdf://stsci.edu/datamodels/roman/schemas/tvac/exposure-1.0.0"
        }

    @rad.field
    def type(self) -> TvacExposureType:
        return TvacExposureType.WFI_IMAGE

    @rad.field
    def start_time(self) -> Time:
        # Astropy has not implemented type hints for Time so MyPy will complain about this
        # until they do.
        return Time("2020-01-01T00:00:00.0", format="isot", scale="utc")  # type: ignore[no-untyped-call]

    @rad.field
    def ngroups(self) -> int:
        return 6

    @rad.field
    def nframes(self) -> int:
        return 8

    @rad.field
    def data_problem(self) -> bool:
        return False

    @rad.field
    def frame_divisor(self) -> int:
        return rad.NOINT

    @rad.field
    def groupgap(self) -> int:
        return 0

    @rad.field
    def frame_time(self) -> float:
        return rad.NONUM

    @rad.field
    def group_time(self) -> float:
        return rad.NONUM

    @rad.field
    def exposure_time(self) -> float:
        return rad.NONUM

    @rad.field
    def ma_table_name(self) -> str:
        return rad.NOSTR

    @rad.field
    def ma_table_number(self) -> int:
        return rad.NOINT

    @rad.field
    def read_pattern(self) -> core.LNode[core.LNode[int]]:
        base = np.arange(1, 56).reshape((-1, 1)).tolist()
        return core.LNode([core.LNode(row) for row in base])
