"""
Mixin classes for additional functionality for STNode classes
"""

from __future__ import annotations

import re
from copy import deepcopy
from typing import TYPE_CHECKING, ClassVar

from asdf.tags.core.ndarray import asdf_datatype_to_numpy_dtype
from astropy.time import Time

from ._schema import Builder, _get_keyword, _get_properties
from ._tagged import TaggedObjectNode, TaggedScalarNode, _get_schema_from_tag

if TYPE_CHECKING:

    class _TimeNode(Time, TaggedScalarNode):
        pass

    _TimeBase = _TimeNode
    _ObjectBase = TaggedObjectNode
else:
    _TimeBase = object
    _ObjectBase = object


__all__ = []


class WfiMode(TaggedObjectNode):
    """
    Extensions to the WfiMode class.
        Adds to indication properties
    """

    __slots__ = ()
    __module__ = "roman_datamodels._stnode"
    _tag_pattern: ClassVar[str] = "asdf://stsci.edu/datamodels/roman/tags/wfi_mode-*"
    _default_tag: ClassVar[str] = "asdf://stsci.edu/datamodels/roman/tags/wfi_mode-1.2.0"

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


class _FileDate(_TimeBase):
    @classmethod
    def _create_minimal(cls, defaults=None, builder=None, *, tag=None):
        new = cls(defaults) if defaults else cls.now()
        if tag:
            new._read_tag = tag

        return new

    @classmethod
    def _create_fake_data(cls, defaults=None, shape=None, builder=None, *, tag=None):
        new = cls(defaults) if defaults else cls("2020-01-01T00:00:00.0", format="isot", scale="utc")
        if tag:
            new._read_tag = tag

        return new


class FileDate(Time, _FileDate, TaggedScalarNode):
    __slots__ = ()
    __module__ = "roman_datamodels._stnode"
    _tag_pattern: ClassVar[str] = "asdf://stsci.edu/datamodels/roman/tags/file_date-*"
    _default_tag: ClassVar[str] = "asdf://stsci.edu/datamodels/roman/tags/file_date-1.0.0"


class FpsFileDate(Time, _FileDate, TaggedScalarNode):
    __slots__ = ()
    __module__ = "roman_datamodels._stnode"
    _tag_pattern: ClassVar[str] = "asdf://stsci.edu/datamodels/roman/tags/fps/file_date-*"
    _default_tag: ClassVar[str] = "asdf://stsci.edu/datamodels/roman/tags/fps/file_date-1.0.0"


class TvacFileDate(Time, _FileDate, TaggedScalarNode):
    __slots__ = ()
    __module__ = "roman_datamodels._stnode"
    _tag_pattern: ClassVar[str] = "asdf://stsci.edu/datamodels/roman/tags/tvac/file_date-*"
    _default_tag: ClassVar[str] = "asdf://stsci.edu/datamodels/roman/tags/tvac/file_date-1.0.0"


class CalibrationSoftwareName(str, TaggedScalarNode):  # type: ignore[misc]
    __slots__ = ()
    __module__ = "roman_datamodels._stnode"
    _tag_pattern: ClassVar[str] = "asdf://stsci.edu/datamodels/roman/tags/calibration_software_name-*"
    _default_tag: ClassVar[str] = "asdf://stsci.edu/datamodels/roman/tags/calibration_software_name-1.0.0"

    @classmethod
    def _create_minimal(cls, defaults=None, builder=None, *, tag=None):
        new = cls(defaults) if defaults else cls("RomanCAL")
        if tag:
            new._read_tag = tag

        return new


class PrdVersion(str, TaggedScalarNode):  # type: ignore[misc]
    __slots__ = ()
    __module__ = "roman_datamodels._stnode"
    _tag_pattern: ClassVar[str] = "asdf://stsci.edu/datamodels/roman/tags/prd_version-*"
    _default_tag: ClassVar[str] = "asdf://stsci.edu/datamodels/roman/tags/prd_version-1.0.0"

    @classmethod
    def _create_fake_data(cls, defaults=None, shape=None, builder=None, *, tag=None):
        new = cls(defaults) if defaults else cls("8.8.8")
        if tag:
            new._read_tag = tag

        return new


class SdfSoftwareVersion(str, TaggedScalarNode):  # type: ignore[misc]
    __slots__ = ()
    __module__ = "roman_datamodels._stnode"
    _tag_pattern: ClassVar[str] = "asdf://stsci.edu/datamodels/roman/tags/sdf_software_version-*"
    _default_tag: ClassVar[str] = "asdf://stsci.edu/datamodels/roman/tags/sdf_software_version-1.0.0"

    @classmethod
    def _create_fake_data(cls, defaults=None, shape=None, builder=None, *, tag=None):
        new = cls(defaults) if defaults else cls("7.7.7")
        if tag:
            new._read_tag = tag

        return new


class Origin(str, TaggedScalarNode):  # type: ignore[misc]
    __slots__ = ()
    __module__ = "roman_datamodels._stnode"
    _tag_pattern: ClassVar[str] = "asdf://stsci.edu/datamodels/roman/tags/origin-*"
    _default_tag: ClassVar[str] = "asdf://stsci.edu/datamodels/roman/tags/origin-1.0.0"

    @classmethod
    def _create_minimal(cls, defaults=None, builder=None, *, tag=None):
        new = cls(defaults) if defaults else cls("STSCI/SOC")
        if tag:
            new._read_tag = tag

        return new


class Telescope(str, TaggedScalarNode):  # type: ignore[misc]
    __slots__ = ()
    __module__ = "roman_datamodels._stnode"
    _tag_pattern: ClassVar[str] = "asdf://stsci.edu/datamodels/roman/tags/telescope-*"
    _default_tag: ClassVar[str] = "asdf://stsci.edu/datamodels/roman/tags/telescope-1.0.0"

    @classmethod
    def _create_minimal(cls, defaults=None, builder=None, *, tag=None):
        new = cls(defaults) if defaults else cls("ROMAN")
        if tag:
            new._read_tag = tag

        return new


class RefFile(TaggedObjectNode):
    __slots__ = ()
    __module__ = "roman_datamodels._stnode"
    _tag_pattern: ClassVar[str] = "asdf://stsci.edu/datamodels/roman/tags/ref_file-*"
    _default_tag: ClassVar[str] = "asdf://stsci.edu/datamodels/roman/tags/ref_file-1.1.0"

    @classmethod
    def _create_minimal(cls, defaults=None, builder=None, *, tag=None):
        # copy defaults as we may modify them below
        if defaults:
            defaults = deepcopy(defaults)
        else:
            defaults = {}
        schema = _get_schema_from_tag(tag or cls._default_tag)
        for k, v in schema["properties"].items():
            if v["type"] != "string":
                continue
            if k in defaults:
                continue
            defaults[k] = "N/A"
        if not builder:
            builder = Builder()
        data = builder.from_object(schema, defaults)
        new = cls(data)
        if tag:
            new._read_tag = tag

        return new


class _CalStep(_ObjectBase):
    __slots__ = ()

    @classmethod
    def _create_minimal(cls, defaults=None, builder=None, *, tag=None):
        defaults = defaults or {}
        schema = _get_schema_from_tag(tag or cls._default_tag)
        new = cls({k: defaults.get(k, "INCOMPLETE") for k in schema["properties"]})
        if tag:
            new._read_tag = tag

        return new


class L2CalStep(_CalStep, TaggedObjectNode):
    __slots__ = ()
    __module__ = "roman_datamodels._stnode"
    _tag_pattern: ClassVar[str] = "asdf://stsci.edu/datamodels/roman/tags/l2_cal_step-*"
    _default_tag: ClassVar[str] = "asdf://stsci.edu/datamodels/roman/tags/l2_cal_step-1.2.0"


class L3CalStep(_CalStep, TaggedObjectNode):
    __slots__ = ()
    __module__ = "roman_datamodels._stnode"
    _tag_pattern: ClassVar[str] = "asdf://stsci.edu/datamodels/roman/tags/l3_cal_step-*"
    _default_tag: ClassVar[str] = "asdf://stsci.edu/datamodels/roman/tags/l3_cal_step-1.1.0"


class _SourceCatalog(_ObjectBase):
    __slots__ = ()

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
    def _create_empty_catalog(cls, tag=None, aperture_radii=None, filters=None):
        from astropy.table import Column, Table

        aperture_radii = aperture_radii or ["00"]
        filters = filters or ["f184"]

        columns_schema = dict(_get_properties(_get_schema_from_tag(tag or cls._default_tag)["properties"]["source_catalog"]))
        columns = []

        if "columns" in columns_schema:
            for raw_col_def in columns_schema["columns"]["allOf"]:
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
    def _create_fake_data(cls, defaults=None, shape=None, builder=None, *, tag=None):
        defaults = defaults or {}
        if "source_catalog" not in defaults:
            defaults["source_catalog"] = cls._create_empty_catalog(tag=tag)
        return super()._create_fake_data(defaults, shape, builder, tag=tag)


class ImageSourceCatalog(_SourceCatalog, TaggedObjectNode):
    __slots__ = ()
    __module__ = "roman_datamodels._stnode"
    _tag_pattern: ClassVar[str] = "asdf://stsci.edu/datamodels/roman/tags/image_source_catalog-*"


class ForcedImageSourceCatalog(_SourceCatalog, TaggedObjectNode):
    __slots__ = ()
    __module__ = "roman_datamodels._stnode"
    _tag_pattern: ClassVar[str] = "asdf://stsci.edu/datamodels/roman/tags/forced_image_source_catalog-*"


class MosaicSourceCatalog(_SourceCatalog, TaggedObjectNode):
    __slots__ = ()
    __module__ = "roman_datamodels._stnode"
    _tag_pattern: ClassVar[str] = "asdf://stsci.edu/datamodels/roman/tags/mosaic_source_catalog-*"


class ForcedMosaicSourceCatalog(_SourceCatalog, TaggedObjectNode):
    __slots__ = ()
    __module__ = "roman_datamodels._stnode"
    _tag_pattern: ClassVar[str] = "asdf://stsci.edu/datamodels/roman/tags/forced_mosaic_source_catalog-*"


class MultibandSourceCatalog(_SourceCatalog, TaggedObjectNode):
    __slots__ = ()
    __module__ = "roman_datamodels._stnode"
    _tag_pattern: ClassVar[str] = "asdf://stsci.edu/datamodels/roman/tags/multiband_source_catalog-*"
