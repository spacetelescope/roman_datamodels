"""
Mixin classes for additional functionality for STNode classes
"""
__all__ = ["WfiModeMixin"]


class WfiModeMixin:
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
