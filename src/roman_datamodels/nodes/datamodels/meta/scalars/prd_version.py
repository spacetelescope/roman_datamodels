from __future__ import annotations

from roman_datamodels.stnode import rad

__all__ = ["PrdVersion"]


class PrdVersion(str, rad.TaggedScalarNode):
    @classmethod
    def _asdf_tag_uris(cls) -> dict[str, str]:
        return {
            "asdf://stsci.edu/datamodels/roman/tags/prd_version-1.0.0": "asdf://stsci.edu/datamodels/roman/schemas/tagged_scalars/prd_version-1.0.0"
        }

    @classmethod
    def default(cls) -> PrdVersion:
        return cls("8.8.8")
