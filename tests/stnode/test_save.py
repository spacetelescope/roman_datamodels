import asdf
import pytest

from roman_datamodels._stnode._registry import DATAMODEL_PATTERNS, NODE_CLASSES_BY_TAG, STATIC_PATTERNS
from roman_datamodels._stnode._stnode import DATAMODEL_MANIFESTS, STATIC_MANIFESTS

_LATEST_STATIC = STATIC_MANIFESTS[0]
_LATEST_STATIC_URIS = set(tag_def["tag_uri"] for tag_def in _LATEST_STATIC["tags"])
_LATEST_DATAMODEL = DATAMODEL_MANIFESTS[0]
_LATEST_DATAMODEL_URIS = set(tag_def["tag_uri"] for tag_def in _LATEST_DATAMODEL["tags"])


# RAD has a bug in its manifests making it so that some tags are not accounted for
_X_FAIL_TAGS = {
    "asdf://stsci.edu/datamodels/roman/tags/l3_cal_step-1.0.0",
    "asdf://stsci.edu/datamodels/roman/tags/l3_cal_step-1.1.0",
    "asdf://stsci.edu/datamodels/roman/tags/resample-1.0.0",
    "asdf://stsci.edu/datamodels/roman/tags/individual_image_meta-1.0.0",
    "asdf://stsci.edu/datamodels/roman/tags/mosaic_associations-1.0.0",
    "asdf://stsci.edu/datamodels/roman/tags/mosaic_wcsinfo-1.0.0",
}

# from ..conftest import MANIFESTS


@pytest.fixture(scope="session", params=NODE_CLASSES_BY_TAG)
def node_tag(request):
    return request.param


@pytest.fixture(scope="session")
def node_cls(node_tag):
    return NODE_CLASSES_BY_TAG[node_tag]


@pytest.fixture(scope="session")
def node_instance(node_cls):
    return node_cls.create_fake_data()


def test_static_datamodel_pattern_disjoint():
    """Test that the static and datamodel manifests are disjoint"""
    assert len(STATIC_PATTERNS) > 0
    assert len(DATAMODEL_PATTERNS) > 0

    assert set(STATIC_PATTERNS.keys()) & set(DATAMODEL_PATTERNS.keys()) == set()


def test_node_uris(node_tag, node_cls, request):
    """Test the _default_tag and _latest_manifest uris to make sure they are correct"""
    if node_tag in _X_FAIL_TAGS:
        request.node.add_marker(pytest.mark.xfail(reason=f"RAD has a manifest bug for {node_tag}"))

    if node_cls._pattern in STATIC_PATTERNS:
        assert node_cls._default_tag in _LATEST_STATIC_URIS
        assert node_cls._latest_manifest == _LATEST_STATIC["id"]

    elif node_cls._pattern in DATAMODEL_PATTERNS:
        assert node_cls._default_tag in _LATEST_DATAMODEL_URIS
        assert node_cls._latest_manifest == _LATEST_DATAMODEL["id"]

    else:
        raise ValueError(f"{node_cls._pattern} for {type(node_cls)} is not in a manifest")


def test_history(tmp_path, node_instance):
    filename = tmp_path / "history_test.asdf"
    prefix = "asdf://stsci.edu/datamodels/roman/extensions/"

    # Save asdf file
    asdf.AsdfFile(tree={"roman": node_instance}).write_to(filename)

    # Read extension history
    with asdf.open(filename) as af:
        extensions = af.tree["history"]["extensions"]

    # Find the roman extension uris
    extension_uris = [extension["extension_uri"] for extension in extensions if extension["extension_uri"].startswith(prefix)]

    # There should be just one
    assert len(extension_uris) == 1

    # Generate the prefix for the extension
    if node_instance._pattern in STATIC_PATTERNS:
        prefix += "static-"
    else:
        prefix += "datamodels-"

    extension_uri = extension_uris[0]
    assert extension_uri.startswith(prefix)

    datamodels_uri = extension_uri.replace("extensions", "manifests")
    assert datamodels_uri.startswith(prefix.replace("extensions", "manifests"))
