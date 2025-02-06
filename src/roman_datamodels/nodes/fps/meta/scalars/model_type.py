from __future__ import annotations

from roman_datamodels.stnode import rad

__all__ = ["FpsModelType"]


class FpsModelType(str, rad.TaggedScalarNode):
    @classmethod
    def _asdf_tag_uris(cls) -> dict[str, str]:
        return {
            "asdf://stsci.edu/datamodels/roman/tags/fps/model_type-1.0.0": "asdf://stsci.edu/datamodels/roman/schemas/fps/tagged_scalars/model_type-1.0.0"
        }

    @classmethod
    def default(cls) -> FpsModelType:
        return cls(rad.NOSTR)
