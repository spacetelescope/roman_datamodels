from roman_datamodels.stnode import core, rad

__all__ = ["Resample", "ResampleWeightTypeEntry"]


class ResampleWeightTypeEntry(rad.StrNodeMixin, rad.RadEnum, metaclass=rad.NodeEnumMeta):
    """
    Enum for the possible entries for resample weight type
    """

    EXPTIME = "exptime"
    IVM = "ivm"

    @classmethod
    def _asdf_container(cls) -> type:
        return Resample

    @classmethod
    def _asdf_property_name(cls) -> str:
        return "weight_type"


class Resample(rad.TaggedObjectNode):
    @classmethod
    def _asdf_tag_uris(cls) -> dict[str, str]:
        return {
            "asdf://stsci.edu/datamodels/roman/tags/resample-1.0.0": "asdf://stsci.edu/datamodels/roman/schemas/resample-1.0.0",
        }

    @rad.field
    def good_bits(self) -> str:
        return "NA"

    @rad.field
    def pixel_scale_ratio(self) -> float:
        return rad.NONUM

    @rad.field
    def pixfrac(self) -> float:
        return rad.NONUM

    @rad.field
    def pointings(self) -> int:
        return rad.NOINT

    @rad.field
    def product_exposure_time(self) -> float:
        return rad.NONUM

    @rad.field
    def members(self) -> core.LNode[str]:
        return core.LNode([])

    @rad.field
    def weight_type(self) -> ResampleWeightTypeEntry:
        return ResampleWeightTypeEntry.EXPTIME
