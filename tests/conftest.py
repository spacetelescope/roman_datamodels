import os

import asdf
import pytest
import yaml

MANIFEST_URIS = [
    "asdf://stsci.edu/datamodels/roman/manifests/datamodels-1.0",
    "asdf://stsci.edu/datamodels/roman/manifests/datamodels-2.0.0.dev",
]
MANIFESTS = [yaml.safe_load(asdf.get_config().resource_manager[manifest_uri]) for manifest_uri in MANIFEST_URIS]


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
