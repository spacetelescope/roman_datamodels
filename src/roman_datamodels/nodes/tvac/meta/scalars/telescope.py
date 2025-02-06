from __future__ import annotations

from roman_datamodels.stnode import rad

__all__ = ["TvacTelescope"]


class TvacTelescope(rad.TaggedStrNodeMixin, rad.RadEnum, metaclass=rad.NodeEnumMeta):
    ROMAN = "ROMAN"

    @classmethod
    def default(cls) -> TvacTelescope:
        return cls.ROMAN

    @classmethod
    def _asdf_tag_uris(cls) -> dict[str, str]:
        return {
            "asdf://stsci.edu/datamodels/roman/tags/tvac/telescope-1.0.0": "asdf://stsci.edu/datamodels/roman/schemas/tvac/tagged_scalars/telescope-1.0.0"
        }
