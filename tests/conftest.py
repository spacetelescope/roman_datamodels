import asdf
import pytest

from roman_datamodels import DataModel
from roman_datamodels._stnode import REGISTRY, TaggedListNode, TaggedObjectNode, TaggedScalarNode


@pytest.fixture(scope="module", params=REGISTRY.manifest_uri)
def manifest(request):
    return request.param


@pytest.fixture(scope="module", params=REGISTRY.nodes)
def node_type(request) -> type[TaggedObjectNode]:
    return request.param


@pytest.fixture(scope="module")
def node(node_type) -> TaggedObjectNode:
    return node_type.create_fake_data()


@pytest.fixture(scope="module", params=REGISTRY.object_nodes)
def object_node_type(request) -> type[TaggedObjectNode]:
    return request.param


@pytest.fixture(scope="module", params=REGISTRY.list_nodes)
def list_node_type(request) -> type[TaggedListNode]:
    return request.param


@pytest.fixture(scope="module", params=tuple(REGISTRY.object_nodes) + tuple(REGISTRY.list_nodes))
def container_node_type(request) -> type[TaggedObjectNode] | type[TaggedListNode]:
    return request.param


@pytest.fixture(scope="module", params=REGISTRY.scalar_nodes)
def scalar_node_type(request) -> type[TaggedScalarNode]:
    return request.param


@pytest.fixture(scope="module")
def object_node_default_schema_uri(object_node_type) -> str:
    return REGISTRY.tag_uri.schema_uri[object_node_type._default_tag]


@pytest.fixture(scope="module")
def object_node_uris(object_node_default_schema_uri) -> tuple[str, ...]:
    prefix_uri = f"{object_node_default_schema_uri.rsplit('-', 1)[0]}-"

    return tuple(schema_uri for schema_uri in asdf.get_config().resource_manager if schema_uri.startswith(prefix_uri))


@pytest.fixture(scope="module", params=REGISTRY.datamodels)
def model_node_type(request) -> type[TaggedObjectNode]:
    """Get the tagged object node type that maps to a datamodel"""
    return request.param


@pytest.fixture
def model_node(model_node_type) -> TaggedObjectNode:
    """Get a fake_data instance of the tagged object node that maps to a datamodel"""
    return model_node_type.create_fake_data()


@pytest.fixture(scope="module")
def model_type(model_node_type) -> type[DataModel]:
    """Get the datamodel type"""
    return REGISTRY.datamodels[model_node_type]


@pytest.fixture
def model(model_type) -> DataModel:
    """Get a fake_data instance of the datamodel"""
    return model_type.create_fake_data()
