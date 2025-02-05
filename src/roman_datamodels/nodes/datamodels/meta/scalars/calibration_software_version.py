from __future__ import annotations

from roman_datamodels.stnode import rad

__all__ = ["CalibrationSoftwareVersion"]


class CalibrationSoftwareVersion(str, rad.TaggedScalarNode):
    @classmethod
    def _asdf_tag_uris(cls) -> dict[str, str]:
        return {
            "asdf://stsci.edu/datamodels/roman/tags/calibration_software_version-1.0.0": "asdf://stsci.edu/datamodels/roman/schemas/tagged_scalars/calibration_software_version-1.0.0"
        }

    @classmethod
    def default(cls) -> CalibrationSoftwareVersion:
        return cls("9.9.0")
