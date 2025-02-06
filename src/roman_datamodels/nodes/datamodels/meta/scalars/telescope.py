from __future__ import annotations

from roman_datamodels.stnode import rad

__all__ = ["Telescope"]


class Telescope(rad.TaggedStrNodeMixin, rad.RadEnum, metaclass=rad.NodeEnumMeta):
    ROMAN = "ROMAN"

    @classmethod
    def default(cls) -> Telescope:
        return cls.ROMAN

    @classmethod
    def _asdf_tag_uris(cls) -> dict[str, str]:
        return {
            "asdf://stsci.edu/datamodels/roman/tags/telescope-1.0.0": "asdf://stsci.edu/datamodels/roman/schemas/tagged_scalars/telescope-1.0.0"
        }
