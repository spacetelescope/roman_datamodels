from roman_datamodels.stnode import rad

__all__ = ["Pointing"]


class Pointing(rad.TaggedObjectNode):
    @classmethod
    def _asdf_tag_uris(cls) -> dict[str, str]:
        return {
            "asdf://stsci.edu/datamodels/roman/tags/pointing-1.0.0": "asdf://stsci.edu/datamodels/roman/schemas/pointing-1.0.0"
        }

    @rad.field
    def ra_v1(self) -> float:
        return rad.NONUM

    @rad.field
    def dec_v1(self) -> float:
        return rad.NONUM

    @rad.field
    def pa_v3(self) -> float:
        return rad.NONUM

    @rad.field
    def target_aperture(self) -> str:
        return rad.NOSTR

    @rad.field
    def target_ra(self) -> float:
        return rad.NONUM

    @rad.field
    def target_dec(self) -> float:
        return rad.NONUM
