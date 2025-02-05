from __future__ import annotations

from roman_datamodels.stnode import rad

__all__ = ["FpsTelescope"]


class FpsTelescope(rad.TaggedStrNodeMixin, rad.RadEnum, metaclass=rad.NodeEnumMeta):
    ROMAN = "ROMAN"

    @classmethod
    def default(cls) -> FpsTelescope:
        return cls.ROMAN

    @classmethod
    def _asdf_tag_uris(cls) -> dict[str, str]:
        return {
            "asdf://stsci.edu/datamodels/roman/tags/fps/telescope-1.0.0": "asdf://stsci.edu/datamodels/roman/schemas/fps/tagged_scalars/telescope-1.0.0"
        }
