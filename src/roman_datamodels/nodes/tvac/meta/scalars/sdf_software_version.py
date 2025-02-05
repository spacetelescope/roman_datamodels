from __future__ import annotations

from roman_datamodels.stnode import rad

__all__ = ["TvacSdfSoftwareVersion"]


class TvacSdfSoftwareVersion(str, rad.TaggedScalarNode):
    @classmethod
    def _asdf_tag_uris(cls) -> dict[str, str]:
        return {
            "asdf://stsci.edu/datamodels/roman/tags/tvac/sdf_software_version-1.0.0": "asdf://stsci.edu/datamodels/roman/schemas/tvac/tagged_scalars/sdf_software_version-1.0.0"
        }

    @classmethod
    def default(cls) -> TvacSdfSoftwareVersion:
        return cls("7.7.7")
