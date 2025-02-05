from roman_datamodels.stnode import rad

from ..scalars import WfiOpticalElement
from .wfi_mode import InstrumentNameEntry

__all__ = ["MosaicBasic"]


class MosaicBasic(rad.TaggedObjectNode):
    @classmethod
    def _asdf_tag_uris(cls) -> dict[str, str]:
        return {
            "asdf://stsci.edu/datamodels/roman/tags/mosaic_basic-1.0.0": "asdf://stsci.edu/datamodels/roman/schemas/mosaic_basic-1.0.0"
        }

    @rad.field
    def time_first_mjd(self) -> float:
        return rad.NONUM

    @rad.field
    def time_last_mjd(self) -> float:
        return rad.NONUM

    @rad.field
    def time_mean_mjd(self) -> float:
        return rad.NONUM

    @rad.field
    def max_exposure_time(self) -> float:
        return rad.NONUM

    @rad.field
    def mean_exposure_time(self) -> float:
        return rad.NONUM

    @rad.field
    def visit(self) -> int:
        return rad.NOINT

    @rad.field
    def segment(self) -> int:
        return rad.NOINT

    @rad.field
    def pass_(self) -> int:
        return rad.NOINT

    @rad.field
    def program(self) -> int:
        return rad.NOINT

    @rad.field
    def survey(self) -> str:
        return rad.NOSTR

    @rad.field
    def optical_element(self) -> WfiOpticalElement:
        return WfiOpticalElement.F158

    @rad.field
    def instrument(self) -> InstrumentNameEntry:
        return InstrumentNameEntry.WFI

    @rad.field
    def location_name(self) -> str:
        return rad.NOSTR

    @rad.field
    def product_type(self) -> str:
        return rad.NOSTR
