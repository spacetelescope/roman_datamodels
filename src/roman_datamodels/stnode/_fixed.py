from astropy.time import Time

from ._tagged import TaggedListNode, TaggedObjectNode, TaggedScalarNode


class WfiMode(TaggedObjectNode):
    _tag = "asdf://stsci.edu/datamodels/roman/tags/wfi_mode-1.0.0"

    _GRATING_OPTICAL_ELEMENTS = {"GRISM", "PRISM"}

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


class CalLogs(TaggedListNode):
    _tag = "asdf://stsci.edu/datamodels/roman/tags/cal_logs-1.0.0"


class FileDate(Time, TaggedScalarNode):
    _tag = "asdf://stsci.edu/datamodels/roman/tags/file_date-1.0.0"
