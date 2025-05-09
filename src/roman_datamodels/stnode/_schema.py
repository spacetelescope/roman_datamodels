"""
Code for relating nodes and schema.
"""

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


def _is_object(schema):
    match _get_keyword(schema, "type"):
        case "object":
            return True
        case _MissingKeywordType():
            pass
        case _:
            return False
    for keyword in (
        "properties",
        "patternProperties",
        "required",
        "additionalProperties",
        "maxProperties",
        "minProperties",
        "dependencies",
    ):
        if _has_keyword(schema, keyword):
            return True
    return False


def _is_array(schema):
    match _get_keyword(schema, "type"):
        case "array":
            return True
        case _MissingKeywordType():
            pass
        case _:
            return False
    for keyword in ("items", "additionalItems", "maxItems", "minItems", "uniqueItems"):
        if _has_keyword(schema, keyword):
            return True
    return False


def _is_string(schema):
    match _get_keyword(schema, "type"):
        case "string":
            return True
        case _MissingKeywordType():
            pass
        case _:
            return False
    if _get_keyword(schema, "type") == "string":
        return True
    for keyword in ("pattern", "minLength", "maxLength"):
        if _has_keyword(schema, keyword):
            return True
    return False


def _is_numeric(schema):
    for keyword in ("multipleOf", "maximum", "exclusiveMaximum", "minimum", "exclusiveMaximum"):
        if _has_keyword(schema, keyword):
            return True
    return False


def _is_number(schema):
    match _get_keyword(schema, "type"):
        case "number":
            return True
        case _MissingKeywordType():
            pass
        case _:
            return False
    return _is_numeric(schema)


def _is_integer(schema):
    match _get_keyword(schema, "type"):
        case "integer":
            return True
        case _MissingKeywordType():
            pass
        case _:
            return False
    return _is_numeric(schema)


def _is_boolean(schema):
    return _get_keyword(schema, "type") == "boolean"


def _is_null(schema):
    return _get_keyword(schema, "type") == "null"


class _NoValueType:
    def __bool__(self):
        return False


_NO_VALUE = _NoValueType()


def _from_tag(schema, tag=None):
    tag = tag or _get_keyword(schema, "tag")
    if property_class := NODE_CLASSES_BY_TAG.get(tag):
        if hasattr(property_class, "_fake_data"):
            return property_class._fake_data()
        return property_class(_from_schema(_get_schema_from_tag(tag)))
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

    raise Exception("Failed to parse value")
    return _NO_VALUE


def _from_object(schema):
    obj = {}
    required = _get_required(schema)
    if not required:
        return obj
    for name, subschema in _get_properties(schema):
        if name not in required:
            continue
        value = _from_schema(subschema)
        if value is _NO_VALUE:
            # guidewindow is missing a tag
            if "ndim" in subschema:
                value = _from_tag(subschema, "tag:stsci.edu:asdf/core/ndarray-1.*")
            else:
                raise Exception("Failed to parse value")
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


def _from_array(schema):
    # TODO minItems maxItems is unused so all arrays can be empty
    return []


def _from_string(schema):
    if enum := _get_keyword(schema, "enum"):
        return enum[0]
    if _ := _get_keyword(schema, "pattern"):
        # TODO this is brittle
        return "WFI_IMAGE|"
    return "?"


def _from_number(schema):
    if enum := _get_keyword(schema, "enum"):
        return enum[0]
    return -999999.0


def _from_integer(schema):
    if enum := _get_keyword(schema, "enum"):
        return enum[0]
    return -999999


def _from_boolean(schema):
    if enum := _get_keyword(schema, "enum"):
        return enum[0]
    return False


def _from_null(schema):
    return None


def _from_schema(schema):
    if _ := _get_keyword(schema, "tag"):
        return _from_tag(schema)
    if _is_object(schema):
        return _from_object(schema)
    if _is_array(schema):
        return _from_array(schema)
    if _is_string(schema):
        return _from_string(schema)
    if _is_number(schema):
        return _from_number(schema)
    if _is_integer(schema):
        return _from_integer(schema)
    if _is_boolean(schema):
        return _from_boolean(schema)
    if _is_null(schema):
        return _from_null(schema)
    if enum := _get_keyword(schema, "enum"):
        return enum[0]
    return _NO_VALUE


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
                if _is_object(subschema):
                    # TODO maybe DNode and LNode should have a from_schema?
                    node[name] = _node_from_schema(DNode, subschema)
                elif _is_array(subschema):
                    node[name] = _node_from_schema(LNode, subschema)
                else:
                    # TODO reference frame is a single item enum, make this
                    pass
    elif isinstance(node, LNode):
        pass  # TODO list?
    return node
