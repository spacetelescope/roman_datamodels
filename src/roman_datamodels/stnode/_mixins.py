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
    def from_schema(cls, defaults=None):
        if defaults:
            return cls(defaults)
        return cls.now()

    @classmethod
    def fake_data(cls, defaults=None):
        if defaults:
            return cls(defaults)
        return cls("2020-01-01T00:00:00.0", format="isot", scale="utc")


class FpsFileDateMixin(FileDateMixin):
    pass


class TvacFileDateMixin(FileDateMixin):
    pass


class CalibrationSoftwareNameMixin:
    @classmethod
    def from_schema(cls, defaults=None):
        if defaults:
            return cls(defaults)
        return cls("RomanCAL")


class OriginMixin:
    @classmethod
    def from_schema(cls, defaults=None):
        if defaults:
            return cls(defaults)
        return cls("STSCI")


class TelescopeMixin:
    @classmethod
    def from_schema(cls, defaults=None):
        if defaults:
            return cls(defaults)
        return cls("ROMAN")


class RefFileMixin:
    @classmethod
    def from_schema(cls, defaults=None):
        defaults = defaults or {}
        # TODO the nested "crds" dict won't be copied here
        schema = _get_schema_from_tag(cls._default_tag)
        keys = defaults.keys() | {k for k, v in schema["properties"].items() if v["type"] == "string"}
        return cls({k: defaults.get(k, "NA") for k in keys})


class L2CalStepMixin:
    @classmethod
    def from_schema(cls, defaults=None):
        defaults = defaults or {}
        schema = _get_schema_from_tag(cls._default_tag)
        return cls({k: defaults.get(k, "INCOMPLETE") for k in schema["properties"]})


class L3CalStepMixin(L2CalStepMixin):  # same as L2CalStepMixin
    pass
