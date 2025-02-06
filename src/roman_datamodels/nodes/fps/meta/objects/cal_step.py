from roman_datamodels.stnode import rad

from ....datamodels import CalStepEntry

__all__ = ["FpsCalStep"]


class FpsCalStep(rad.TaggedObjectNode):
    @classmethod
    def _asdf_tag_uris(cls) -> dict[str, str]:
        return {
            "asdf://stsci.edu/datamodels/roman/tags/fps/cal_step-1.0.0": "asdf://stsci.edu/datamodels/roman/schemas/fps/cal_step-1.0.0"
        }

    @rad.field
    def assign_wcs(self) -> CalStepEntry:
        return CalStepEntry.INCOMPLETE

    @rad.field
    def flat_field(self) -> CalStepEntry:
        return CalStepEntry.INCOMPLETE

    @rad.field
    def dark(self) -> CalStepEntry:
        return CalStepEntry.INCOMPLETE

    @rad.field
    def dq_init(self) -> CalStepEntry:
        return CalStepEntry.INCOMPLETE

    @rad.field
    def flux(self) -> CalStepEntry:
        return CalStepEntry.INCOMPLETE

    @rad.field
    def jump(self) -> CalStepEntry:
        return CalStepEntry.INCOMPLETE

    @rad.field
    def linearity(self) -> CalStepEntry:
        return CalStepEntry.INCOMPLETE

    @rad.field
    def photom(self) -> CalStepEntry:
        return CalStepEntry.INCOMPLETE

    @rad.field
    def source_detection(self) -> CalStepEntry:
        return CalStepEntry.INCOMPLETE

    @rad.field
    def ramp_fit(self) -> CalStepEntry:
        return CalStepEntry.INCOMPLETE

    @rad.field
    def refpix(self) -> CalStepEntry:
        return CalStepEntry.INCOMPLETE

    @rad.field
    def saturation(self) -> CalStepEntry:
        return CalStepEntry.INCOMPLETE

    @rad.field
    def outlier_detection(self) -> CalStepEntry:
        return CalStepEntry.INCOMPLETE

    @rad.field
    def tweakreg(self) -> CalStepEntry:
        return CalStepEntry.INCOMPLETE

    @rad.field
    def skymatch(self) -> CalStepEntry:
        return CalStepEntry.INCOMPLETE
