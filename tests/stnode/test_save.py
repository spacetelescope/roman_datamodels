import asdf
import pytest

from roman_datamodels._stnode._registry import REGISTRY


@pytest.fixture(scope="session", params=REGISTRY.tag_uri)
def node_tag(request):
    return request.param


@pytest.fixture(scope="session")
def node_cls(node_tag):
    return REGISTRY.tag_uri.node[node_tag]


@pytest.fixture(scope="session")
def node_instance(node_tag, node_cls):
    return node_cls.create_fake_data(tag=node_tag)


@pytest.mark.parametrize("manifest_uri", REGISTRY.manifest_uri)
def test_registry_manifest_to_tags_is_disjoint(manifest_uri):
    """Test that the tags registered to each manifest are unique"""
    for uri, tags in REGISTRY.manifest_uri.tag_uri.items():
        if uri != manifest_uri:
            assert set(tags) & set(REGISTRY.manifest_uri.tag_uri[manifest_uri]) == set()
        else:
            assert len(set(REGISTRY.manifest_uri.tag_uri[manifest_uri])) == len(REGISTRY.manifest_uri.tag_uri[manifest_uri])

        for tag in tags:
            assert tag in REGISTRY.tag_uri


def test_all_tags_in_manifest_to_tags_registry():
    assert sum(len(tags) for tags in REGISTRY.manifest_uri.tag_uri.values()) == len(REGISTRY.tag_uri)
    assert (
        len(REGISTRY.tag_uri.node)
        == len(REGISTRY.tag_uri.manifest_uri)
        == len(REGISTRY.tag_uri.schema_uri)
        == len(REGISTRY.tag_uri)
    )


def test_history(tmp_path, node_tag, node_instance):
    filename = tmp_path / "history_test.asdf"
    prefix = "asdf://stsci.edu/datamodels/roman/extensions/"

    # Sanity check
    assert node_instance.tag == node_tag
    assert node_instance._current_tag == node_tag

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
    assert REGISTRY.tag_uri.manifest_uri[node_tag] in datamodel_uris

    # If a tag is in a given manifest then all of its referenced tags are also in that manifest
    #    so the earliest manifest and extension can be is the latest one for the node_tag.
    #    all other manifests must be the same or newer.
    assert REGISTRY.tag_uri.manifest_uri[node_tag] == datamodel_uris[0]
