from contextlib import nullcontext

import asdf
import pytest

from roman_datamodels import _stnode as stnode
from roman_datamodels import datamodels
from roman_datamodels.testing import assert_node_equal, assert_node_is_copy, wraps_hashable

from .conftest import MANIFESTS


@pytest.mark.parametrize("tag_def", [tag_def for manifest in MANIFESTS for tag_def in manifest["tags"]])
def test_tag_has_node_class(tag_def):
    class_name = stnode._factories.class_name_from_tag_uri(tag_def["tag_uri"])
    node_class = getattr(stnode, class_name)

    assert asdf.util.uri_match(node_class._pattern, tag_def["tag_uri"])
    if node_class._default_tag == tag_def["tag_uri"]:
        assert tag_def["description"] in node_class.__doc__
        assert tag_def["tag_uri"] in node_class.__doc__
    else:
        default_tag_version = node_class._default_tag.rsplit("-", maxsplit=1)[1]
        tag_def_version = tag_def["tag_uri"].rsplit("-", maxsplit=1)[1]
        assert asdf.versioning.Version(default_tag_version) > asdf.versioning.Version(tag_def_version)


@pytest.mark.parametrize("node_class", stnode.NODE_CLASSES)
def test_node_classes_available_via_stnode(node_class):
    assert issubclass(node_class, stnode.TaggedObjectNode | stnode.TaggedListNode | stnode.TaggedScalarNode)
    assert node_class.__module__ == stnode.__name__
    assert hasattr(stnode, node_class.__name__)


@pytest.mark.parametrize("node_class", stnode.NODE_CLASSES)
def test_copy(node_class):
    """Demonstrate nodes can copy themselves, but don't always deepcopy."""
    node = node_class.create_fake_data()
    node_copy = node.copy()

    # Assert the copy is shallow:
    assert_node_is_copy(node, node_copy, deepcopy=False)

    # If the node only wraps hashable values, then it should "deepcopy" itself because
    # the immutable values cannot actually be copied. In the case, where there is an
    # unhashable value, then the node should not deepcopy itself.
    with nullcontext() if wraps_hashable(node) else pytest.raises(AssertionError):
        assert_node_is_copy(node, node_copy, deepcopy=True)


@pytest.mark.parametrize("model_class", datamodels.MODEL_REGISTRY.values())
def test_deepcopy_model(model_class):
    model = model_class.create_fake_data(shape=(8, 8, 8))
    model_copy = model.copy()

    # There is no assert equal for models, but the data inside is what we care about.
    # this is stored under the _instance attribute. We can assert those instances are
    # deep copies of each other.
    assert_node_is_copy(model._instance, model_copy._instance, deepcopy=True)


def test_wfi_mode():
    """
    The WfiMode class includes special properties that map optical_element
    values to grating or filter.
    """
    node = stnode.WfiMode({"optical_element": "GRISM"})
    assert node.optical_element == "GRISM"
    assert node.grating == "GRISM"
    assert node.filter is None
    assert isinstance(node, stnode.DNode)
    assert isinstance(node, stnode._mixins.WfiModeMixin)

    node = stnode.WfiMode({"optical_element": "PRISM"})
    assert node.optical_element == "PRISM"
    assert node.grating == "PRISM"
    assert node.filter is None
    assert isinstance(node, stnode.DNode)
    assert isinstance(node, stnode._mixins.WfiModeMixin)

    node = stnode.WfiMode({"optical_element": "F129"})
    assert node.optical_element == "F129"
    assert node.grating is None
    assert node.filter == "F129"
    assert isinstance(node, stnode.DNode)
    assert isinstance(node, stnode._mixins.WfiModeMixin)


@pytest.mark.parametrize("node_class", stnode.NODE_CLASSES)
def test_serialization(node_class, tmp_path):
    file_path = tmp_path / "test.asdf"

    node = node_class.create_fake_data()
    with asdf.AsdfFile() as af:
        af["node"] = node
        af.write_to(file_path)

    with asdf.open(file_path) as af:
        assert_node_equal(af["node"], node)


@pytest.mark.parametrize("node_class", [cls for cls in stnode.NODE_CLASSES if issubclass(cls, stnode.TaggedObjectNode)])
def test_no_hidden(node_class):
    node = node_class.create_fake_data()
    with pytest.raises(AttributeError, match=r"Cannot set private attribute.*"):
        node._foo = "bar"  # Add a hidden attribute


@pytest.mark.parametrize("node_class", [cls for cls in stnode.NODE_CLASSES if issubclass(cls, stnode.TaggedListNode)])
def test_list_node_no_new_attributes(node_class):
    """Test that no new attributes can be added to a list node."""
    node = node_class.create_fake_data()
    with pytest.raises(AttributeError, match=r"Cannot set attribute .*, only allowed are .*"):
        node.foo = "bar"

    with pytest.raises(AttributeError, match=r"Cannot set attribute .*, only allowed are .*"):
        node._foo = "bar"


@pytest.mark.parametrize(
    "node_class", [cls for cls in stnode.NODE_CLASSES if issubclass(cls, stnode.TaggedObjectNode | stnode.TaggedListNode)]
)
def test_slotted(node_class):
    """
    Test that slotted nodes do not allow new attributes to be added.
    """
    node = node_class.create_fake_data()
    with pytest.raises(AttributeError, match=r".* attribute .*__dict__.*"):
        # Attempt to access __dict__ directly, slotted classes do not have __dict__
        node.__dict__  # noqa: B018


def test_info(capsys):
    node = stnode.WfiMode({"optical_element": "GRISM", "detector": "WFI18", "name": "WFI"})
    tree = dict(wfimode=node)
    af = asdf.AsdfFile(tree)
    af.info()
    captured = capsys.readouterr()
    assert "optical_element" in captured.out
    assert "GRISM" in captured.out


def test_schema_info():
    node = stnode.WfiMode({"optical_element": "GRISM", "detector": "WFI18", "name": "WFI"})
    tree = dict(wfimode=node)
    af = asdf.AsdfFile(tree)

    info = af.schema_info("archive_catalog")
    assert info == {
        "wfimode": {
            "detector": {
                "archive_catalog": (
                    {
                        "datatype": "nvarchar(10)",
                        "destination": ["WFIExposure.detector", "GuideWindow.detector", "WFICommon.detector"],
                    },
                    "WFI18",
                )
            },
            "name": {
                "archive_catalog": (
                    {
                        "datatype": "nvarchar(5)",
                        "destination": [
                            "WFIExposure.instrument_name",
                            "GuideWindow.instrument_name",
                            "WFICommon.instrument_name",
                        ],
                    },
                    "WFI",
                )
            },
            "optical_element": {
                "archive_catalog": (
                    {
                        "datatype": "nvarchar(20)",
                        "destination": [
                            "WFIExposure.optical_element",
                            "GuideWindow.optical_element",
                            "WFICommon.optical_element",
                        ],
                    },
                    "GRISM",
                )
            },
        }
    }


def test_node_representation():
    """
    Regression test for #244.

    The DNode object was lacking the __repr__ method, which is used to return
    the representation of the object. The reported issue was with ``mdl.meta.instrument``,
    so that is directly checked here.
    """
    mdl = datamodels.ImageModel.create_fake_data()
    assert repr(mdl.meta.instrument) == repr(
        {
            "name": "WFI",
            "detector": mdl.meta.instrument.detector,
            "optical_element": mdl.meta.instrument.optical_element,
        }
    )


def test_get_latest_schema(object_node, object_node_default_uri, object_node_uris):
    assert len(object_node_uris) > 0, "This test requires at lest one URI available."

    for uri in [object_node_default_uri.rsplit("-", 1)[0], *object_node_uris]:
        latest_uri, schema = stnode.get_latest_schema(uri)
        assert latest_uri == object_node_default_uri

        assert stnode._schema._get_schema_from_tag(object_node._default_tag) == schema


@pytest.mark.parametrize(
    "set_method, value, getattr_type, getitem_type",
    [
        ("__setattr__", {}, stnode.DNode, dict),
        ("__setattr__", stnode.DNode({}), stnode.DNode, dict),
        ("__setitem__", {}, stnode.DNode, dict),
        ("__setitem__", stnode.DNode({}), stnode.DNode, stnode.DNode),
        ("__setattr__", [], stnode.LNode, list),
        ("__setattr__", stnode.LNode([]), stnode.LNode, list),
        ("__setitem__", [], stnode.LNode, list),
        ("__setitem__", stnode.LNode([]), stnode.LNode, stnode.LNode),
    ],
)
def test_dnode_unwrapping(set_method, value, getattr_type, getitem_type):
    """
    Test DNode wraps and unwraps for set/getattr but not for set/getitem
    """
    node = stnode.DNode()
    key = "a"
    getattr(node, set_method)(key, value)
    assert type(getattr(node, key)) is getattr_type
    assert type(node[key]) is getitem_type
    if set_method == "__setattr__":
        assert getattr(node, key) is not value


@pytest.mark.parametrize(
    "value, return_type",
    [
        ({}, stnode.DNode),
        (stnode.DNode({}), stnode.DNode),
        ([], stnode.LNode),
        (stnode.LNode([]), stnode.LNode),
    ],
)
def test_lnode_unwrapping(value, return_type):
    """
    Test LNode wraps and unwraps for set/getitem
    """
    node = stnode.LNode([0])
    node[0] = value
    assert type(node[0]) is return_type
    assert node[0] is not value
