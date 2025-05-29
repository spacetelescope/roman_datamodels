"""
Mixin classes for additional functionality for STNode classes
"""

from __future__ import annotations

from copy import deepcopy
from typing import TYPE_CHECKING

from ._schema import Builder
from ._tagged import _get_schema_from_tag

if TYPE_CHECKING:
    from typing import ClassVar

__all__ = [
    "CalibrationSoftwareNameMixin",
    "FileDateMixin",
    "FpsFileDateMixin",
    "L2CalStepMixin",
    "L3CalStepMixin",
    "OriginMixin",
    "PrdVersionMixin",
    "RefFileMixin",
    "SdfSoftwareVersionMixin",
    "TelescopeMixin",
    "TvacFileDateMixin",
    "WfiImgPhotomRefMixin",
    "WfiModeMixin",
]


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
    def create_minimal(cls, defaults=None, builder=None):
        if defaults:
            return cls(defaults)
        return cls.now()

    @classmethod
    def create_fake_data(cls, defaults=None, shape=None, builder=None):
        if defaults:
            return cls(defaults)
        return cls("2020-01-01T00:00:00.0", format="isot", scale="utc")


class FpsFileDateMixin(FileDateMixin):
    pass


class TvacFileDateMixin(FileDateMixin):
    pass


class CalibrationSoftwareNameMixin:
    @classmethod
    def create_minimal(cls, defaults=None, builder=None):
        if defaults:
            return cls(defaults)
        return cls("RomanCAL")


class PrdVersionMixin:
    @classmethod
    def create_fake_data(cls, defaults=None, builder=None):
        if defaults:
            return cls(defaults)
        return cls("8.8.8")


class SdfSoftwareVersionMixin:
    @classmethod
    def create_fake_data(cls, defaults=None, builder=None):
        if defaults:
            return cls(defaults)
        return cls("7.7.7")


class OriginMixin:
    @classmethod
    def create_minimal(cls, defaults=None, builder=None):
        if defaults:
            return cls(defaults)
        return cls("STSCI/SOC")


class TelescopeMixin:
    @classmethod
    def create_minimal(cls, defaults=None, builder=None):
        if defaults:
            return cls(defaults)
        return cls("ROMAN")


class RefFileMixin:
    @classmethod
    def create_minimal(cls, defaults=None, builder=None):
        # copy defaults as we may modify them below
        if defaults:
            defaults = deepcopy(defaults)
        else:
            defaults = {}
        schema = _get_schema_from_tag(cls._default_tag)
        for k, v in schema["properties"].items():
            if v["type"] != "string":
                continue
            if k in defaults:
                continue
            defaults[k] = "N/A"
        if not builder:
            builder = Builder()
        data = builder.from_object(schema, defaults)
        obj = cls(data)
        return obj


class L2CalStepMixin:
    @classmethod
    def create_minimal(cls, defaults=None, builder=None):
        defaults = defaults or {}
        schema = _get_schema_from_tag(cls._default_tag)
        return cls({k: defaults.get(k, "INCOMPLETE") for k in schema["properties"]})


class L3CalStepMixin(L2CalStepMixin):  # same as L2CalStepMixin
    pass


class WfiImgPhotomRefMixin:
    @classmethod
    def create_fake_data(cls, defaults=None, shape=None, builder=None):
        defaults = defaults or {}
        if "phot_table" not in defaults:
            defaults["phot_table"] = {
                "F062": {"photmjsr": 1e-15, "uncertainty": 1e-16, "pixelareasr": 1e-13},
                "F087": {"photmjsr": 1e-15, "uncertainty": 1e-16, "pixelareasr": 1e-13},
                "F106": {"photmjsr": 1e-15, "uncertainty": 1e-16, "pixelareasr": 1e-13},
                "F129": {"photmjsr": 1e-15, "uncertainty": 1e-16, "pixelareasr": 1e-13},
                "F146": {"photmjsr": 1e-15, "uncertainty": 1e-16, "pixelareasr": 1e-13},
                "F158": {"photmjsr": 1e-15, "uncertainty": 1e-16, "pixelareasr": 1e-13},
                "F184": {"photmjsr": 1e-15, "uncertainty": 1e-16, "pixelareasr": 1e-13},
                "F213": {"photmjsr": 1e-15, "uncertainty": 1e-16, "pixelareasr": 1e-13},
                "GRISM": {"photmjsr": None, "uncertainty": None, "pixelareasr": 1e-13},
                "PRISM": {"photmjsr": None, "uncertainty": None, "pixelareasr": 1e-13},
                "DARK": {"photmjsr": None, "uncertainty": None, "pixelareasr": 1e-13},
            }
        return super().create_fake_data(defaults, shape, builder)
