from roman_datamodels.stnode import rad

from ...datamodels import ExposureType

__all__ = ["RefExposureTypeRef", "RefExposureTypeRef_Exposure"]


class RefExposureTypeRef_Exposure(rad.ImpliedNodeMixin, rad.ObjectNode):
    @classmethod
    def _asdf_implied_by(cls) -> type:
        return RefExposureTypeRef

    @rad.field
    def type(self) -> ExposureType:
        return ExposureType.WFI_IMAGE

    @rad.field
    def p_exptype(self) -> str:
        return "WFI_IMAGE|WFI_GRISM|WFI_PRISM|"


class RefExposureTypeRef(rad.SchemaObjectNode):
    @classmethod
    def _asdf_schema_uris(self) -> tuple[str]:
        return ("asdf://stsci.edu/datamodels/roman/schemas/reference_files/ref_exposure_type-1.0.0",)

    @rad.field
    def exposure(self) -> RefExposureTypeRef_Exposure:
        return RefExposureTypeRef_Exposure()
