from typing import cast

from roman_datamodels.stnode import rad

from .scalars import (
    FpsCalibrationSoftwareVersion,
    FpsFileDate,
    FpsFilename,
    FpsModelType,
    FpsOrigin,
    FpsPrdSoftwareVersion,
    FpsSdfSoftwareVersion,
    FpsTelescope,
)

__all__ = ["FpsBasic"]


class FpsBasic(rad.SchemaObjectNode):
    @classmethod
    def _asdf_schema_uris(cls) -> tuple[str]:
        return ("asdf://stsci.edu/datamodels/roman/schemas/fps/basic-1.0.0",)

    @rad.field
    def calibration_software_version(self) -> FpsCalibrationSoftwareVersion:
        return FpsCalibrationSoftwareVersion.default()

    @rad.field
    def filename(self) -> FpsFilename:
        return FpsFilename.default()

    @rad.field
    def file_date(self) -> FpsFileDate:
        # Astropy has not implemented type hints for Time so MyPy will complain about this
        # until they do.
        return FpsFileDate.default()

    @rad.field
    def model_type(self) -> FpsModelType:
        return cast(FpsModelType, rad.default_model_type(self, FpsModelType))

    @rad.field
    def origin(self) -> FpsOrigin:
        return FpsOrigin.default()

    @rad.field
    def prd_software_version(self) -> FpsPrdSoftwareVersion:
        return FpsPrdSoftwareVersion.default()

    @rad.field
    def sdf_software_version(self) -> FpsSdfSoftwareVersion:
        return FpsSdfSoftwareVersion.default()

    @rad.field
    def telescope(self) -> FpsTelescope:
        return FpsTelescope.default()
