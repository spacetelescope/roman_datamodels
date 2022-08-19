import asdf
import pytest

from roman_datamodels import stnode
from roman_datamodels.testing import assert_node_equal, create_node


def test_generated_node_classes(manifest):
    for tag in manifest["tags"]:
        class_name = stnode._class_name_from_tag_uri(tag["tag_uri"])
        node_class = getattr(stnode, class_name)

        assert issubclass(node_class, (stnode.TaggedObjectNode, stnode.TaggedListNode, stnode.TaggedScalarNode))
        assert node_class._tag == tag["tag_uri"]
        assert tag["description"] in node_class.__doc__
        assert tag["tag_uri"] in node_class.__doc__
        assert node_class.__module__ == stnode.__name__
        assert node_class.__name__ in stnode.__all__


def test_wfi_mode():
    """
    The WfiMode class includes special properties that map optical_element
    values to grating or filter.
    """
    node = stnode.WfiMode({"optical_element": "GRISM"})
    assert node.optical_element == "GRISM"
    assert node.grating == "GRISM"
    assert node.filter is None

    node = stnode.WfiMode({"optical_element": "PRISM"})
    assert node.optical_element == "PRISM"
    assert node.grating == "PRISM"
    assert node.filter is None

    node = stnode.WfiMode({"optical_element": "F129"})
    assert node.optical_element == "F129"
    assert node.grating is None
    assert node.filter == "F129"


@pytest.mark.parametrize("node_class", stnode.NODE_CLASSES)
def test_serialization(node_class, tmp_path):
    file_path = tmp_path / "test.asdf"

    node = create_node(node_class)
    with asdf.AsdfFile() as af:
        af["node"] = node
        af.write_to(file_path)

    with asdf.open(file_path) as af:
        assert_node_equal(af["node"], node)


def test_info(capsys):
    node = stnode.WfiMode({"optical_element": "GRISM",
                           "detector": "WFI18",
                           "name": "WFI"})
    tree = dict(wfimode=node)
    af = asdf.AsdfFile(tree)
    af.info()
    captured = capsys.readouterr()
    assert "optical_element" in captured.out
    assert "GRISM" in captured.out


def test_schema_info():
    node = stnode.WfiMode({"optical_element": "GRISM",
                           "detector": "WFI18",
                           "name": "WFI"})
    tree = dict(wfimode=node)
    af = asdf.AsdfFile(tree)

    info = af.schema_info("archive_catalog")
    assert info == {
        'wfimode': {
            'detector': {
                'archive_catalog': ({'datatype': 'nvarchar(10)', 'destination': ['ScienceCommon.detector']}, "WFI18")
            },
            'name': {
                'archive_catalog': ({'datatype': 'nvarchar(5)', 'destination': ['ScienceCommon.instrument_name']}, "WFI")
            },
            'optical_element': {
                'archive_catalog': ({'datatype': 'nvarchar(20)', 'destination': ['ScienceCommon.optical_element']}, "GRISM")
            }
        }
    }
