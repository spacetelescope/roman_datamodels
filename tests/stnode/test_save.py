import asdf
import pytest

from roman_datamodels._stnode._tagged import SerializationNode

_TAG_URIS = tuple(tag_uri for node_cls in SerializationNode.__subclasses__() for tag_uri in node_cls.tag_uris)


@pytest.fixture(scope="session", params=_TAG_URIS)
def node_tag(request):
    return request.param


@pytest.fixture(scope="session")
def node_cls(node_tag):
    return SerializationNode.tag_type(node_tag)


@pytest.fixture(scope="session")
def node_instance(node_tag, node_cls):
    return node_cls.create_fake_data(tag=node_tag)


@pytest.mark.parametrize("node_type", SerializationNode.__subclasses__())
def test_manifest_tag_registry_disjoint(node_type: type[SerializationNode]):
    """Test that the tags registered to each manifest are unique"""
    manifest_uri = node_type.manifest_uri
    for node_cls in SerializationNode.__subclasses__():
        uri = node_cls.manifest_uri
        tags = node_cls.tag_uris
        if uri != manifest_uri:
            assert set(tags) & set(node_type.tag_uris) == set()
        else:
            assert len(set(node_type.tag_uris)) == len(node_type.tag_uris), f"Duplicate tags in manifest {manifest_uri}"

        for tag in tags:
            assert tag in _TAG_URIS


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
    assert SerializationNode.serialization_type(node_instance.tag).manifest_uri in datamodel_uris

    # If a tag is in a given manifest then all of its referenced tags are also in that manifest
    #    so the earliest manifest and extension can be is the latest one for the node_tag.
    #    all other manifests must be the same or newer.
    assert SerializationNode.serialization_type(node_instance.tag).manifest_uri == datamodel_uris[0]
