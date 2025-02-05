from typing import cast

from roman_datamodels.stnode import rad

from .scalars import (
    CalibrationSoftwareName,
    CalibrationSoftwareVersion,
    FileDate,
    Filename,
    ModelType,
    Origin,
    PrdVersion,
    ProductType,
    SdfSoftwareVersion,
    Telescope,
)

__all__ = ["Basic"]


class Basic(rad.SchemaObjectNode):
    @classmethod
    def _asdf_schema_uris(cls) -> tuple[str]:
        return ("asdf://stsci.edu/datamodels/roman/schemas/basic-1.0.0",)

    @rad.field
    def calibration_software_name(self) -> CalibrationSoftwareName:
        return CalibrationSoftwareName.default()

    @rad.field
    def calibration_software_version(self) -> CalibrationSoftwareVersion:
        return CalibrationSoftwareVersion.default()

    @rad.field
    def product_type(self) -> ProductType:
        return ProductType.default()

    @rad.field
    def filename(self) -> Filename:
        return Filename.default()

    @rad.field
    def file_date(self) -> FileDate:
        # Astropy has not implemented type hints for Time so MyPy will complain about this
        # until they do.
        return FileDate.default()

    @rad.field
    def model_type(self) -> ModelType:
        return cast(ModelType, rad.default_model_type(self, ModelType))

    @rad.field
    def origin(self) -> Origin:
        return Origin.default()

    @rad.field
    def prd_version(self) -> PrdVersion:
        return PrdVersion.default()

    @rad.field
    def sdf_software_version(self) -> SdfSoftwareVersion:
        return SdfSoftwareVersion.default()

    @rad.field
    def telescope(self) -> Telescope:
        return Telescope.default()
