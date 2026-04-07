import asdf
import pytest

from roman_datamodels._stnode._stnode import _MANIFESTS as MANIFESTS
from roman_datamodels._stnode._tagged import SerializationNode, TaggedObjectNode


@pytest.fixture(scope="session", params=MANIFESTS)
def manifest(request):
    return request.param


@pytest.fixture(scope="session", params=TaggedObjectNode.__subclasses__())
def object_node(request):
    return request.param


@pytest.fixture(scope="session")
def object_node_default_uri(object_node):
    return SerializationNode.schema_uri(object_node._default_tag)


@pytest.fixture(scope="session")
def object_node_uris(object_node_default_uri):
    prefix_uri = f"{object_node_default_uri.rsplit('-', 1)[0]}-"

    return [schema_uri for schema_uri in asdf.get_config().resource_manager if schema_uri.startswith(prefix_uri)]
