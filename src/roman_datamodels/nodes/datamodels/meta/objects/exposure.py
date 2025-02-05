from astropy.time import Time

from roman_datamodels.stnode import core, rad

from ..scalars import ExposureType

__all__ = ["Exposure"]


class Exposure(rad.TaggedObjectNode):
    @classmethod
    def _asdf_tag_uris(cls) -> dict[str, str]:
        return {
            "asdf://stsci.edu/datamodels/roman/tags/exposure-1.0.0": "asdf://stsci.edu/datamodels/roman/schemas/exposure-1.0.0"
        }

    @rad.field
    def type(self) -> ExposureType:
        return ExposureType.WFI_IMAGE

    @rad.field
    def start_time(self) -> Time:
        # Astropy has not implemented type hints for Time so MyPy will complain about this
        # until they do.
        return Time("2020-01-01T00:00:00.0", format="isot", scale="utc")  # type: ignore[no-untyped-call]

    @rad.field
    def mid_time(self) -> Time:
        # Astropy has not implemented type hints for Time so MyPy will complain about this
        # until they do.
        return Time("2020-01-01T01:00:00.0", format="isot", scale="utc")  # type: ignore[no-untyped-call]

    @rad.field
    def end_time(self) -> Time:
        # Astropy has not implemented type hints for Time so MyPy will complain about this
        # until they do.
        return Time("2020-01-01T02:00:00.0", format="isot", scale="utc")  # type: ignore[no-untyped-call]

    @rad.field
    def nresultants(self) -> int:
        return 6

    @rad.field
    def data_problem(self) -> bool:
        return False

    @rad.field
    def frame_time(self) -> float:
        return rad.NONUM

    @rad.field
    def exposure_time(self) -> float:
        return rad.NONUM

    @rad.field
    def effective_exposure_time(self) -> float:
        return rad.NONUM

    @rad.field
    def ma_table_name(self) -> str:
        return rad.NOSTR

    @rad.field
    def ma_table_number(self) -> int:
        return rad.NOINT

    @rad.field
    def read_pattern(self) -> core.LNode[core.LNode[int]]:
        return core.LNode([core.LNode(read) for read in ([1], [2, 3], [4], [5, 6, 7, 8], [9, 10], [11])])

    @rad.field
    def truncated(self) -> bool:
        return False
