from contextlib import nullcontext

import asdf
import numpy as np
import pytest
from astropy.table import Table
from astropy.time import Time

from roman_datamodels import datamodels, stnode
from roman_datamodels.stnode._individual_image_meta import _MetaTables, _SchemaTable
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


@pytest.mark.parametrize("scalar_key, scalar_type", stnode._registry.SCALAR_NODE_CLASSES_BY_KEY.items())
def test_no_wrapping_of_scalars(scalar_key, scalar_type):
    """Demonstrate that scalar types are not wrapped in nodes."""
    test_value = Time.now() if "file_date" in scalar_key else "test_value"

    # Plain DNode does not convert to scalar type
    node = stnode.DNode({scalar_key: test_value})
    assert getattr(node, scalar_key) == test_value
    assert not isinstance(getattr(node, scalar_key), scalar_type)

    # Spcalialized TaggedScalarDNode does convert to scalar type
    #   Guidewindow, Fps, Tvac use this case
    node = stnode.TaggedScalarDNode({scalar_key: test_value})
    assert getattr(node, scalar_key) == test_value
    assert isinstance(getattr(node, scalar_key), scalar_type)


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


class TestMetaTables:
    """Test the _MetaTables for combining multiple image meta nodes together."""

    def test_create_table(self):
        """Test the blending of the table metadata."""

        names = ["Foo", "Bar", "Baz", "Qux"]
        defaults = {"Foo": 1, "Bar": 2.0}

        schema_table = _SchemaTable(names=names, defaults=defaults)
        schema_table.add_row(stnode.DNode({}))
        schema_table.add_row(stnode.DNode({"Foo": 27, "Bar": 3.14, "Baz": "Hello"}))
        schema_table.add_row(stnode.DNode({"Foo": -3, "Bar": 2.72, "Baz": ["A", "B"]}))
        schema_table.add_row(stnode.DNode({"Foo": 0, "Bar": None, "Baz": None}))

        table = schema_table.create_table()
        assert isinstance(table, Table)

        assert table.colnames == names

        assert table["Foo"].dtype == np.int64
        assert (table["Foo"] == np.array([1, 27, -3, 0])).all()

        assert table["Bar"].dtype == np.float64
        assert np.array_equal(table["Bar"], np.array([2.0, 3.14, 2.72, np.nan]), equal_nan=True)

        assert table["Baz"].dtype == np.dtype("<U12")
        assert (table["Baz"] == np.array(["MISSING_CELL", "Hello", "['A', 'B']", "None"])).all()

        assert table["Qux"].dtype == np.dtype("<U4")
        assert (table["Qux"] == np.array(["None"] * 4)).all()

        schema_table.reset()
        assert not schema_table.create_table()  # empty table

    def test_create_tables(self):
        """Test the the building of multiple tables from multiple nodes with meta attributes for each table."""

        schema_tables = {"foo": _SchemaTable(names=["A", "B"]), "bar": _SchemaTable(names=["C", "D"])}

        meta_tables = _MetaTables(schema_tables=schema_tables)

        assert meta_tables.n_models == 0

        meta_tables.add_image(stnode.DNode({"meta": {"foo": {"A": 1, "B": 2}, "bar": {"C": 3, "D": 4}}}))
        meta_tables.add_image(stnode.DNode({"meta": {"foo": {"A": 5, "B": 6}, "bar": {"C": 7, "D": 8}}}))

        with pytest.raises(ValueError, match=r"Image does not have a meta attribute"):
            meta_tables.add_image(stnode.DNode({}))

        assert meta_tables.n_models == 2

        tables = meta_tables.create_tables()
        assert isinstance(tables, dict)
        assert len(tables) == 2
        assert tables.keys() == schema_tables.keys()
        assert all(isinstance(t, Table) for t in tables.values())

        assert tables["foo"].colnames == ["A", "B"]
        assert (tables["foo"]["A"] == np.array([1, 5])).all()
        assert (tables["foo"]["B"] == np.array([2, 6])).all()

        assert tables["bar"].colnames == ["C", "D"]
        assert (tables["bar"]["C"] == np.array([3, 7])).all()
        assert (tables["bar"]["D"] == np.array([4, 8])).all()
