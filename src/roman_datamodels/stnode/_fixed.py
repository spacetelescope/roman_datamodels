from ._tagged import TaggedObjectNode


class WfiMode(TaggedObjectNode):
    _tag = "asdf://stsci.edu/datamodels/roman/tags/wfi_mode-1.0.0"

    _GRATING_OPTICAL_ELEMENTS = {"GRISM", "PRISM"}

    __module__ = "roman_datamodels.stnode"

    @property
    def filter(self):
        if self.optical_element in self._GRATING_OPTICAL_ELEMENTS:
            return None
        else:
            return self.optical_element

    @property
    def grating(self):
        if self.optical_element in self._GRATING_OPTICAL_ELEMENTS:
            return self.optical_element
        else:
            return None
