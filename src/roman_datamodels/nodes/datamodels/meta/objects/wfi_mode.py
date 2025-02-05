from typing import ClassVar

from roman_datamodels.stnode import rad

from ..scalars import WfiDetector, WfiOpticalElement

__all__ = ["InstrumentNameEntry", "WfiMode"]


class InstrumentNameEntry(rad.StrNodeMixin, rad.RadEnum, metaclass=rad.NodeEnumMeta):
    """
    Enum for the possible entries for instrument name in schemas
    """

    WFI = "WFI"

    @classmethod
    def _asdf_container(cls) -> type:
        return WfiMode

    @classmethod
    def _asdf_property_name(cls) -> str:
        return "name"


class WfiMode(rad.TaggedObjectNode):
    # Every optical element is a grating or a filter
    #   There are less gratings than filters so its easier to list out the
    #   gratings.
    _GRATING_OPTICAL_ELEMENTS: ClassVar[tuple[str, ...]] = WfiOpticalElement.gratings()

    @classmethod
    def _asdf_tag_uris(cls) -> dict[str, str]:
        return {
            "asdf://stsci.edu/datamodels/roman/tags/wfi_mode-1.0.0": "asdf://stsci.edu/datamodels/roman/schemas/wfi_mode-1.0.0",
        }

    @rad.field
    def name(self) -> InstrumentNameEntry:
        return InstrumentNameEntry.WFI

    @rad.field
    def detector(self) -> WfiDetector:
        return WfiDetector.WFI01

    @rad.field
    def optical_element(self) -> WfiOpticalElement:
        return WfiOpticalElement.F158

    @property
    def filter(self) -> WfiOpticalElement | None:
        """
        Returns the filter if it is one, otherwise None
        """
        if self.optical_element in self._GRATING_OPTICAL_ELEMENTS:
            return None

        return self.optical_element

    @property
    def grating(self) -> WfiOpticalElement | None:
        """
        Returns the grating if it is one, otherwise None
        """
        if self.optical_element in self._GRATING_OPTICAL_ELEMENTS:
            return self.optical_element

        return None
