import os

import asdf
import pytest
import yaml

import roman_datamodels

MANIFEST_URIS = [
    "asdf://stsci.edu/datamodels/roman/manifests/datamodels-1.0",
    "asdf://stsci.edu/datamodels/roman/manifests/datamodels-2.0.0.dev",
]
MANIFESTS = [yaml.safe_load(asdf.get_config().resource_manager[manifest_uri]) for manifest_uri in MANIFEST_URIS]

TAGGED_OBJECT_NODES = roman_datamodels.stnode._tagged.TaggedObjectNode.__subclasses__()
TAGGED_LIST_NODES = roman_datamodels.stnode._tagged.TaggedListNode.__subclasses__()
TAGGED_SCALAR_NODES = roman_datamodels.stnode._tagged.TaggedScalarNode.__subclasses__()
NODE_CLASSES = TAGGED_OBJECT_NODES + TAGGED_LIST_NODES + TAGGED_SCALAR_NODES


@pytest.fixture(scope="session", params=MANIFESTS)
def manifest(request):
    return request.param


@pytest.fixture(scope="function")
def nuke_env_var(request):
    from roman_datamodels import validate

    assert os.getenv(validate.ROMAN_VALIDATE) == "true"
    os.environ[validate.ROMAN_VALIDATE] = request.param
    yield request.param, request.param.lower() in ["true", "yes", "1"]
    os.environ[validate.ROMAN_VALIDATE] = "true"


@pytest.fixture(scope="function")
def nuke_env_strict_var(request):
    from roman_datamodels import validate

    assert os.getenv(validate.ROMAN_STRICT_VALIDATION) == "true"
    os.environ[validate.ROMAN_STRICT_VALIDATION] = request.param
    yield request.param
    os.environ[validate.ROMAN_STRICT_VALIDATION] = "true"
