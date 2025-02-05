from roman_datamodels.stnode import rad

__all__ = ["TvacRefFile", "TvacRefFile_Crds"]


class TvacRefFile_Crds(rad.ImpliedNodeMixin, rad.ObjectNode):
    @classmethod
    def _asdf_implied_by(cls) -> type:
        return TvacRefFile

    @rad.field
    def sw_version(self) -> str:
        return "12.3.1"

    @rad.field
    def context_used(self) -> str:
        return "roman_0815.pmap"


class TvacRefFile(rad.TaggedObjectNode):
    @classmethod
    def _asdf_tag_uris(cls) -> dict[str, str]:
        return {
            "asdf://stsci.edu/datamodels/roman/tags/tvac/ref_file-1.0.0": "asdf://stsci.edu/datamodels/roman/schemas/tvac/ref_file-1.0.0"
        }

    @rad.field
    def crds(self) -> TvacRefFile_Crds:
        return TvacRefFile_Crds()

    @rad.field
    def dark(self) -> str:
        return "N/A"

    @rad.field
    def distortion(self) -> str:
        return "N/A"

    @rad.field
    def mask(self) -> str:
        return "N/A"

    @rad.field
    def flat(self) -> str:
        return "N/A"

    @rad.field
    def gain(self) -> str:
        return "N/A"

    @rad.field
    def readnoise(self) -> str:
        return "N/A"

    @rad.field
    def linearity(self) -> str:
        return "N/A"

    @rad.field
    def photom(self) -> str:
        return "N/A"

    @rad.field
    def area(self) -> str:
        return "N/A"

    @rad.field
    def saturation(self) -> str:
        return "N/A"
