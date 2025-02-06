from __future__ import annotations

from roman_datamodels.stnode import rad

__all__ = ["FpsSdfSoftwareVersion"]


class FpsSdfSoftwareVersion(str, rad.TaggedScalarNode):
    @classmethod
    def _asdf_tag_uris(cls) -> dict[str, str]:
        return {
            "asdf://stsci.edu/datamodels/roman/tags/fps/sdf_software_version-1.0.0": "asdf://stsci.edu/datamodels/roman/schemas/fps/tagged_scalars/sdf_software_version-1.0.0"
        }

    @classmethod
    def default(cls) -> FpsSdfSoftwareVersion:
        return cls("7.7.7")
