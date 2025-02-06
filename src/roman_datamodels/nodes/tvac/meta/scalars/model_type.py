from __future__ import annotations

from roman_datamodels.stnode import rad

__all__ = ["TvacModelType"]


class TvacModelType(str, rad.TaggedScalarNode):
    @classmethod
    def _asdf_tag_uris(cls) -> dict[str, str]:
        return {
            "asdf://stsci.edu/datamodels/roman/tags/tvac/model_type-1.0.0": "asdf://stsci.edu/datamodels/roman/schemas/tvac/tagged_scalars/model_type-1.0.0"
        }

    @classmethod
    def default(cls) -> TvacModelType:
        return cls(rad.NOSTR)
