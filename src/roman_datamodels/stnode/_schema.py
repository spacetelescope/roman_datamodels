"""
Code for relating nodes and schema.
"""

import copy
import enum
import functools

import asdf

from ._registry import (
    NODE_CLASSES_BY_TAG,
    SCHEMA_URIS_BY_TAG,
)

__all__ = []


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
    def __bool__(self):
        return False


_MISSING_KEYWORD = _MissingKeywordType()


def _get_keyword(schema, key):
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
    return _get_keyword(schema, key) != _MISSING_KEYWORD


def _get_properties(schema):
    if "allOf" in schema:
        for subschema in schema["allOf"]:
            yield from _get_properties(subschema)
    elif "anyOf" in schema:
        yield from _get_properties(schema["anyOf"][0])
    elif "properties" in schema:
        yield from schema["properties"].items()


def _get_required(schema, required=None):
    required = required or set()
    if "required" in schema:
        required.update(set(schema["required"]))
    if "allOf" in schema:
        for subschema in schema["allOf"]:
            required.update(_get_required(subschema))
    if "anyOf" in schema:
        required.uupdate(_get_required(schema["anyOf"][0]))
    return required


class _NoValueType:
    def __bool__(self):
        return False


_NO_VALUE = _NoValueType()


class SchemaType(enum.Enum):
    UNKNOWN = 0
    OBJECT = 1
    ARRAY = 2
    STRING = 3
    INTEGER = 4
    NUMBER = 5
    BOOLEAN = 6
    NULL = 7
    TAGGED = 8


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
        required = _get_required(schema) | defaults.keys()
        if not required:
            return obj
        for name, subschema in _get_properties(schema):
            if name not in required:
                continue
            if (subdefaults := defaults.get(name, _NO_VALUE)) is not _NO_VALUE:
                # TODO remove any DNode/LNode
                pass
            if (value := self.build_node(subschema, subdefaults)) is _NO_VALUE:
                continue
            if name in obj:
                if type(obj[name]) is not type(value):
                    raise Exception("Failed to parse value")
                elif isinstance(value, dict):
                    # blend the 2 dictionaries
                    obj[name] |= value
                elif isinstance(value, str):
                    if value == "?":
                        continue
                    obj[name] = value
                else:
                    raise Exception("Failed to parse value")
            else:
                obj[name] = value
        return obj

    def from_array(self, schema, defaults):
        if defaults is not _NO_VALUE:
            return copy.deepcopy(defaults)
        # TODO minItems maxItems is unused so all arrays can be empty
        return []

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
        if tag is _MISSING_KEYWORD:
            return _NO_VALUE
        if property_class := NODE_CLASSES_BY_TAG.get(tag):
            return property_class.from_schema(defaults, builder=self)
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
        return _NO_VALUE

    def build(self, schema, defaults=_NO_VALUE):
        if defaults is None:
            defaults = _NO_VALUE
        return self.build_node(schema, defaults)


class FakeDataBuilder(Builder):
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
        if _has_keyword(schema, "pattern"):
            # TODO this is brittle
            return "WFI_IMAGE|"
        return "?"

    def from_unknown(self, schema, defaults):
        if (value := super().from_unknown(schema, defaults)) is not _NO_VALUE:
            return value
        if "ndim" in schema:
            # TODO guidewindow is missing a tag for an array
            return self.from_tagged(schema, defaults)
        return _NO_VALUE

    def from_integer(self, schema, defaults):
        if (value := super().from_integer(schema, defaults)) is not _NO_VALUE:
            return value
        return -999999

    def from_number(self, schema, defaults):
        if (value := super().from_number(schema, defaults)) is not _NO_VALUE:
            return value
        return -999999.0

    def from_boolean(self, schema, defaults):
        if (value := super().from_boolean(schema, defaults)) is not _NO_VALUE:
            return value
        return False

    def from_tagged(self, schema, defaults):
        tag = _get_keyword(schema, "tag")
        if tag is _MISSING_KEYWORD:
            # TODO a guidewindow array is missing a tag
            if _get_keyword(schema, "ndim"):
                tag = "tag:stsci.edu:asdf/core/ndarray-1.*"
            else:
                return _NO_VALUE
        if property_class := NODE_CLASSES_BY_TAG.get(tag):
            # Pass control to the class for fake_data overrides
            return property_class.fake_data(defaults, builder=self)
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

        props = schema.get("properties", {})
        unit = props.get("unit", {}).get("enum", ["dn"])[0]
        arr = self.make_array(props.get("value", {}), defaults)
        if arr.size < 2:
            # astropy will convert 1 and 0 item quantities to scalars
            # which will fail asdf validation (since these aren't arrays)
            ndim = arr.ndim or 1
            shape = [2] * ndim
            arr = np.zeros(shape, dtype=arr.dtype)
        return u.Quantity(arr, unit=unit, dtype=arr.dtype, copy=False)
