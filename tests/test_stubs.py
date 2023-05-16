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
    schemas = set(SCHEMAS.keys())
    nodes = set(maker.NODE_CLASSES_BY_NAME.keys())
    stubs = set(maker.STUB_CLASSES_BY_NAME.keys())

    assert schemas == nodes
    assert schemas.issubset(stubs), f"Missing stubs for {schemas - stubs}"


@pytest.mark.parametrize("name", SCHEMAS.keys())
def test_stub(name):
    # Create the object from stub multiple times to make sure it works
    # this is because it is randomly generated and may follow different
    # creation paths each time
    for _ in range(NUM_ITERATIONS):
        tree = _tag_object(maker.create_stub(maker.STUB_CLASSES_BY_NAME[name]))
        asdf.schema.validate(tree, schema=SCHEMAS[name])
