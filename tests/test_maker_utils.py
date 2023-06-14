import asdf
import pytest

from roman_datamodels import datamodels, maker_utils, stnode
from roman_datamodels.maker_utils import _ref_files as ref_files


@pytest.mark.parametrize("node_class", stnode.NODE_CLASSES)
def test_maker_utility_implemented(node_class):
    """
    Confirm that a subclass of TaggedObjectNode has a maker utility.
    """
    instance = maker_utils.mk_node(node_class)
    assert isinstance(instance, node_class)


@pytest.mark.parametrize("node_class", stnode.NODE_CLASSES)
def test_instance_valid(node_class):
    """
    Confirm that a class's maker utility creates an object that
    is valid against its schema.
    """
    with asdf.AsdfFile() as af:
        af["node"] = maker_utils.mk_node(node_class)
        af.validate()


@pytest.mark.parametrize("node_class", [c for c in stnode.NODE_CLASSES if issubclass(c, stnode.TaggedObjectNode)])
def test_no_extra_fields(node_class, manifest):
    instance = maker_utils.mk_node(node_class)
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
    assert len(diff) == 0, "Dummy instance has extra keys: " + ", ".join(diff)


@pytest.mark.parametrize("name", [c.__name__ for c in stnode.NODE_CLASSES if c.__name__.endswith("Ref")])
def test_ref_files_all(name):
    """
    Meta test to confirm that the __all__ in _ref_files.py has an entry for every ref file maker.
    """
    from roman_datamodels.testing.factories import _camel_case_to_snake_case

    method_name = "mk_" + _camel_case_to_snake_case(name)
    assert method_name[:-4] in ref_files.__all__


@pytest.mark.parametrize("util", [c.__name__ for c in datamodels.MODEL_REGISTRY])
def test_make_datamodel_tests(util):
    """
    Meta test to confirm that correct tests exist for each datamodel maker utility.
    """
    from roman_datamodels.testing.factories import _camel_case_to_snake_case

    from . import test_models as tests

    name = maker_utils.SPECIAL_MAKERS.get(util, _camel_case_to_snake_case(util))
    if name.startswith("mk_"):
        name = name[3:]
    if name.endswith("_ref"):
        name = name[:-4]

    assert hasattr(tests, f"test_make_{name}"), name
    assert hasattr(tests, f"test_opening_{name}_ref")


def test_deprecated():
    """
    mk_rampfitoutput has been deprecated because its name is inconsistent with the other
    maker utilities.  Confirm that it raises a DeprecationWarning.
    """

    with pytest.warns(DeprecationWarning):
        maker_utils.mk_rampfitoutput()


@pytest.mark.parametrize("model_class", [mdl for mdl in maker_utils.NODE_REGISTRY])
def test_datamodel_maker(model_class):
    """
    Test that the datamodel maker utility creates a valid datamodel.
    """

    model = maker_utils.mk_datamodel(model_class)

    assert isinstance(model, model_class)
    model.validate()
