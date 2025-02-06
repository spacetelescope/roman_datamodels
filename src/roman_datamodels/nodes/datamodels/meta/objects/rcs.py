from roman_datamodels.stnode import rad

__all__ = ["Rcs", "RcsBankEntry", "RcsElectronicsEntry", "RcsLedEntry"]


class RcsElectronicsEntry(rad.StrNodeMixin, rad.RadEnum, metaclass=rad.NodeEnumMeta):
    """
    Enum for the possible electronics in rcs
    """

    A = "A"
    B = "B"
    NONE = "None"

    @classmethod
    def _asdf_container(cls) -> type:
        return Rcs

    @classmethod
    def _asdf_property_name(cls) -> str:
        return "electronics"


class RcsBankEntry(rad.StrNodeMixin, rad.RadEnum, metaclass=rad.NodeEnumMeta):
    """
    Enum for the possible banks in rcs
    """

    ONE = "1"
    TWO = "2"
    NONE = "None"

    @classmethod
    def _asdf_container(cls) -> type:
        return Rcs

    @classmethod
    def _asdf_property_name(cls) -> str:
        return "bank"


class RcsLedEntry(rad.StrNodeMixin, rad.RadEnum, metaclass=rad.NodeEnumMeta):
    """
    Enum for the possible leds in rcs
    """

    ONE = "1"
    TWO = "2"
    THREE = "3"
    FOUR = "4"
    FIVE = "5"
    SIX = "6"
    NONE = "None"

    @classmethod
    def _asdf_container(cls) -> type:
        return Rcs

    @classmethod
    def _asdf_property_name(cls) -> str:
        return "led"


class Rcs(rad.TaggedObjectNode):
    @classmethod
    def _asdf_tag_uris(cls) -> dict[str, str]:
        return {"asdf://stsci.edu/datamodels/roman/tags/rcs-1.0.0": "asdf://stsci.edu/datamodels/roman/schemas/rcs-1.0.0"}

    @rad.field
    def active(self) -> bool:
        return False

    @rad.field
    def electronics(self) -> RcsElectronicsEntry | None:
        return RcsElectronicsEntry.A

    @rad.field
    def bank(self) -> RcsBankEntry | None:
        return RcsBankEntry.ONE

    @rad.field
    def led(self) -> RcsLedEntry | None:
        return RcsLedEntry.ONE

    @rad.field
    def counts(self) -> int:
        return rad.NOINT
