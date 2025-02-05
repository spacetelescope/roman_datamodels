from __future__ import annotations

from roman_datamodels.stnode import rad

__all__ = ["FpsFilename"]


class FpsFilename(str, rad.TaggedScalarNode):
    @classmethod
    def _asdf_tag_uris(cls) -> dict[str, str]:
        return {
            "asdf://stsci.edu/datamodels/roman/tags/fps/filename-1.0.0": "asdf://stsci.edu/datamodels/roman/schemas/fps/tagged_scalars/filename-1.0.0"
        }

    @classmethod
    def default(cls) -> FpsFilename:
        return cls(rad.NOFN)
