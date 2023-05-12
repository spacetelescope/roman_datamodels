import inspect

import asdf
import pytest
from astropy.time import Time
from astropy.units import Quantity, Unit
from mypy import nodes, options, parse

from roman_datamodels import stnode


def _get_tag_for_type(type_):
    converter = asdf.AsdfFile().extension_manager.get_converter_for_type(type_)
    return converter.tags


TYPES = {
    "integer": "int",
    "number": "float",
    "string": "str",
    "boolean": "bool",
}


EXTERNAL_TAGGED_TYPES = [Quantity, Unit, Time]


def _external_tagged_types():
    return {t.__name__: _get_tag_for_type(t) for t in EXTERNAL_TAGGED_TYPES}


TAGGED_TYPES = _external_tagged_types()


def _parse_stubs():
    path = f"{inspect.getfile(stnode)}i"
    module = stnode.__name__
    options_ = options.Options()

    with open(path) as f:
        source = f.read()

    return parse.parse(source, path, module, None, options_)


def _class_stubs():
    stubs = _parse_stubs()
    return [c for c in stubs.defs if isinstance(c, nodes.ClassDef)]


def _get_schema(tag):
    tag_uri = tag["tag_uri"]
    schema_uri = asdf.AsdfFile().extension_manager.get_tag_definition(tag_uri).schema_uris[0]

    return asdf.schema.load_schema(schema_uri, resolve_references=True)


def _schemas():
    schemas = {}
    for tag in stnode._DATAMODELS_MANIFEST["tags"]:
        name = stnode._class_name_from_tag_uri(tag["tag_uri"])
        schema = _get_schema(tag)
        schemas[name] = schema

    return schemas


def _stubs():
    return {c.name: c for c in _class_stubs()}


def _classes():
    return {c.__name__: c for c in stnode.NODE_CLASSES}


STUBS = _stubs()
SCHEMAS = _schemas()
INTERMEDIATE_STUBS = {k: v for k, v in STUBS.items() if k not in SCHEMAS}
CLASSES = _classes()


def test_check_names():
    schemas = set(SCHEMAS.keys())
    classes = set(CLASSES.keys())
    stubs = set(STUBS.keys())

    assert schemas == classes
    assert schemas.issubset(stubs), f"Missing stubs for {schemas - stubs}"


def _get_stub(name, stubs):
    stub = stubs[name]
    type_name = stub.type.name

    return INTERMEDIATE_STUBS.get(type_name, None) or stub


def _check_stub(name, schema, stubs):
    stub = _get_stub(name, stubs)
    try:
        type_name = stub.type.name
    except AttributeError:
        new_stubs = {b.lvalues[0].name: b for b in stub.defs.body}
    else:
        new_stubs = {}

    tag = schema.get("tag", None)
    if tag:
        assert tag in TAGGED_TYPES[type_name], f"Missing tag for {type_name}"

    type_ = schema.get("type", None)
    if type_:
        assert type_name == TYPES[type_], f"Missing type for {type_name}"

    all_of = schema.get("allOf", None)
    if all_of:
        if new_stubs:
            for subschema in all_of:
                _check_object_stub(subschema, new_stubs)
        else:
            raise ValueError(f"Missing stub for {name}")


def _check_object_stub(schema, body):
    properties = schema.get("properties", {})
    for name, subschema in properties.items():
        _check_stub(name, subschema, body)


@pytest.mark.parametrize("name", SCHEMAS.keys())
def test_class(name):
    schema = SCHEMAS[name]
    stub = STUBS[name]
    class_ = CLASSES[name]

    if issubclass(class_, stnode.TaggedObjectNode):
        properties = schema.get("properties", {})
        body = {b.lvalues[0].name: b for b in stub.defs.body}

        attributes = set(properties.keys())
        names = set(body.keys())
        print("Checking attributes:")
        for name in attributes:
            print(f"    attribute {name}")
            assert name in names, f"Missing attribute {name}"
        print("Checking stubs:")
        for name in names:
            print(f"    stub {name}")
            assert name in attributes, f"Extra attribute {name}"
        # assert attributes == names

        # _check_object_stub(schema, body)
    else:
        raise ValueError(f"Unknown class {name}")
