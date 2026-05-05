import pytest
from asdf import get_config

from roman_datamodels._stnode._registry import OBJECT_NODE_CLASSES_BY_PATTERN, SCHEMA_URIS_BY_TAG


@pytest.fixture(scope="module", params=list(OBJECT_NODE_CLASSES_BY_PATTERN.values()))
def object_node(request):
    return request.param


@pytest.fixture(scope="module")
def object_node_default_uri(object_node):
    return SCHEMA_URIS_BY_TAG[object_node._default_tag]


@pytest.fixture(scope="module")
def object_node_uris(object_node_default_uri):
    prefix_uri = f"{object_node_default_uri.rsplit('-', 1)[0]}-"

    return [schema_uri for schema_uri in get_config().resource_manager if schema_uri.startswith(prefix_uri)]
