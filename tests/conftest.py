import asdf
import pytest

from roman_datamodels._stnode._registry import (
    LIST_NODE_CLASSES_BY_PATTERN,
    NODE_CLASSES_BY_TAG,
    OBJECT_NODE_CLASSES_BY_PATTERN,
    SCHEMA_URIS_BY_TAG,
)
from roman_datamodels._stnode._stnode import _MANIFESTS as MANIFESTS
from roman_datamodels._stnode._tagged import TaggedListNode, TaggedObjectNode, tagged_type
from roman_datamodels.datamodels import MODEL_REGISTRY, DataModel


@pytest.fixture(scope="session", params=MANIFESTS)
def manifest(request):
    return request.param


@pytest.fixture(scope="module", params=NODE_CLASSES_BY_TAG)
def tag_uri(request) -> str:
    """Fixture for providing all tag URIs to test against."""
    return request.param


@pytest.fixture(scope="module")
def node_class(tag_uri: str) -> tagged_type:
    """Fixture for providing the node class corresponding to a given tag URI for testing."""
    return NODE_CLASSES_BY_TAG[tag_uri]


@pytest.fixture(scope="module", params=MODEL_REGISTRY)
def model_node(request) -> type[TaggedObjectNode]:
    """Fixture for providing all of the node classes that data models wrap"""
    return request.param


@pytest.fixture(scope="module", params=MODEL_REGISTRY)
def other_model_node(request) -> type[TaggedObjectNode]:
    """Another independent fixture for providing all of the node classes that data models wrap"""
    return request.param


@pytest.fixture(scope="module")
def data_model(model_node: type[TaggedObjectNode]) -> type[DataModel]:
    """Fixture for providing all of the data model classes for testing"""
    return MODEL_REGISTRY[model_node]


@pytest.fixture(scope="module", params=OBJECT_NODE_CLASSES_BY_PATTERN.values())
def object_node_class(request) -> type[TaggedObjectNode]:
    """Fixture for providing all of the object node classes for testing"""
    return request.param


@pytest.fixture(scope="module", params=LIST_NODE_CLASSES_BY_PATTERN.values())
def list_node_class(request) -> type[TaggedListNode]:
    """Fixture for providing all of the list node classes for testing"""
    return request.param


@pytest.fixture(scope="module", params=(*OBJECT_NODE_CLASSES_BY_PATTERN.values(), *LIST_NODE_CLASSES_BY_PATTERN.values()))
def container_node_class(request) -> type[TaggedObjectNode] | type[TaggedListNode]:
    """Fixture for providing all of the container node classes for testing"""
    return request.param


@pytest.fixture(scope="module")
def object_node_default_schema_uri(object_node_class: type[TaggedObjectNode]) -> str:
    """Fixture for providing the default schema URI for an object node class."""
    return SCHEMA_URIS_BY_TAG[object_node_class._default_tag]


@pytest.fixture(scope="module")
def object_node_schema_uris(object_node_default_schema_uri: str) -> tuple[str, ...]:
    """Fixture for providing all of the schema URIs for an object node class."""
    prefix_uri = f"{object_node_default_schema_uri.rsplit('-', 1)[0]}-"

    return tuple(schema_uri for schema_uri in asdf.get_config().resource_manager if schema_uri.startswith(prefix_uri))
