from contextlib import nullcontext

import asdf
import pytest

from roman_datamodels._stnode._registry import OBJECT_NODE_CLASSES_BY_PATTERN, SCHEMA_URIS_BY_TAG
from roman_datamodels._stnode._stnode import _MANIFESTS as MANIFESTS
from roman_datamodels.datamodels import MODEL_REGISTRY, GuidewindowModel, RampFitOutputModel


@pytest.fixture(scope="session", params=MANIFESTS)
def manifest(request):
    return request.param


@pytest.fixture(scope="session", params=list(OBJECT_NODE_CLASSES_BY_PATTERN.values()))
def object_node(request):
    return request.param


@pytest.fixture(scope="session")
def object_node_default_uri(object_node):
    return SCHEMA_URIS_BY_TAG[object_node._default_tag]


@pytest.fixture(scope="session")
def object_node_uris(object_node_default_uri):
    prefix_uri = f"{object_node_default_uri.rsplit('-', 1)[0]}-"

    return [schema_uri for schema_uri in asdf.get_config().resource_manager if schema_uri.startswith(prefix_uri)]


@pytest.fixture(params=MODEL_REGISTRY.values())
def model(request):
    return request.param


@pytest.fixture
def node(model):
    return model._node_type


@pytest.fixture()
def create_fake_data(model):
    def _create_fake_data(*args, **kwargs):
        with (
            pytest.warns(DeprecationWarning, match=r"This node is no longer.*")
            if (model is RampFitOutputModel or model is GuidewindowModel)
            else nullcontext()
        ):
            return model.create_fake_data(*args, **kwargs)

    return _create_fake_data


@pytest.fixture()
def fake_data(create_fake_data):
    return create_fake_data()


@pytest.fixture()
def create_minimal(model):
    def _create_minimal(*args, **kwargs):
        with (
            pytest.warns(DeprecationWarning, match=r"This node is no longer.*")
            if (model is RampFitOutputModel or model is GuidewindowModel)
            else nullcontext()
        ):
            return model.create_minimal(*args, **kwargs)

    return _create_minimal


@pytest.fixture()
def minimal(create_minimal):
    return create_minimal()


@pytest.fixture()
def node_fake_data(node, model):
    with (
        pytest.warns(DeprecationWarning, match=r"This node is no longer.*")
        if (model is RampFitOutputModel or model is GuidewindowModel)
        else nullcontext()
    ):
        return node.create_fake_data()


@pytest.fixture()
def node_minimal(node, model):
    with (
        pytest.warns(DeprecationWarning, match=r"This node is no longer.*")
        if (model is RampFitOutputModel or model is GuidewindowModel)
        else nullcontext()
    ):
        return node.create_minimal()
