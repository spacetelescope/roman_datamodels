from typing import Any

from roman_datamodels.stnode import core, rad

from .basic import TvacBasic
from .objects import (
    TvacCalStep,
    TvacExposure,
    TvacGuidestar,
    TvacRefFile,
    TvacStatistics,
    TvacWfiMode,
)

__all__ = ["TvacCommon", "TvacCommonMixin"]


class TvacCommonMixin(rad.ExtraFieldsMixin):
    """Mixin things present in the constructors not present in the schema"""

    @rad.field
    def statistics(self) -> TvacStatistics:
        return TvacStatistics()


class TvacCommon(TvacCommonMixin, TvacBasic):
    @classmethod
    def _asdf_schema_uris(self) -> tuple[str]:
        return ("asdf://stsci.edu/datamodels/roman/schemas/tvac/common-1.0.0",)

    @rad.field
    def cal_step(self) -> TvacCalStep:
        return TvacCalStep()

    @rad.field
    def exposure(self) -> TvacExposure:
        return TvacExposure()

    @rad.field
    def guidestar(self) -> TvacGuidestar:
        return TvacGuidestar()

    @rad.field
    def instrument(self) -> TvacWfiMode:
        return TvacWfiMode()

    @rad.field
    def ref_file(self) -> TvacRefFile:
        return TvacRefFile()

    @rad.field
    def hdf5_meta(self) -> core.DNode[Any]:
        return core.DNode({"test": rad.NOSTR})

    @rad.field
    def hdf5_telemetry(self) -> str:
        return rad.NOSTR

    @rad.field
    def gw_meta(self) -> core.DNode[Any]:
        return core.DNode({"test": rad.NOSTR})
