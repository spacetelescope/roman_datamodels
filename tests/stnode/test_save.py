import asdf
import pytest

from roman_datamodels._stnode._registry import NODE_CLASSES_BY_TAG


@pytest.fixture(scope="session", params=NODE_CLASSES_BY_TAG)
def node_tag(request):
    return request.param


@pytest.fixture(scope="session")
def node_cls(node_tag):
    return NODE_CLASSES_BY_TAG[node_tag]


@pytest.fixture(scope="session")
def node_instance(node_cls):
    return node_cls.create_fake_data()


def test_history(tmp_path, node_instance):
    filename = tmp_path / "history_test.asdf"
    prefix = "asdf://stsci.edu/datamodels/roman/extensions/datamodels-"

    # Save asdf file
    asdf.AsdfFile(tree={"roman": node_instance}).write_to(filename)

    # Read extension history
    with asdf.open(filename) as af:
        extensions = af.tree["history"]["extensions"]

    # Find the roman extension uris
    extension_uris = [extension["extension_uri"] for extension in extensions if extension["extension_uri"].startswith(prefix)]

    # There should be just one
    assert len(extension_uris) == 1

    extension_uri = extension_uris[0]
    assert extension_uri.startswith(prefix)

    datamodels_uri = extension_uri.replace("extensions", "manifests")
    assert node_instance._latest_manifest == datamodels_uri
