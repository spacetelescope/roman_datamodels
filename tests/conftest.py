import importlib.resources
import os

import pytest
import yaml
from rad import resources

# Load the manifest directly from the rad resources and not from ASDF.
#   This is because the ASDF extensions have to be created before they can be registered
#   and this module creates the classes used by the ASDF extension.
_MANIFEST_DIR = importlib.resources.files(resources) / "manifests"
# sort manifests by version (newest first)
_MANIFEST_PATHS = sorted([path for path in _MANIFEST_DIR.glob("*.yaml")], reverse=True)
MANIFESTS = [yaml.safe_load(path.read_bytes()) for path in _MANIFEST_PATHS]


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


@pytest.fixture
def enable_typeguard():
    """
    Fixture to enable typeguard for testing.
    """
    from roman_datamodels.stnode import core

    assert core.get_config().typeguard_enabled is False

    with core.get_config().enable_typeguard():
        assert core.get_config().typeguard_enabled is True

        yield

    assert core.get_config().typeguard_enabled is False


@pytest.fixture(scope="function")
def use_testing_shape():
    """
    Fixture to force the use of testing shapes.
    """
    from roman_datamodels.stnode import core

    assert core.get_config().use_test_array_shape is False
    with core.get_config().enable_test_array_shape():
        assert core.get_config().use_test_array_shape is True
        yield

    assert core.get_config().use_test_array_shape is False
