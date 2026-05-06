import asdf
import pytest

from roman_datamodels import Manager
from roman_datamodels._stnode import TaggedNode


@pytest.fixture(scope="module")
def node_instance(tag_uri: str, node_class: type[TaggedNode]) -> TaggedNode:
    return node_class.create_fake_data(tag=tag_uri)


@pytest.mark.parametrize("manifest_uri", Manager().manifests)
def test_manager_manifest_tags_disjoint(manifest_uri):
    """Test that the tags registered to each manifest are unique"""
    for uri, manifest_node in Manager().manifests.items():
        if uri != manifest_uri:
            assert set(manifest_node.tag_uris) & set(Manager().manifests[manifest_uri].tag_uris) == set()
        else:
            assert len(set(manifest_node.tag_uris)) == len(manifest_node.tag_uris)

        for tag in manifest_node.tag_uris:
            assert tag in Manager().tags


def test_all_tags_in_manager_tags():
    assert sum(len(manifest_node.tag_uris) for manifest_node in Manager().manifests.values()) == len(Manager().tags)


def test_history(tmp_path, tag_uri: str, node_instance: TaggedNode):
    filename = tmp_path / "history_test.asdf"
    prefix = "asdf://stsci.edu/datamodels/roman/extensions/"

    # Sanity check
    assert node_instance.tag == tag_uri

    # Save asdf file
    asdf.AsdfFile(tree={"roman": node_instance}).write_to(filename)

    # Read extension history
    with asdf.open(filename) as af:
        extensions = af.tree["history"]["extensions"]

    # Find the roman extension uris
    extension_uris = [extension["extension_uri"] for extension in extensions if extension["extension_uri"].startswith(prefix)]

    for extension_uri in extension_uris:
        assert extension_uri.startswith(f"{prefix}datamodels-")

    datamodel_uris = sorted([extension_uri.replace("extensions", "manifests") for extension_uri in extension_uris])
    # node_tag should be the list of datamodel_uris
    assert Manager().tags[tag_uri].manifest_uri in datamodel_uris

    # If a tag is in a given manifest then all of its referenced tags are also in that manifest
    #    so the earliest manifest and extension can be is the latest one for the node_tag.
    #    all other manifests must be the same or newer.
    assert Manager().tags[tag_uri].manifest_uri == datamodel_uris[0]
