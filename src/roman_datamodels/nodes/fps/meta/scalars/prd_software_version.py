from __future__ import annotations

from roman_datamodels.stnode import rad

__all__ = ["FpsPrdSoftwareVersion"]


class FpsPrdSoftwareVersion(str, rad.TaggedScalarNode):
    @classmethod
    def _asdf_tag_uris(cls) -> dict[str, str]:
        return {
            "asdf://stsci.edu/datamodels/roman/tags/fps/prd_software_version-1.0.0": "asdf://stsci.edu/datamodels/roman/schemas/fps/tagged_scalars/prd_software_version-1.0.0"
        }

    @classmethod
    def default(cls) -> FpsPrdSoftwareVersion:
        return cls("8.8.8")
