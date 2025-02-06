from __future__ import annotations

from roman_datamodels.stnode import rad

__all__ = ["Filename"]


class Filename(str, rad.TaggedScalarNode):
    @classmethod
    def _asdf_tag_uris(cls) -> dict[str, str]:
        return {
            "asdf://stsci.edu/datamodels/roman/tags/filename-1.0.0": "asdf://stsci.edu/datamodels/roman/schemas/tagged_scalars/filename-1.0.0"
        }

    @classmethod
    def default(cls) -> Filename:
        return cls(rad.NOFN)
