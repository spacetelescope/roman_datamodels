import asdf
import pytest

from roman_datamodels.testing import create_node
from roman_datamodels import stnode


@pytest.mark.parametrize("node_class", stnode.NODE_CLASSES)
def test_factory_method_implemented(node_class):
    """
    Confirm that a subclass of TaggedObjectNode has a factory method
    available.
    """
    instance = create_node(node_class)
    assert isinstance(instance, node_class)


@pytest.mark.parametrize("node_class", stnode.NODE_CLASSES)
def test_instance_valid(node_class):
    """
    Confirm that a class's factory method creates an object that
    is valid against its schema.
    """
    with asdf.AsdfFile() as af:
        af["node"] = create_node(node_class)
        af.validate()


@pytest.mark.parametrize("node_class", stnode.NODE_CLASSES)
def test_no_extra_fields(node_class, manifest):
    instance = create_node(node_class)
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
