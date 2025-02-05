from roman_datamodels.stnode import core, rad

__all__ = ["MosaicWcsinfo", "MosaicWcsinfoProjectionEntry"]


class MosaicWcsinfoProjectionEntry(rad.StrNodeMixin, rad.RadEnum, metaclass=rad.NodeEnumMeta):
    """
    Enum for the possible entries for projection in wcsinfo
    """

    TAN = "TAN"

    @classmethod
    def _asdf_container(cls) -> type:
        return MosaicWcsinfo

    @classmethod
    def _asdf_property_name(cls) -> str:
        return "projection"


class MosaicWcsinfo(rad.TaggedObjectNode):
    @classmethod
    def _asdf_tag_uris(cls) -> dict[str, str]:
        return {
            "asdf://stsci.edu/datamodels/roman/tags/mosaic_wcsinfo-1.0.0": "asdf://stsci.edu/datamodels/roman/schemas/mosaic_wcsinfo-1.0.0"
        }

    @rad.field
    def ra_ref(self) -> float:
        return rad.NONUM

    @rad.field
    def dec_ref(self) -> float:
        return rad.NONUM

    @rad.field
    def x_ref(self) -> float:
        return rad.NONUM

    @rad.field
    def y_ref(self) -> float:
        return rad.NONUM

    @rad.field
    def rotation_matrix(self) -> core.LNode[core.LNode[float]]:
        return core.LNode(
            [
                core.LNode([rad.NONUM, rad.NONUM]),
                core.LNode([rad.NONUM, rad.NONUM]),
            ]
        )

    @rad.field
    def pixel_scale(self) -> float:
        return rad.NONUM

    @rad.field
    def pixel_scale_local(self) -> float:
        return rad.NONUM

    @rad.field
    def projection(self) -> MosaicWcsinfoProjectionEntry:
        return MosaicWcsinfoProjectionEntry.TAN

    @rad.field
    def s_region(self) -> str:
        return rad.NOSTR

    @rad.field
    def pixel_shape(self) -> core.LNode[int]:
        return core.LNode([rad.NOINT, rad.NOINT])

    @rad.field
    def ra_center(self) -> float:
        return rad.NONUM

    @rad.field
    def dec_center(self) -> float:
        return rad.NONUM

    @rad.field
    def ra_corn1(self) -> float:
        return rad.NONUM

    @rad.field
    def dec_corn1(self) -> float:
        return rad.NONUM

    @rad.field
    def ra_corn2(self) -> float:
        return rad.NONUM

    @rad.field
    def dec_corn2(self) -> float:
        return rad.NONUM

    @rad.field
    def ra_corn3(self) -> float:
        return rad.NONUM

    @rad.field
    def dec_corn3(self) -> float:
        return rad.NONUM

    @rad.field
    def ra_corn4(self) -> float:
        return rad.NONUM

    @rad.field
    def dec_corn4(self) -> float:
        return rad.NONUM

    @rad.field
    def orientat_local(self) -> float:
        return rad.NONUM

    @rad.field
    def orientat(self) -> float:
        return rad.NONUM
