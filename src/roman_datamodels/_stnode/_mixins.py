"""
Mixin classes for additional functionality for STNode classes
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from copy import deepcopy
from typing import TYPE_CHECKING, Any, ClassVar, Self, TypeAlias

from asdf.tags.core.ndarray import asdf_datatype_to_numpy_dtype

from ._schema import Builder, _get_keyword, _get_properties
from ._tagged import _get_schema_from_tag

# This is a workaround for MyPy to understand the Mixin classes
if TYPE_CHECKING:
    from astropy.time import Time

    from ._tagged import TaggedObjectNode, TaggedScalarNode

    class _TimeNode(Time, TaggedScalarNode):
        pass

    _ObjectBase: TypeAlias = TaggedObjectNode
    _ScalarBase: TypeAlias = TaggedScalarNode
    _TimeBase: TypeAlias = _TimeNode
else:
    _ObjectBase = object
    _ScalarBase: TypeAlias = object
    _TimeBase: TypeAlias = object

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
    "WfiModeMixin",
]


class WfiModeMixin:
    """
    Extensions to the WfiMode class.
        Adds to indication properties
    """

    __slots__ = ()

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


class FileDateMixin(_TimeBase):
    @classmethod
    def _create_minimal(
        cls,
        *,
        defaults: Mapping[str, Any] | None = None,
        builder: Builder | None = None,
        tag: str | None = None,
    ) -> Self:
        return cls.from_tag(
            node=(defaults if defaults else cls.now()),
            tag=(tag or cls.default_tag()),
        )

    @classmethod
    def _create_fake_data(
        cls,
        *,
        defaults: Mapping[str, Any] | None = None,
        shape: tuple[int, ...] | None = None,
        builder: Builder | None = None,
        tag: str | None = None,
    ) -> Self:
        return cls.from_tag(
            node=(defaults if defaults else cls("2020-01-01T00:00:00.0", format="isot", scale="utc")),
            tag=(tag or cls.default_tag()),
        )


class FpsFileDateMixin(FileDateMixin):
    pass


class TvacFileDateMixin(FileDateMixin):
    pass


class CalibrationSoftwareNameMixin(_ScalarBase):
    @classmethod
    def _create_minimal(
        cls,
        *,
        defaults: Mapping[str, Any] | None = None,
        builder: Builder | None = None,
        tag: str | None = None,
    ) -> Self:
        return cls.from_tag(
            node=(defaults if defaults else "RomanCAL"),
            tag=(tag or cls.default_tag()),
        )


class PrdVersionMixin(_ScalarBase):
    @classmethod
    def _create_fake_data(
        cls,
        *,
        defaults: Mapping[str, Any] | None = None,
        shape: tuple[int, ...] | None = None,
        builder: Builder | None = None,
        tag: str | None = None,
    ) -> Self:
        return cls.from_tag(
            node=(defaults if defaults else "8.8.8"),
            tag=(tag or cls.default_tag()),
        )


class SdfSoftwareVersionMixin(_ScalarBase):
    @classmethod
    def _create_fake_data(
        cls,
        *,
        defaults: Mapping[str, Any] | None = None,
        shape: tuple[int, ...] | None = None,
        builder: Builder | None = None,
        tag: str | None = None,
    ) -> Self:
        return cls.from_tag(
            node=(defaults if defaults else "7.7.7"),
            tag=(tag or cls.default_tag()),
        )


class OriginMixin(_ScalarBase):
    @classmethod
    def _create_minimal(
        cls,
        *,
        defaults: Mapping[str, Any] | None = None,
        builder: Builder | None = None,
        tag: str | None = None,
    ) -> Self:
        return cls.from_tag(
            node=(defaults if defaults else "STSCI/SOC"),
            tag=(tag or cls.default_tag()),
        )


class TelescopeMixin(_ScalarBase):
    @classmethod
    def _create_minimal(
        cls,
        *,
        defaults: Mapping[str, Any] | None = None,
        builder: Builder | None = None,
        tag: str | None = None,
    ) -> Self:
        return cls.from_tag(
            node=(defaults if defaults else "ROMAN"),
            tag=(tag or cls.default_tag()),
        )


class RefFileMixin(_ObjectBase):
    __slots__ = ()

    @classmethod
    def _create_minimal(
        cls,
        *,
        defaults: Mapping[str, Any] | None = None,
        builder: Builder | None = None,
        tag: str | None = None,
    ) -> Self:
        # copy defaults as we may modify them below
        defaults = dict(deepcopy(defaults)) if defaults else {}
        tag = tag or cls.default_tag()

        schema = _get_schema_from_tag(tag)
        for k, v in schema["properties"].items():
            if v["type"] != "string":
                continue
            if k in defaults:
                continue
            defaults[k] = "N/A"

        return cls.from_tag(
            node=(builder or Builder()).from_object(schema, defaults),
            tag=tag,
        )


class L2CalStepMixin(_ObjectBase):
    __slots__ = ()

    @classmethod
    def _create_minimal(
        cls,
        *,
        defaults: Mapping[str, Any] | None = None,
        builder: Builder | None = None,
        tag: str | None = None,
    ) -> Self:
        tag = tag or cls.default_tag()
        defaults = defaults or {}
        return cls.from_tag(
            node=({k: defaults.get(k, "INCOMPLETE") for k in _get_schema_from_tag(tag)["properties"]}),
            tag=tag,
        )


class L3CalStepMixin(L2CalStepMixin):  # same as L2CalStepMixin
    __slots__ = ()


class ImageSourceCatalogMixin(_ObjectBase):
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

        columns_schema = dict(_get_properties(_get_schema_from_tag(tag or cls.default_tag())["properties"]["source_catalog"]))
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
    def _create_fake_data(
        cls,
        *,
        defaults: Mapping[str, Any] | None = None,
        shape: tuple[int, ...] | None = None,
        builder: Builder | None = None,
        tag: str | None = None,
    ) -> Self | None:
        defaults = dict(defaults) if defaults else {}
        if "source_catalog" not in defaults:
            defaults["source_catalog"] = cls._create_empty_catalog(tag=tag)
        return super()._create_fake_data(defaults=defaults, shape=shape, builder=builder, tag=tag)


class ForcedImageSourceCatalogMixin(ImageSourceCatalogMixin):
    __slots__ = ()


class MosaicSourceCatalogMixin(ImageSourceCatalogMixin):
    __slots__ = ()


class ForcedMosaicSourceCatalogMixin(ImageSourceCatalogMixin):
    __slots__ = ()


class MultibandSourceCatalogMixin(ImageSourceCatalogMixin):
    __slots__ = ()
