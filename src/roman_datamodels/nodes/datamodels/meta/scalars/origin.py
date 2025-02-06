from __future__ import annotations

from roman_datamodels.stnode import rad

__all__ = ["Origin"]


class Origin(rad.TaggedStrNodeMixin, rad.RadEnum, metaclass=rad.NodeEnumMeta):
    STSCI = "STSCI"
    STSCI_SOC = "STSCI/SOC"
    IPAC_SSC = "IPAC/SSC"

    @classmethod
    def default(cls) -> Origin:
        return cls.STSCI_SOC

    @classmethod
    def _asdf_tag_uris(cls) -> dict[str, str]:
        return {
            "asdf://stsci.edu/datamodels/roman/tags/origin-1.0.0": "asdf://stsci.edu/datamodels/roman/schemas/tagged_scalars/origin-1.0.0"
        }
