from roman_datamodels.stnode import rad

from .l2_cal_step import CalStepEntry, L2CalStep

__all__ = ["L3CalStep"]


class L3CalStep(rad.TaggedObjectNode):
    @classmethod
    def _asdf_tag_uris(cls) -> dict[str, str]:
        return {
            "asdf://stsci.edu/datamodels/roman/tags/l3_cal_step-1.0.0": "asdf://stsci.edu/datamodels/roman/schemas/l3_cal_step-1.0.0"
        }

    # NOTE: I am not using __future__ annotations here because that changes
    #       how to infer the types to wrap values into nodes.
    @classmethod
    def from_l2(cls, l2: L2CalStep) -> "L3CalStep":
        """
        Construct a L3CalStep from a L2CalStep

        Parameters
        ----------
        l2
            The L2CalStep to pull parameters from
        """
        new = cls()
        for field in new.fields:
            if field in l2.fields:
                setattr(new, field, getattr(l2, field))

        return new

    @rad.field
    def flux(self) -> CalStepEntry:
        return CalStepEntry.INCOMPLETE

    @rad.field
    def outlier_detection(self) -> CalStepEntry:
        return CalStepEntry.INCOMPLETE

    @rad.field
    def skymatch(self) -> CalStepEntry:
        return CalStepEntry.INCOMPLETE

    @rad.field
    def resample(self) -> CalStepEntry:
        return CalStepEntry.INCOMPLETE
