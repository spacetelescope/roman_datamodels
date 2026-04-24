import asdf
import pytest

from roman_datamodels._stnode._manifest import MANIFEST_TAG_REGISTRY, TAG_MANIFEST_REGISTRY
from roman_datamodels._stnode._stnode import NODE_CLASSES_BY_TAG


@pytest.fixture(scope="session", params=TAG_MANIFEST_REGISTRY.keys())
def node_tag(request):
    return request.param


@pytest.fixture(scope="session")
def node_cls(node_tag):
    return NODE_CLASSES_BY_TAG[node_tag]


@pytest.fixture(scope="session")
def node_instance(node_tag, node_cls):
    return node_cls.create_fake_data(tag=node_tag)


@pytest.mark.parametrize("manifest_uri", MANIFEST_TAG_REGISTRY)
def test_manifest_tag_registry_disjoint(manifest_uri):
    """Test that the tags registered to each manifest are unique"""
    for uri, tags in MANIFEST_TAG_REGISTRY.items():
        if uri != manifest_uri:
            assert set(tags) & set(MANIFEST_TAG_REGISTRY[manifest_uri]) == set()
        else:
            assert len(set(MANIFEST_TAG_REGISTRY[manifest_uri])) == len(MANIFEST_TAG_REGISTRY[manifest_uri])

        for tag in tags:
            assert tag in NODE_CLASSES_BY_TAG


def test_all_tags_in_manifest_tag_registry():
    assert sum(len(tags) for tags in MANIFEST_TAG_REGISTRY.values()) == len(NODE_CLASSES_BY_TAG)
    assert len(TAG_MANIFEST_REGISTRY) == len(NODE_CLASSES_BY_TAG)


def test_history(tmp_path, node_tag, node_instance):
    filename = tmp_path / "history_test.asdf"
    prefix = "asdf://stsci.edu/datamodels/roman/extensions/"

    # Sanity check
    assert node_instance.tag == node_tag

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
    assert TAG_MANIFEST_REGISTRY[node_tag] in datamodel_uris

    # If a tag is in a given manifest then all of its referenced tags are also in that manifest
    #    so the earliest manifest and extension can be is the latest one for the node_tag.
    #    all other manifests must be the same or newer.
    assert TAG_MANIFEST_REGISTRY[node_tag] == datamodel_uris[0]
