import gwcs
import numpy as np
import pytest
from astropy.table import Table
from astropy.time import Time
from astropy.units import Quantity

from roman_datamodels.stnode import SkyBackground
from roman_datamodels.stnode._schema import _NO_VALUE, Builder, FakeDataBuilder, SchemaType, _NoValueType


@pytest.mark.parametrize(
    "schema, type_",
    (
        # explicit cases
        ({}, SchemaType.UNKNOWN),
        ({"type": "object"}, SchemaType.OBJECT),
        ({"type": "array"}, SchemaType.ARRAY),
        ({"type": "string"}, SchemaType.STRING),
        ({"type": "integer"}, SchemaType.INTEGER),
        ({"type": "number"}, SchemaType.NUMBER),
        ({"type": "boolean"}, SchemaType.BOOLEAN),
        ({"type": "null"}, SchemaType.NULL),
        ({"tag": ""}, SchemaType.TAGGED),
        # fuzzy cases
        ({"properties": {}}, SchemaType.OBJECT),
        ({"items": []}, SchemaType.ARRAY),
        ({"minItems": 0}, SchemaType.ARRAY),
        ({"maxItems": 42}, SchemaType.ARRAY),
        ({"pattern": ""}, SchemaType.STRING),
        ({"minimum": 0}, SchemaType.NUMBER),
    ),
)
def test_type(schema, type_):
    assert Builder().get_type(schema) == type_


@pytest.mark.parametrize(
    "schema, defaults, expected",
    (
        ({}, None, _NO_VALUE),
        ({"enum": [0]}, None, 0),
        ({"type": "string", "enum": ["a"]}, None, "a"),
        ({"type": "integer", "enum": [0]}, None, 0),
        ({"type": "number", "enum": [3.14]}, None, 3.14),
        ({"type": "boolean", "enum": [False]}, None, False),
        ({"type": "null"}, None, None),
        ({"enum": [0, 1]}, None, _NO_VALUE),
        ({"properties": {"a": {"enum": [0]}}}, None, {}),
        ({"properties": {"a": {"enum": [0]}}, "required": ["a"]}, None, {"a": 0}),
        ({"properties": {"a": {"type": "string"}}, "required": ["a"]}, None, {}),
        ({"properties": {"a": {"type": "string"}}, "required": ["a"]}, {"a": "b"}, {"a": "b"}),
        ({"properties": {"a": {"type": "integer"}}, "required": ["a"]}, {"a": 1}, {"a": 1}),
        ({"properties": {"a": {"type": "number"}}, "required": ["a"]}, {"a": 3.14}, {"a": 3.14}),
        ({"properties": {"a": {"type": "boolean"}}, "required": ["a"]}, {"a": True}, {"a": True}),
        ({"properties": {"a": {"type": "null"}}, "required": ["a"]}, {"a": None}, {"a": None}),
        ({"properties": {"a": {}}, "required": ["a"]}, {"a": "b"}, {"a": "b"}),
        ({"properties": {"a": {"type": "string"}}}, {"a": "b"}, {}),
        (
            {"allOf": [{"properties": {"a": {}}, "required": ["a"]}, {"properties": {"b": {}}, "required": ["b"]}]},
            {"a": 0, "b": 1},
            {"a": 0, "b": 1},
        ),
        (
            {"anyOf": [{"properties": {"a": {}}, "required": ["a"]}, {"properties": {"b": {}}, "required": ["b"]}]},
            {"a": 0, "b": 1},
            {"a": 0},
        ),
        ({"items": {"enum": [0]}}, None, []),
        ({"items": {"enum": [0]}, "minItems": 1}, None, [0]),
        ({"items": [{"enum": [0]}, {"enum": [1]}], "minItems": 2}, None, [0, 1]),
        ({"items": [{"enum": [0]}, {"enum": [1]}], "minItems": 1}, None, [0]),
        ({"items": [{"enum": [0]}], "minItems": 2}, None, [0]),
        ({"items": [{"enum": [0]}], "minItems": 2}, None, [0]),
        ({"minItems": 1}, [0, 1], [0]),
        ({"minItems": 2}, [0, 1], [0, 1]),
        ({"minItems": 3}, [0, 1], [0, 1]),
        ({"minItems": 3, "items": [{"enum": [42]}]}, [0, 1], [0, 1]),
        ({"minItems": 3, "items": {"enum": [42]}}, [0, 1], [0, 1, 42]),
        ({"minItems": 2, "items": {"enum": [42]}}, [0, 1], [0, 1]),
    ),
)
def test_build(schema, defaults, expected):
    assert Builder().build(schema, defaults) == expected


@pytest.mark.parametrize(
    "subschema, data",
    (
        ({"type": "array"}, [1, 2, 3]),
        ({"type": "object"}, {"foo": "bar"}),
        ({"tag": "tag:stsci.edu:asdf/core/ndarray-1.*"}, np.zeros([], dtype="uint8")),
    ),
)
def test_default_is_copied(subschema, data):
    """Test that default values are copied not referenced"""
    schema = {
        "properties": {
            "a": subschema,
        },
        "required": ["a"],
    }
    obj = Builder().build(schema, {"a": data})
    assert obj["a"] is not data


@pytest.mark.parametrize(
    "tag, expected_type",
    (
        # non-rad tags
        ("tag:stsci.edu:asdf/time/time-1.*", _NoValueType),
        ("tag:stsci.edu:asdf/core/ndarray-1.*", _NoValueType),
        ("tag:stsci.edu:gwcs/wcs-*", _NoValueType),
        ("tag:astropy.org:astropy/table/table-1.*", _NoValueType),
        ("tag:stsci.edu:asdf/unit/quantity-1.*", _NoValueType),
        # unknown tag
        ("abc", _NoValueType),
        # test one rad tag to not make this test dependent on NODE_CLASSES_BY_TAG
        ("asdf://stsci.edu/datamodels/roman/tags/sky_background-1.0.0", SkyBackground),
    ),
)
def test_tag(tag, expected_type):
    """Test that a schema with a tag produces the object with that tag"""
    schema = {
        "tag": tag,
    }
    assert isinstance(Builder().build(schema), expected_type)


@pytest.mark.parametrize(
    "tag, expected_type",
    (
        # non-rad tags
        ("tag:stsci.edu:asdf/time/time-1.*", Time),
        ("tag:stsci.edu:asdf/core/ndarray-1.*", np.ndarray),
        ("tag:stsci.edu:gwcs/wcs-*", gwcs.WCS),
        ("tag:astropy.org:astropy/table/table-1.*", Table),
        ("tag:stsci.edu:asdf/unit/quantity-1.*", Quantity),
        # unknown tag
        ("abc", _NoValueType),
        # test one rad tag to not make this test dependent on NODE_CLASSES_BY_TAG
        ("asdf://stsci.edu/datamodels/roman/tags/sky_background-1.0.0", SkyBackground),
    ),
)
def test_fake_tag(tag, expected_type):
    """Test that a schema with a tag produces the object with that tag"""
    schema = {
        "tag": tag,
    }
    assert isinstance(FakeDataBuilder().build(schema), expected_type)


@pytest.mark.parametrize(
    "ndim, shape, expected",
    (
        (None, None, tuple()),
        (1, None, (0,)),
        (2, None, (0, 0)),
        (None, (10, 20, 30), tuple()),
        (1, (10, 20, 30), (10,)),
        (2, (10, 20, 30), (10, 20)),
        (3, (10, 20, 30), (10, 20, 30)),
        (4, (10, 20, 30), (10, 20, 30, 0)),
    ),
)
def test_array_shape(ndim, shape, expected):
    """Test that providing a shape still respcts ndim"""
    schema = {
        "tag": "tag:stsci.edu:asdf/core/ndarray-1.*",
    }
    if ndim is not None:
        schema["ndim"] = ndim
    arr = FakeDataBuilder(shape=shape).build(schema)
    assert arr.shape == expected
