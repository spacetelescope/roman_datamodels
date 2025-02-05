from roman_datamodels.stnode import rad

__all__ = ["RefFile", "RefFile_Crds"]


class RefFile_Crds(rad.ImpliedNodeMixin, rad.ObjectNode):
    @classmethod
    def _asdf_implied_by(cls) -> type:
        return RefFile

    @rad.field
    def version(self) -> str:
        return "12.3.1"

    @rad.field
    def context(self) -> str:
        return "roman_0815.pmap"


class RefFile(rad.TaggedObjectNode):
    @classmethod
    def _asdf_tag_uris(cls) -> dict[str, str]:
        return {
            "asdf://stsci.edu/datamodels/roman/tags/ref_file-1.0.0": "asdf://stsci.edu/datamodels/roman/schemas/ref_file-1.0.0"
        }

    @rad.field
    def crds(self) -> RefFile_Crds:
        return RefFile_Crds()

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
    def inverse_linearity(self) -> str:
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

    @rad.field
    def refpix(self) -> str:
        return "N/A"
