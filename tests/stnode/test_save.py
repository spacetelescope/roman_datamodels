import asdf
import pytest

from roman_datamodels._stnode._registry import NODE_CLASSES_BY_TAG

from ..conftest import MANIFESTS


@pytest.mark.parametrize("tag", NODE_CLASSES_BY_TAG)
def test_history(tmp_path, tag):
    filename = tmp_path / "history_test.asdf"
    node_cls = NODE_CLASSES_BY_TAG[tag]
    node = node_cls.create_fake_data()

    # Save asdf file
    asdf.AsdfFile(tree={"roman": node}).write_to(filename)

    # Read extension history
    with asdf.open(filename) as af:
        extensions = af.tree["history"]["extensions"]

    # Find the roman extension uris
    extension_uris = [
        extension["extension_uri"]
        for extension in extensions
        if extension["extension_uri"].startswith("asdf://stsci.edu/datamodels/roman/extensions/")
    ]

    # There should be just one
    assert len(extension_uris) == 1
    extension_uri = extension_uris[0]
    assert extension_uri.startswith("asdf://stsci.edu/datamodels/roman/extensions/datamodels-")

    datamodels_uri = extension_uri.replace("extensions", "manifests")
    assert datamodels_uri.startswith("asdf://stsci.edu/datamodels/roman/manifests/datamodels-")

    assert extension_uri == MANIFESTS[0]["extension_uri"]
    assert datamodels_uri == MANIFESTS[0]["id"]
