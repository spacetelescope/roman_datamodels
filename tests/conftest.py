import os

import pytest

from roman_datamodels.stnode._stnode import _MANIFESTS as MANIFESTS


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
