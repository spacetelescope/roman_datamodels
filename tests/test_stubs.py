import asdf
import pytest

from roman_datamodels import stnode
from roman_datamodels._typing import maker

NUM_ITERATIONS = 3


def _get_schema(tag):
    schema_uri = asdf.AsdfFile().extension_manager.get_tag_definition(tag["tag_uri"]).schema_uris[0]

    return asdf.schema.load_schema(schema_uri, resolve_references=True)


def _get_name(tag):
    return stnode._class_name_from_tag_uri(tag["tag_uri"])


SCHEMAS = {_get_name(tag): _get_schema(tag) for tag in stnode._DATAMODELS_MANIFEST["tags"]}


def _tag_object(tree):
    ctx = asdf.AsdfFile()
    return asdf.yamlutil.custom_tree_to_tagged_tree(tree, ctx)


def test_check_names():
    """test that all the tagged schemas have a corresponding node and stub"""
    schemas = set(SCHEMAS.keys())
    nodes = set(maker.NODE_CLASSES_BY_NAME.keys())
    stubs = set(maker.STUB_CLASSES_BY_NAME.keys())

    assert schemas == nodes
    assert schemas.issubset(stubs), f"Missing stubs for {schemas - stubs}"


def test_enum_names():
    """
    test the enum class names only overlap with the stubs when the class name matches
        a tagged scalar class.
    """
    enums = set(maker.ENUM_CLASSES_BY_NAME.keys())
    stubs = set(maker.STUB_CLASSES_BY_NAME.keys())
    scalar = set(maker.SCALAR_CLASSES_BY_NAME.keys())

    assert enums.intersection(stubs).issubset(scalar)


@pytest.mark.parametrize("name", SCHEMAS.keys())
def test_stub_is_valid(name):
    """
    Test generating an object from the stub for each tagged schema and then
        validating it against the schema.
    """
    # Create the object from stub multiple times to make sure it works
    # this is because it is randomly generated and may follow different
    # creation paths each time
    for _ in range(NUM_ITERATIONS):
        tree = _tag_object(maker.create_stub(maker.STUB_CLASSES_BY_NAME[name]))
        asdf.schema.validate(tree, schema=SCHEMAS[name])


@pytest.mark.parametrize(
    "stub", [maker.STUB_CLASSES_BY_NAME[c.__name__] for c in stnode.NODE_CLASSES if issubclass(c, stnode.TaggedObjectNode)]
)
def test_no_extra_stub_fields(stub, manifest):
    instance = maker.create_stub(stub)
    instance_keys = set(instance.keys())

    schema_uri = next(t["schema_uri"] for t in manifest["tags"] if t["tag_uri"] == instance.tag)
    schema = asdf.schema.load_schema(schema_uri, resolve_references=True)

    schema_keys = set()
    subschemas = [schema]
    if "allOf" in schema:
        subschemas.extend(schema["allOf"])
    for subschema in subschemas:
        schema_keys.update(subschema.get("properties", {}).keys())

    diff = instance_keys - schema_keys
    assert len(diff) == 0, "Factory instance has extra keys: " + ", ".join(diff)
