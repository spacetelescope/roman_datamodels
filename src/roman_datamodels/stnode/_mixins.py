"""
Mixin classes for additional functionality for STNode classes
"""

from __future__ import annotations

import re
from copy import deepcopy
from typing import TYPE_CHECKING

from asdf.tags.core.ndarray import asdf_datatype_to_numpy_dtype

from ._schema import Builder, _get_keyword, _get_properties
from ._tagged import _get_schema_from_tag

if TYPE_CHECKING:
    from typing import ClassVar

__all__ = [
    "CalibrationSoftwareNameMixin",
    "FileDateMixin",
    "ForcedImageSourceCatalogMixin",
    "ForcedMosaicSourceCatalogMixin",
    "FpsFileDateMixin",
    "ImageSourceCatalogMixin",
    "L2CalStepMixin",
    "L3CalStepMixin",
    "MosaicSourceCatalogMixin",
    "MultibandSourceCatalogMixin",
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


class ImageSourceCatalogMixin:
    def get_column_definition(self, name):
        """
        Get the definition of a named column in the catalog table.

        This function parses the "definitions" part of the catalog
        schema and returns the parsed content.

        Parameters
        ----------
        name: str
            Column name, may contain aperture radisu or filter/band or prefixed
            with ``forced_``.

        Returns
        -------
        dict or None
            Dictionary containing unit, description, and datatype information
            or None if the name does not match any definition.
        """
        if name.startswith("forced_"):
            _, name = name.split("forced_", maxsplit=1)
        definitions = _get_keyword(self.get_schema()["properties"]["source_catalog"], "definitions")
        for def_name, definition in definitions.items():
            if "~radius~" in def_name:
                def_name = def_name.replace("~radius~", r"[0-9]{2}")
            if "_~band~" in def_name:
                def_name = def_name.replace("_~band~", r"(_f[0-9]{3}|)")
            if "~band~" in def_name:
                def_name = def_name.replace("~band~", r"(f[0-9]{3}|)")
            if re.match(f"^{def_name}$", name):
                return {
                    "unit": definition["unit"],
                    "description": definition["description"],
                    "datatype": asdf_datatype_to_numpy_dtype(
                        definition["properties"]["data"]["properties"]["datatype"]["enum"][0]
                    ),
                }

    @classmethod
    def _create_empty_catalog(cls, aperture_radii=None, filters=None):
        from astropy.table import Column, Table

        aperture_radii = aperture_radii or ["00"]
        filters = filters or ["f184"]

        table_schema = _get_schema_from_tag(cls._default_tag)["properties"]["source_catalog"]
        columns = []
        for raw_col_def in dict(_get_properties(table_schema))["columns"]["allOf"]:
            col_def = raw_col_def["not"]["items"]["not"]
            properties = dict(_get_properties(col_def))
            name_regex = properties["name"]["pattern"]
            unit = _get_keyword(col_def, "unit")
            description = _get_keyword(col_def, "description")
            dtype = asdf_datatype_to_numpy_dtype(properties["data"]["properties"]["datatype"]["enum"][0])

            name_queue = [name_regex[1:-1]]

            substitutions = [
                (r"\[0-9]\{2}", aperture_radii),
                (r"\(.*\)", filters),
            ]
            while name_queue:
                name = name_queue.pop()
                for regex, values in substitutions:
                    if re.search(regex, name):
                        name_queue.extend(re.sub(regex, value, name) for value in values)
                        break
                else:
                    columns.append(Column([], unit=unit, description=description, dtype=dtype, name=name))
        return Table(columns)

    @classmethod
    def create_fake_data(cls, defaults=None, shape=None, builder=None):
        defaults = defaults or {}
        if "source_catalog" not in defaults:
            defaults["source_catalog"] = cls._create_empty_catalog()
        return super().create_fake_data(defaults, shape, builder)


class ForcedImageSourceCatalogMixin(ImageSourceCatalogMixin):
    pass


class MosaicSourceCatalogMixin(ImageSourceCatalogMixin):
    pass


class ForcedMosaicSourceCatalogMixin(ImageSourceCatalogMixin):
    pass


class MultibandSourceCatalogMixin(ImageSourceCatalogMixin):
    pass
