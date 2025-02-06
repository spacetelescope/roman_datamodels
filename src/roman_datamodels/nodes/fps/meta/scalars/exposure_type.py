from roman_datamodels.stnode import rad

__all__ = ["FpsExposureType"]


class FpsExposureType(rad.SchemaStrNodeMixin, rad.RadEnum, metaclass=rad.NodeEnumMeta):
    WFI_IMAGE = "WFI_IMAGE"
    WFI_GRISM = "WFI_GRISM"
    WFI_PRISM = "WFI_PRISM"
    WFI_DARK = "WFI_DARK"
    WFI_FLAT = "WFI_FLAT"
    WFI_WFSC = "WFI_WFSC"

    @classmethod
    def _asdf_schema_uris(self) -> tuple[str]:
        return ("asdf://stsci.edu/datamodels/roman/schemas/fps/exposure_type-1.0.0",)
