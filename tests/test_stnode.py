from contextlib import nullcontext
from typing import Any

import asdf
import pytest
from asdf.schema import load_schema

from roman_datamodels import DataModel, Manager, datamodels
from roman_datamodels import _stnode as stnode
from roman_datamodels._stnode import TaggedListNode, TaggedNode, TaggedObjectNode
from roman_datamodels.testing import assert_node_equal, assert_node_is_copy, wraps_hashable


@pytest.fixture(
    scope="session",
    params=(tag_def for manifest_uri in Manager().manifests for tag_def in load_schema(manifest_uri)["tags"]),
)
def raw_tag_def(request) -> dict[str, Any]:
    """
    Fixture to return the raw tag definitions from the raw manifest information.

    Note that this will have repeated items as it returns every single definition
        from every single manifest, but this is intentional to make sure we hit
        everything in the tests that use this fixture.
    """
    return request.param


def test_tag_has_node_class(raw_tag_def: dict[str, Any]):
    assert Manager().get_node_class(raw_tag_def["tag_uri"]) is not None

    tag_pattern = raw_tag_def["tag_uri"].rsplit("-", maxsplit=1)[0] + "-*"
    assert asdf.util.uri_match(tag_pattern, raw_tag_def["tag_uri"])
    if (default_tag := stnode.get_default_tag(tag_pattern)) != raw_tag_def["tag_uri"]:
        default_tag_version = default_tag.rsplit("-", maxsplit=1)[1]
        tag_def_version = raw_tag_def["tag_uri"].rsplit("-", maxsplit=1)[1]
        assert asdf.versioning.Version(default_tag_version) > asdf.versioning.Version(tag_def_version)


def test_node_classes_available_via_manager(tag_uri: str, node_class: type[TaggedNode]):
    assert issubclass(node_class, stnode.TaggedObjectNode | stnode.TaggedListNode | stnode.TaggedScalarNode)
    assert node_class.__module__.startswith(stnode.__name__)
    assert Manager().get_node_class(tag_uri) is node_class


def test_copy(node_class: type[TaggedNode], node_default_tag: str):
    """Demonstrate nodes can copy themselves, but don't always deepcopy."""
    node = node_class.create_fake_data(tag=node_default_tag)
    node_copy = node.copy()

    # Assert the copy is shallow:
    assert_node_is_copy(node, node_copy, deepcopy=False)

    # If the node only wraps hashable values, then it should "deepcopy" itself because
    # the immutable values cannot actually be copied. In the case, where there is an
    # unhashable value, then the node should not deepcopy itself.
    with nullcontext() if wraps_hashable(node) else pytest.raises(AssertionError):
        assert_node_is_copy(node, node_copy, deepcopy=True)


def test_deepcopy_model(data_model: type[DataModel]):
    model = data_model.create_fake_data(shape=(8, 8, 8))
    model_copy = model.copy()

    # There is no assert equal for models, but the data inside is what we care about.
    # this is stored under the _instance attribute. We can assert those instances are
    # deep copies of each other.
    assert_node_is_copy(model._instance, model_copy._instance, deepcopy=True)


def test_serialization(node_class: type[TaggedNode], node_default_tag: str, tmp_path):
    file_path = tmp_path / "test.asdf"

    node = node_class.create_fake_data(tag=node_default_tag)
    with asdf.AsdfFile() as af:
        af["node"] = node
        af.write_to(file_path)

    with asdf.open(file_path) as af:
        assert_node_equal(af["node"], node)


def test_no_hidden(object_node_default_tag: str):
    node = TaggedObjectNode.create_fake_data(tag=object_node_default_tag)
    with pytest.raises(AttributeError, match=r"Cannot set private attribute.*"):
        node._foo = "bar"  # Add a hidden attribute


def test_list_node_no_new_attributes(list_node_default_tag: str):
    """Test that no new attributes can be added to a list node."""
    node = TaggedListNode.create_fake_data(tag=list_node_default_tag)
    with pytest.raises(AttributeError, match=r"Cannot set attribute .*, only allowed are .*"):
        node.foo = "bar"

    with pytest.raises(AttributeError, match=r"Cannot set attribute .*, only allowed are .*"):
        node._foo = "bar"


def test_slotted(
    container_node_class: type[stnode.TaggedObjectNode] | type[stnode.TaggedListNode], container_node_default_tag: str
):
    """
    Test that slotted nodes do not allow new attributes to be added.
    """
    node = container_node_class.create_fake_data(tag=container_node_default_tag)
    with pytest.raises(AttributeError, match=r".* attribute .*__dict__.*"):
        # Attempt to access __dict__ directly, slotted classes do not have __dict__
        node.__dict__  # noqa: B018


def test_info(capsys):
    tag = "asdf://stsci.edu/datamodels/roman/tags/wfi_mode-1.2.0"
    node = Manager().get_node_class(tag)(
        {"optical_element": "GRISM", "detector": "WFI18", "name": "WFI"},
        read_tag=tag,
    )
    tree = dict(wfimode=node)
    af = asdf.AsdfFile(tree)
    af.info()
    captured = capsys.readouterr()
    assert "optical_element" in captured.out
    assert "GRISM" in captured.out


def test_schema_info():
    tag = "asdf://stsci.edu/datamodels/roman/tags/wfi_mode-1.2.0"
    node = Manager().get_node_class(tag)(
        {"optical_element": "GRISM", "detector": "WFI18", "name": "WFI"},
        read_tag=tag,
    )
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


def test_get_latest_schema(
    object_node_default_schema_uri: str,
    object_node_schema_uris: list[str],
    object_node_default_tag: str,
):
    assert len(object_node_schema_uris) > 0, "This test requires at lest one URI available."

    for uri in [object_node_default_schema_uri.rsplit("-", 1)[0], *object_node_schema_uris]:
        latest_uri, schema = stnode.get_latest_schema(uri)
        assert latest_uri == object_node_default_schema_uri

        assert stnode.get_schema_from_tag(object_node_default_tag) == schema


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
