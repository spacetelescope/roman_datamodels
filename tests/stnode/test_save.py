import asdf
import pytest

from roman_datamodels._stnode._registry import MANIFEST_TAG_REGISTRY, NODE_CLASSES_BY_TAG

_TAG_MANIFEST_MAP = {tag_uri: manifest_uri for manifest_uri, tags in MANIFEST_TAG_REGISTRY.items() for tag_uri in tags}


XFAIL_CREATE_FAKE_DATA = (
    "asdf://stsci.edu/datamodels/roman/tags/image_source_catalog-1.5.0",
    "asdf://stsci.edu/datamodels/roman/tags/mosaic_source_catalog-1.6.0",
    "asdf://stsci.edu/datamodels/roman/tags/multiband_source_catalog-1.2.0",
    "asdf://stsci.edu/datamodels/roman/tags/forced_image_source_catalog-1.2.0",
    "asdf://stsci.edu/datamodels/roman/tags/forced_mosaic_source_catalog-1.3.0",
    "asdf://stsci.edu/datamodels/roman/tags/image_source_catalog-1.4.0",
    "asdf://stsci.edu/datamodels/roman/tags/mosaic_source_catalog-1.5.0",
    "asdf://stsci.edu/datamodels/roman/tags/multiband_source_catalog-1.1.0",
    "asdf://stsci.edu/datamodels/roman/tags/forced_image_source_catalog-1.1.0",
    "asdf://stsci.edu/datamodels/roman/tags/forced_mosaic_source_catalog-1.2.0",
    "asdf://stsci.edu/datamodels/roman/tags/mosaic_source_catalog-1.4.0",
    "asdf://stsci.edu/datamodels/roman/tags/forced_mosaic_source_catalog-1.1.0",
    "asdf://stsci.edu/datamodels/roman/tags/image_source_catalog-1.3.0",
    "asdf://stsci.edu/datamodels/roman/tags/mosaic_source_catalog-1.3.0",
    "asdf://stsci.edu/datamodels/roman/tags/multiband_source_catalog-1.0.0",
    "asdf://stsci.edu/datamodels/roman/tags/forced_image_source_catalog-1.0.0",
    "asdf://stsci.edu/datamodels/roman/tags/forced_mosaic_source_catalog-1.0.0",
)


@pytest.fixture(scope="session", params=NODE_CLASSES_BY_TAG)
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
    assert len(_TAG_MANIFEST_MAP) == len(NODE_CLASSES_BY_TAG)


def test_history(tmp_path, node_tag, node_instance, request):
    filename = tmp_path / "history_test.asdf"
    prefix = "asdf://stsci.edu/datamodels/roman/extensions/"

    # Sanity check
    assert node_instance.tag == node_tag

    # These ones are broken due to a bug
    if node_tag in XFAIL_CREATE_FAKE_DATA:
        request.node.add_marker(pytest.mark.xfail(reason="Create_fake_data is broken for this model"))

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
    assert _TAG_MANIFEST_MAP[node_tag] in datamodel_uris

    # If a tag is in a given manifest then all of its referenced tags are also in that manifest
    #    so the earliest manifest and extension can be is the latest one for the node_tag.
    #    all other manifests must be the same or newer.
    assert _TAG_MANIFEST_MAP[node_tag] == datamodel_uris[0]
