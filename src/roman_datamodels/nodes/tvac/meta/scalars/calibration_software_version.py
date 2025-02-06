from __future__ import annotations

from roman_datamodels.stnode import rad

__all__ = ["TvacCalibrationSoftwareVersion"]


class TvacCalibrationSoftwareVersion(str, rad.TaggedScalarNode):
    @classmethod
    def _asdf_tag_uris(cls) -> dict[str, str]:
        return {
            "asdf://stsci.edu/datamodels/roman/tags/tvac/calibration_software_version-1.0.0": "asdf://stsci.edu/datamodels/roman/schemas/tvac/tagged_scalars/calibration_software_version-1.0.0"
        }

    @classmethod
    def default(cls) -> TvacCalibrationSoftwareVersion:
        return cls("9.9.0")
