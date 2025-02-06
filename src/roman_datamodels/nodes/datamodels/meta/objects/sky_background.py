from roman_datamodels.stnode import rad

__all__ = ["SkyBackground", "SkyBackgroundMethodEntry"]


class SkyBackgroundMethodEntry(rad.StrNodeMixin, rad.RadEnum, metaclass=rad.NodeEnumMeta):
    """
    Enum for the possible entries for method in sky_background
    """

    NONE = "None"
    LOCAL = "local"
    GLOBAL_MATCH = "global+match"
    MATCH = "match"
    GLOBAL = "global"

    @classmethod
    def _asdf_container(cls) -> type:
        return SkyBackground

    @classmethod
    def _asdf_property_name(cls) -> str:
        return "method"


class SkyBackground(rad.TaggedObjectNode):
    @classmethod
    def _asdf_tag_uris(cls) -> dict[str, str]:
        return {
            "asdf://stsci.edu/datamodels/roman/tags/sky_background-1.0.0": "asdf://stsci.edu/datamodels/roman/schemas/sky_background-1.0.0",
        }

    @rad.field
    def level(self) -> float | None:
        return None

    @rad.field
    def method(self) -> SkyBackgroundMethodEntry:
        return SkyBackgroundMethodEntry.NONE

    @rad.field
    def subtracted(self) -> bool:
        return False
