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
    if node_class.__name__ == "KeywordPixelarea":
        pytest.xfail("No schema for KeywordPixelarea, see https://github.com/spacetelescope/rad/issues/11")

    instance = create_node(node_class)
    assert isinstance(instance, node_class)


@pytest.mark.parametrize("node_class", stnode.NODE_CLASSES)
def test_instance_valid(node_class):
    """
    Confirm that a class's factory method creates an object that
    is valid against its schema.
    """
    if node_class.__name__ == "KeywordPixelarea":
        pytest.xfail("No schema for KeywordPixelarea, see https://github.com/spacetelescope/rad/issues/11")

    with asdf.AsdfFile() as af:
        af["node"] = create_node(node_class)
        af.validate()
