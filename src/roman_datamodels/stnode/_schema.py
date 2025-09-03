"""
Code for relating nodes and schema.
"""

import copy
import enum
import functools
from collections.abc import Mapping, Sequence

import asdf

from ._registry import (
    NODE_CLASSES_BY_TAG,
    SCHEMA_URIS_BY_TAG,
)

__all__ = []


NOSTR = "?"
NONUM = -999999
NOBOOL = False


@functools.cache
def _get_schema_from_tag(tag):
    """
    Look up and load ASDF's schema corresponding to the tag_uri.

    Parameters
    ----------
    tag : str
        The tag_uri of the schema to load.
    """
    schema_uri = SCHEMA_URIS_BY_TAG[tag]

    return asdf.schema.load_schema(schema_uri, resolve_references=True)


class _MissingKeywordType:
    """Special value to indicate a keyword was not found in a schema"""

    def __bool__(self):
        return False


_MISSING_KEYWORD = _MissingKeywordType()


def _get_keyword(schema, key):
    """
    Search a schema for value for a given a keyword.

    Parameters
    ----------
    schema : dict
        The schema (with all references resolved) to search.

    key : str
        The keyword to use for the search.

    Returns
    -------
    value : Any or _MISSING_KEYWORD
        The value for the keyword or _MISSING_KEYWORD if not found.
    """
    if key in schema:
        return schema[key]
    for combiner in ("allOf", "anyOf"):
        if combiner not in schema:
            continue
        for subschema in schema[combiner]:
            value = _get_keyword(subschema, key)
            if value is not _MISSING_KEYWORD:
                return value
    return _MISSING_KEYWORD


def _has_keyword(schema, key):
    """
    Check if a schema has a given keyword.

    Parameters
    ----------
    schema : dict
        Schema to check.

    key : str
        Keyword to check for.

    Returns
    -------
    bool
        If the keyword was found
    """
    return _get_keyword(schema, key) != _MISSING_KEYWORD


def _get_properties(schema):
    """
    Generator that produces property definitions.

    Parameters
    ----------
    schema : dict
        Schema to parse.

    Yields
    ------
    (str, any)
        Property name and subschema.
    """
    if "allOf" in schema:
        for subschema in schema["allOf"]:
            yield from _get_properties(subschema)
    elif "anyOf" in schema:
        yield from _get_properties(schema["anyOf"][0])
    elif "properties" in schema:
        yield from schema["properties"].items()


def _get_required(schema):
    """
    Search a schema for required property names.

    Parameters
    ----------
    schema : dict
        Schema to parse.

    Returns
    -------
    set of str
        Set of required property names.
    """
    required = set()
    if "required" in schema:
        required.update(set(schema["required"]))
    if "allOf" in schema:
        for subschema in schema["allOf"]:
            required.update(_get_required(subschema))
    if "anyOf" in schema:
        required.update(_get_required(schema["anyOf"][0]))
    return required


class _NoValueType:
    """Special value to indicate a builder built nothing"""

    def __bool__(self):
        return False


_NO_VALUE = _NoValueType()


class SchemaType(enum.Enum):
    """
    Enumeration of possible types defined by a schema

    This includes jsonschema inherited types and TAGGED and UNKNOWN
    """

    UNKNOWN = 0
    OBJECT = 1
    ARRAY = 2
    STRING = 3
    INTEGER = 4
    NUMBER = 5
    BOOLEAN = 6
    NULL = 7
    TAGGED = 8


# sets of keyword names that are specific to certain types
_OBJECT_KEYWORDS = {
    "properties",
    "patternProperties",
    "required",
    "additionalProperties",
    "maxProperties",
    "minProperties",
    "dependencies",
}
_ARRAY_KEYWORDS = {"items", "additionalItems", "maxItems", "minItems", "uniqueItems"}
_STRING_KEYWORDS = {"pattern", "minLength", "maxLength"}
_NUMERIC_KEYWORDS = {"multipleOf", "maximum", "exclusiveMaximum", "minimum"}


class Builder:
    """
    Class to build objects based on a schema (and optional defaults).

    This base class only builds:
        - constant values (for example a single item enum)
        - container objects
        - required properties

    When a default is available it will be used instead of any
    schema defined value but only if the item is required by the
    schema. Default values for non-required items are ignored.
    """

    def get_type(self, schema):
        if _has_keyword(schema, "tag"):
            return SchemaType.TAGGED
        if defined_type := _get_keyword(schema, "type"):
            defined_type = defined_type.upper()
            if hasattr(SchemaType, defined_type):
                return getattr(SchemaType, defined_type)
        if any(_has_keyword(schema, k) for k in _OBJECT_KEYWORDS):
            return SchemaType.OBJECT
        if any(_has_keyword(schema, k) for k in _ARRAY_KEYWORDS):
            return SchemaType.ARRAY
        if any(_has_keyword(schema, k) for k in _STRING_KEYWORDS):
            return SchemaType.STRING
        # assume anything numeric is a number not an integer
        if any(_has_keyword(schema, k) for k in _NUMERIC_KEYWORDS):
            return SchemaType.NUMBER
        return SchemaType.UNKNOWN

    def from_enum(self, schema):
        if enum := _get_keyword(schema, "enum"):
            if len(enum) == 1:
                return enum[0]
        return _NO_VALUE

    def from_unknown(self, schema, defaults):
        if defaults is not _NO_VALUE:
            return copy.deepcopy(defaults)
        # even an unknown type can have an enum
        if (enum := self.from_enum(schema)) is not _NO_VALUE:
            return enum
        return defaults

    def from_object(self, schema, defaults):
        if defaults is _NO_VALUE:
            defaults = {}
        obj = {}
        required = _get_required(schema)
        if not required:
            return obj
        for name, subschema in _get_properties(schema):
            if name not in required:
                continue
            if (subdefaults := defaults.get(name, _NO_VALUE)) is not _NO_VALUE:
                pass
            if (value := self.build_node(subschema, subdefaults)) is _NO_VALUE:
                continue
            if name in obj and isinstance(value, dict):
                # blend the 2 dictionaries
                obj[name] |= value
            else:
                obj[name] = value
        return obj

    def from_array(self, schema, defaults):
        if defaults is _NO_VALUE:
            defaults = []
        arr = []

        min_items = _get_keyword(schema, "minItems")
        if min_items is _MISSING_KEYWORD:
            return arr

        for sub_default in defaults[:min_items]:
            arr.append(copy.deepcopy(sub_default))

        if len(arr) == min_items:
            return arr

        items_keyword = _get_keyword(schema, "items")
        if items_keyword is _MISSING_KEYWORD:
            return arr
        if isinstance(items_keyword, dict):
            item = self.build_node(items_keyword, _NO_VALUE)
            if item is _NO_VALUE:
                return arr
            for _ in range(min_items - len(arr)):
                arr.append(copy.deepcopy(item))
            return arr

        for subitem in items_keyword[len(arr) : min_items]:
            arr.append(self.build_node(subitem, _NO_VALUE))
        return arr

    def from_string(self, schema, defaults):
        if defaults is not _NO_VALUE:
            return defaults
        if (enum := self.from_enum(schema)) is not _NO_VALUE:
            return enum
        return defaults

    def from_integer(self, schema, defaults):
        if defaults is not _NO_VALUE:
            return defaults
        if (enum := self.from_enum(schema)) is not _NO_VALUE:
            return enum
        return defaults

    def from_number(self, schema, defaults):
        if defaults is not _NO_VALUE:
            return defaults
        if (enum := self.from_enum(schema)) is not _NO_VALUE:
            return enum
        return defaults

    def from_boolean(self, schema, defaults):
        if defaults is not _NO_VALUE:
            return defaults
        if (enum := self.from_enum(schema)) is not _NO_VALUE:
            return enum
        return defaults

    def from_null(self, schema, defaults):
        return None

    def from_tagged(self, schema, defaults):
        tag = _get_keyword(schema, "tag")
        if property_class := NODE_CLASSES_BY_TAG.get(tag):
            return property_class.create_minimal(defaults, builder=self)
        if defaults is not _NO_VALUE:
            return copy.deepcopy(defaults)
        return _NO_VALUE

    def build_node(self, schema, defaults):
        match self.get_type(schema):
            case SchemaType.UNKNOWN:
                return self.from_unknown(schema, defaults)
            case SchemaType.OBJECT:
                return self.from_object(schema, defaults)
            case SchemaType.ARRAY:
                return self.from_array(schema, defaults)
            case SchemaType.STRING:
                return self.from_string(schema, defaults)
            case SchemaType.INTEGER:
                return self.from_integer(schema, defaults)
            case SchemaType.NUMBER:
                return self.from_number(schema, defaults)
            case SchemaType.BOOLEAN:
                return self.from_boolean(schema, defaults)
            case SchemaType.NULL:
                return self.from_null(schema, defaults)
            case SchemaType.TAGGED:
                return self.from_tagged(schema, defaults)

    def build(self, schema, defaults=_NO_VALUE):
        if defaults is None:
            defaults = _NO_VALUE
        return self.build_node(schema, defaults)


class FakeDataBuilder(Builder):
    """
    Builder subclass that includes fake values.

    When constructing objects, values will be determined by (in this order):
        - the provided default
        - the schema value
        - a fake value

    For fake array values the optionally provided shape will be used.
    If shape is not provided a 0-sized array with the required dimensions
    will be created. If shape is provided only the dimensions that match
    the required dimensions are used.
    """

    def __init__(self, shape=None):
        super().__init__()
        self._shape = shape

    def from_enum(self, schema):
        if enum := _get_keyword(schema, "enum"):
            return enum[0]
        return _NO_VALUE

    def from_string(self, schema, defaults):
        if (value := super().from_string(schema, defaults)) is not _NO_VALUE:
            return value
        if pattern := _get_keyword(schema, "pattern"):
            if "WFI_IMAGE|" in pattern:
                # this is special cased for p_exptype
                return "WFI_IMAGE|"
        return NOSTR

    def from_unknown(self, schema, defaults):
        if (value := super().from_unknown(schema, defaults)) is not _NO_VALUE:
            return value
        if "ndim" in schema:
            # FIXME guidewindow is missing a tag for an array
            return self.from_tagged(schema, defaults)
        return _NO_VALUE

    def from_integer(self, schema, defaults):
        if (value := super().from_integer(schema, defaults)) is not _NO_VALUE:
            return value
        return int(NONUM)

    def from_number(self, schema, defaults):
        if (value := super().from_number(schema, defaults)) is not _NO_VALUE:
            return value
        return float(NONUM)

    def from_boolean(self, schema, defaults):
        if (value := super().from_boolean(schema, defaults)) is not _NO_VALUE:
            return value
        return NOBOOL

    def from_object(self, schema, defaults):
        obj = super().from_object(schema, defaults)
        if defaults:
            for k, v in defaults.items():
                if k not in obj:
                    obj[k] = copy.deepcopy(v)
        return obj

    def from_tagged(self, schema, defaults):
        tag = _get_keyword(schema, "tag")
        if tag is _MISSING_KEYWORD:
            # FIXME a guidewindow array is missing a tag
            if _get_keyword(schema, "ndim"):
                tag = "tag:stsci.edu:asdf/core/ndarray-1.*"
            else:
                return _NO_VALUE
        if property_class := NODE_CLASSES_BY_TAG.get(tag):
            # Pass control to the class for create_fake_data overrides
            return property_class.create_fake_data(defaults, builder=self)
        if defaults is not _NO_VALUE:
            return copy.deepcopy(defaults)
        if tag == "tag:stsci.edu:asdf/time/time-1.*":
            return self.make_time(schema, defaults)
        if tag == "tag:stsci.edu:asdf/core/ndarray-1.*":
            return self.make_array(schema, defaults)
        if tag == "tag:stsci.edu:gwcs/wcs-*":
            return self.make_wcs(schema, defaults)
        if tag == "tag:astropy.org:astropy/table/table-1.*":
            return self.make_table(schema, defaults)
        if tag == "tag:stsci.edu:asdf/unit/quantity-1.*":
            return self.make_quantity(schema, defaults)
        return _NO_VALUE

    def make_time(self, schema, defaults):
        from astropy.time import Time

        return Time("2020-01-01T00:00:00.0", format="isot", scale="utc")

    def make_array(self, schema, defaults):
        import numpy as np

        ndim = _get_keyword(schema, "ndim") or 0
        dtype = _get_keyword(schema, "datatype") or "float32"
        shape = [0] * ndim
        if self._shape is not None:
            for i, v in enumerate(self._shape):
                if i == len(shape):
                    break
                shape[i] = v
        return np.zeros(shape, dtype=asdf.tags.core.ndarray.asdf_datatype_to_numpy_dtype(dtype))

    def make_wcs(self, schema, defaults):
        from astropy import coordinates
        from astropy import units as u
        from astropy.modeling import models
        from gwcs import coordinate_frames
        from gwcs.wcs import WCS

        pixelshift = models.Shift(-500) & models.Shift(-500)
        pixelscale = models.Scale(0.1 / 3600.0) & models.Scale(0.1 / 3600.0)  # 0.1 arcsec/pixel
        tangent_projection = models.Pix2Sky_TAN()
        celestial_rotation = models.RotateNative2Celestial(30.0, 45.0, 180.0)

        det2sky = pixelshift | pixelscale | tangent_projection | celestial_rotation

        detector_frame = coordinate_frames.Frame2D(name="detector", axes_names=("x", "y"), unit=(u.pix, u.pix))
        sky_frame = coordinate_frames.CelestialFrame(reference_frame=coordinates.ICRS(), name="icrs", unit=(u.deg, u.deg))
        return WCS(
            [
                (detector_frame, det2sky),
                (sky_frame, None),
            ]
        )

    def make_table(self, schema, defaults):
        from astropy.table import Table

        return Table()

    def make_quantity(self, schema, defaults):
        import astropy.units as u
        import numpy as np

        props = dict(_get_properties(schema))
        unit = props.get("unit", {}).get("enum", ["dn"])[0]
        arr = self.make_array(props.get("value", {}), defaults)
        if arr.size < 2:
            # astropy will convert 1 and 0 item quantities to scalars
            # which will fail asdf validation (since these aren't arrays)
            ndim = arr.ndim or 1
            shape = [2] * ndim
            arr = np.zeros(shape, dtype=arr.dtype)
        return u.Quantity(arr, unit=unit, dtype=arr.dtype, copy=False)


class NodeBuilder(Builder):
    """
    Builder subclass that includes all provided data.

    When constructing objects, values will be copied from the
    provided defaults and converted to tags defined in the schema.
    """

    def _copy_default(self, default):
        return copy.deepcopy(default)

    def from_unknown(self, schema, defaults):
        return self._copy_default(defaults)

    def from_object(self, schema, defaults):
        if defaults is _NO_VALUE:
            return defaults

        if not isinstance(defaults, Mapping):
            return self._copy_default(defaults)

        obj = {}

        subschemas = dict(_get_properties(schema))
        for name, subdefaults in defaults.items():
            subschema = subschemas.get(name, {})
            obj[name] = self.build_node(subschema, subdefaults)
        return obj

    def from_array(self, schema, defaults):
        if defaults is _NO_VALUE:
            return defaults

        if not isinstance(defaults, Sequence) or isinstance(defaults, str):
            return self._copy_default(defaults)

        # don't consider minItem maxItems, consider items
        items_keyword = _get_keyword(schema, "items")
        if items_keyword is _MISSING_KEYWORD:
            return self._copy_default(defaults)

        if isinstance(items_keyword, dict):
            # single schema for all items
            subschemas = {}
            default_subschema = items_keyword
        else:
            # (possibly only some) items have schemas
            subschemas = dict(enumerate(items_keyword))
            default_subschema = {}

        arr = []
        for index, subitem in enumerate(defaults):
            subschema = subschemas.get(index, default_subschema)
            arr.append(self.build_node(subschema, subitem))
        return arr

    def from_string(self, schema, defaults):
        return self._copy_default(defaults)

    def from_integer(self, schema, defaults):
        return self._copy_default(defaults)

    def from_number(self, schema, defaults):
        return self._copy_default(defaults)

    def from_boolean(self, schema, defaults):
        return self._copy_default(defaults)

    def from_null(self, schema, defaults):
        return self._copy_default(defaults)

    def from_tagged(self, schema, defaults):
        tag = _get_keyword(schema, "tag")
        if property_class := NODE_CLASSES_BY_TAG.get(tag):
            try:
                return property_class.create_from_node(defaults, builder=self)
            except ValueError:
                # Providing an incompatible value (list to a dict expecting class)
                # will result in a ValueError. Don't let this stop the conversion
                # and instead let the copy below return the defaults.
                pass
        if defaults is not _NO_VALUE:
            return copy.deepcopy(defaults)
        return _NO_VALUE
