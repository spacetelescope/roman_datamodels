"""
Mixin classes for additional functionality for STNode classes
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ._tagged import _get_schema_from_tag

if TYPE_CHECKING:
    from typing import ClassVar

__all__ = ["WfiModeMixin"]


class WfiModeMixin:
    """
    Extensions to the WfiMode class.
        Adds to indication properties
    """

    # Every optical element is a grating or a filter
    #   There are less gratings than filters so its easier to list out the
    #   gratings.
    _GRATING_OPTICAL_ELEMENTS: ClassVar = {"GRISM", "PRISM"}

    @property
    def filter(self):
        """
        Returns the filter if it is one, otherwise None
        """
        if self.optical_element in self._GRATING_OPTICAL_ELEMENTS:
            return None
        else:
            return self.optical_element

    @property
    def grating(self):
        """
        Returns the grating if it is one, otherwise None
        """
        if self.optical_element in self._GRATING_OPTICAL_ELEMENTS:
            return self.optical_element
        else:
            return None


class FileDateMixin:
    @classmethod
    def from_schema(cls):
        return cls.now()


class CalibrationSoftwareNameMixin:
    @classmethod
    def from_schema(cls):
        return cls("RomanCAL")


class OriginMixin:
    @classmethod
    def from_schema(cls):
        return cls("STSCI")


class TelescopeMixin:
    @classmethod
    def from_schema(cls):
        return cls("ROMAN")


class RefFileMixin:
    @classmethod
    def from_schema(cls):
        schema = _get_schema_from_tag(cls._default_tag)
        return cls({k: "NA" for k, v in schema["properties"].items() if v["type"] == "string"})


class L2CalStepMixin:
    @classmethod
    def from_schema(cls):
        schema = _get_schema_from_tag(cls._default_tag)
        return cls({k: "INCOMPLETE" for k in schema["properties"]})


class L3CalStepMixin(L2CalStepMixin):  # same as L2CalStepMixin
    pass
