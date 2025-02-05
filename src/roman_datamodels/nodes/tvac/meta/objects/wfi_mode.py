from roman_datamodels.stnode import rad

from ....datamodels import InstrumentNameEntry
from ..scalars import (
    TvacWfiDetector,
    TvacWfiOpticalElement,
)

__all__ = ["TvacWfiMode"]


class TvacWfiMode(rad.TaggedObjectNode):
    @classmethod
    def _asdf_tag_uris(cls) -> dict[str, str]:
        return {
            "asdf://stsci.edu/datamodels/roman/tags/tvac/wfi_mode-1.0.0": "asdf://stsci.edu/datamodels/roman/schemas/tvac/wfi_mode-1.0.0"
        }

    @rad.field
    def name(self) -> InstrumentNameEntry:
        return InstrumentNameEntry.WFI

    @rad.field
    def detector(self) -> TvacWfiDetector:
        return TvacWfiDetector.WFI01

    @rad.field
    def optical_element(self) -> TvacWfiOpticalElement:
        return TvacWfiOpticalElement.F158
