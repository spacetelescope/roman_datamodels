from __future__ import annotations

from roman_datamodels.stnode import rad

__all__ = ["FpsOrigin"]


class FpsOrigin(rad.TaggedStrNodeMixin, rad.RadEnum, metaclass=rad.NodeEnumMeta):
    STSCI = "STSCI"
    IPAC_SSC = "IPAC/SSC"

    @classmethod
    def default(cls) -> FpsOrigin:
        return cls.STSCI

    @classmethod
    def _asdf_tag_uris(cls) -> dict[str, str]:
        return {
            "asdf://stsci.edu/datamodels/roman/tags/fps/origin-1.0.0": "asdf://stsci.edu/datamodels/roman/schemas/fps/tagged_scalars/origin-1.0.0"
        }
