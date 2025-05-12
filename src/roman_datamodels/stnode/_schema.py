"""
Code for relating nodes and schema.
"""

import enum
import functools

import asdf

from ._node import DNode, LNode
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


def _node_from_schema(node_class, schema=None):
    if schema is None:
        schema = _get_schema_from_tag(node_class._default_tag)
    node = node_class()
    if isinstance(node, DNode):
        for name, subschema in _get_properties(schema):
            # TODO handle recursion for tag
            if tag := subschema.get("tag"):
                if property_class := NODE_CLASSES_BY_TAG.get(tag):
                    if hasattr(property_class, "from_schema"):
                        node[name] = property_class.from_schema()
                else:
                    if "roman" in tag:
                        # TODO for "fake" make these
                        pass
            else:
                node_type = _get_keyword(subschema, "type")
                if node_type == "object":
                    # TODO maybe DNode and LNode should have a from_schema?
                    node[name] = _node_from_schema(DNode, subschema)
                if node_type == "array":
                    node[name] = _node_from_schema(LNode, subschema)
    elif isinstance(node, LNode):
        pass  # TODO list?
    return node


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

_OBJECT_KEYWORDS = {"properties", "patternProperties", "required", "additionalProperties", "maxProperties", "minProperties", "dependencies"}
_ARRAY_KEYWORDS = {"items", "additionalItems", "maxItems", "minItems", "uniqueItems"}
_STRING_KEYWORDS = {"pattern", "minLength", "maxLength"}
_NUMERIC_KEYWORDS = {"multipleOf", "maximum", "exclusiveMaximum", "minimum", "exclusiveMaximum"}


def _get_type(schema):
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


class Builder:
    def __init__(self, schema, defaults=None):
        self._schema = schema
        self._defaults = defaults

    def get_type(self, schema):
        return _get_type(schema)

    def from_enum(self, schema):
        if enum := _get_keyword(schema, "enum"):
            return enum[0]
        return _NO_VALUE

    def from_unknown(self, schema):
        # even an unknown type can have an enum
        if (enum := self.from_enum(schema)) is not _NO_VALUE:
            return enum
        if "ndim" in schema:
            # TODO guidewindow is missing a tag for an array
            return self.from_tagged(schema)
        return self.from_enum(schema)

    def from_object(self, schema):
        obj = {}
        required = _get_required(schema)
        if not required:
            return obj
        for name, subschema in _get_properties(schema):
            if name not in required:
                continue
            if (value := self.build_node(subschema)) is _NO_VALUE:
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

    def from_array(self, schema):
        # TODO minItems maxItems is unused so all arrays can be empty
        return []

    def from_string(self, schema):
        if (enum := self.from_enum(schema)) is not _NO_VALUE:
            return enum
        if _has_keyword(schema, "pattern"):
            # TODO this is brittle
            return "WFI_IMAGE|"
        return "?"


    def from_integer(self, schema):
        if (enum := self.from_enum(schema)) is not _NO_VALUE:
            return enum
        return -999999

    def from_number(self, schema):
        if (enum := self.from_enum(schema)) is not _NO_VALUE:
            return enum
        return -999999.0

    def from_boolean(self, schema):
        if (enum := self.from_enum(schema)) is not _NO_VALUE:
            return enum
        return False

    def from_null(self, schema):
        pass

    def from_tagged(self, schema):
        tag = _get_keyword(schema, "tag")
        if tag is _MISSING_KEYWORD:
            # TODO a guidewindow array is missing a tag
            if _get_keyword(schema, "ndim"):
                tag = "tag:stsci.edu:asdf/core/ndarray-1.*"
            else:
                return _NO_VALUE
        if property_class := NODE_CLASSES_BY_TAG.get(tag):
            if hasattr(property_class, "_fake_data"):
                return property_class._fake_data()
            # TODO this is calling build_node with a different schema
            return property_class(self.build_node(_get_schema_from_tag(tag)))
        if tag == "tag:stsci.edu:asdf/time/time-1.*":
            from astropy.time import Time

            return Time("2020-01-01T00:00:00.0", format="isot", scale="utc")
        if tag == "tag:stsci.edu:asdf/core/ndarray-1.*":
            import numpy as np

            ndim = _get_keyword(schema, "ndim") or 0
            dtype = _get_keyword(schema, "datatype") or "float32"
            return np.zeros([0] * ndim, dtype=asdf.tags.core.ndarray.asdf_datatype_to_numpy_dtype(dtype))
        if tag == "tag:stsci.edu:gwcs/wcs-*":
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
        if tag == "tag:astropy.org:astropy/table/table-1.*":
            from astropy.table import Table

            return Table()
        if tag == "tag:stsci.edu:asdf/unit/quantity-1.*":
            import astropy.units as u
            import numpy as np

            props = schema.get("properties", {})
            value = props.get("value", {})
            dtype = value.get("datatype", "float32")
            dtype = asdf.tags.core.ndarray.asdf_datatype_to_numpy_dtype(dtype)
            unit = props.get("unit", {}).get("enum", ["dn"])[0]
            ndim = value.get("ndim", 1)
            arr = np.zeros([2] * ndim, dtype=dtype)
            # astropy forces 1 item arrays to scalars and dtypes to float64 so define
            # extra stuff here to prevent Quantity from failing validation
            return u.Quantity(arr, unit=unit, dtype=dtype)

        return _NO_VALUE

    def build_node(self, schema):
        match self.get_type(schema):
            case SchemaType.UNKNOWN:
                return self.from_unknown(schema)
            case SchemaType.OBJECT:
                return self.from_object(schema)
            case SchemaType.ARRAY:
                return self.from_array(schema)
            case SchemaType.STRING:
                return self.from_string(schema)
            case SchemaType.INTEGER:
                return self.from_integer(schema)
            case SchemaType.NUMBER:
                return self.from_number(schema)
            case SchemaType.BOOLEAN:
                return self.from_boolean(schema)
            case SchemaType.NULL:
                return self.from_null(schema)
            case SchemaType.TAGGED:
                return self.from_tagged(schema)
        return _NO_VALUE

    def build(self):
        return self.build_node(self._schema)
