import pytest
from asdf import get_config

from roman_datamodels._stnode import TaggedListNode, TaggedNode, TaggedObjectNode, get_default_tag, get_schema_uri
from roman_datamodels._stnode._registry import NODE_CLASSES_BY_TAG, NODES_BY_PATTERN
from roman_datamodels.datamodels import (
    MODEL_REGISTRY,
    DataModel,
    ForcedImageSourceCatalogModel,
    ForcedMosaicSourceCatalogModel,
    ImageSourceCatalogModel,
    MosaicSourceCatalogModel,
    MultibandSourceCatalogModel,
)


@pytest.fixture(scope="module", params=NODE_CLASSES_BY_TAG)
def tag_uri(request) -> str:
    """Fixture to provide a tag URI for each of the RAD tags"""
    return request.param


@pytest.fixture(scope="module")
def tagged_node_class(tag_uri: str) -> type[TaggedNode]:
    """Fixture to provide the node class associated with each of the RAD tags"""
    return NODE_CLASSES_BY_TAG[tag_uri]


@pytest.fixture(scope="module", params=NODES_BY_PATTERN)
def node_pattern(request) -> str:
    """Fixture to provide a tag pattern for each of the RAD tags"""
    return request.param


@pytest.fixture(scope="module")
def node_class(node_pattern: str) -> type[TaggedNode]:
    """Fixture to provide all of the node classes"""
    return NODES_BY_PATTERN[node_pattern]


@pytest.fixture(scope="module")
def node_default_tag(node_pattern: str) -> str:
    """Fixture to provide a node's default tag for testing"""
    return get_default_tag(node_pattern)


@pytest.fixture(
    scope="session", params=(pattern for pattern, cls in NODES_BY_PATTERN.items() if issubclass(cls, TaggedObjectNode))
)
def object_pattern(request) -> str:
    """Fixture to provide a tag pattern for each of the object node classes"""
    return request.param


@pytest.fixture(scope="module")
def object_node_class(object_pattern: str) -> type[TaggedObjectNode]:
    """Fixture to provide all of the object node classes"""
    return NODES_BY_PATTERN[object_pattern]


@pytest.fixture(scope="module")
def object_node_default_tag(object_pattern: str) -> str:
    """Fixture to provide an object node's default tag for testing"""
    return get_default_tag(object_pattern)


@pytest.fixture(scope="module", params=(pattern for pattern, cls in NODES_BY_PATTERN.items() if issubclass(cls, TaggedListNode)))
def list_pattern(request) -> str:
    """Fixture to provide a tag pattern for each of the list node classes"""
    return request.param


@pytest.fixture(scope="module")
def list_node_class(list_pattern: str) -> type[TaggedListNode]:
    """Fixture to provide all of the list node classes"""
    return NODES_BY_PATTERN[list_pattern]


@pytest.fixture(scope="module")
def list_node_default_tag(list_pattern: str) -> str:
    """Fixture to provide a list node's default tag for testing"""
    return get_default_tag(list_pattern)


@pytest.fixture(
    scope="module",
    params=(pattern for pattern, cls in NODES_BY_PATTERN.items() if issubclass(cls, (TaggedObjectNode, TaggedListNode))),
)
def container_pattern(request) -> str:
    """Fixture to provide a tag pattern for each of the container node classes (object and list)"""
    return request.param


@pytest.fixture(scope="module")
def container_node_class(container_pattern: str) -> type[TaggedObjectNode] | type[TaggedListNode]:
    """Fixture to provide all of the container node classes (object and list)"""
    return NODES_BY_PATTERN[container_pattern]


@pytest.fixture(scope="module")
def container_node_default_tag(container_pattern: str) -> str:
    """Fixture to provide a container node's default tag for testing"""
    return get_default_tag(container_pattern)


@pytest.fixture(scope="module")
def object_node_default_schema_uri(object_node_default_tag: str) -> str:
    """Fixture to provide an object node's default schema URI for testing"""
    return get_schema_uri(object_node_default_tag)


@pytest.fixture(scope="module")
def object_node_schema_uris(object_node_default_schema_uri: str) -> tuple[str, ...]:
    """Fixture to provide all of the schema URIs associated with an object node for testing"""
    prefix_uri = f"{object_node_default_schema_uri.rsplit('-', 1)[0]}-"

    return tuple(schema_uri for schema_uri in get_config().resource_manager if schema_uri.startswith(prefix_uri))


@pytest.fixture(scope="module", params=MODEL_REGISTRY)
def data_model_node(request) -> type[TaggedObjectNode]:
    """
    Fixture to provide all of the model nodes associated with each of the DataModels
    """
    return request.param


@pytest.fixture(scope="module")
def data_model(data_model_node: type[TaggedObjectNode]) -> type[DataModel]:
    """
    Fixture to provide all of the DataModels
    """
    return MODEL_REGISTRY[data_model_node]


@pytest.fixture(scope="module")
def data_model_tags(data_model_node: type[TaggedObjectNode]) -> set[str]:
    """
    Fixture to provide all of the tags associated with each of the DataModels
    """
    return set(tag_uri for tag_uri, node in NODE_CLASSES_BY_TAG.items() if node is data_model_node)


# TODO: Automate how to get these instead of hardcoding them here
@pytest.fixture(
    scope="module",
    params=(
        ImageSourceCatalogModel,
        MosaicSourceCatalogModel,
        ForcedImageSourceCatalogModel,
        ForcedMosaicSourceCatalogModel,
        MultibandSourceCatalogModel,
    ),
)
def catalog_data_model(request) -> type[DataModel]:
    """
    Fixture to provide all of the DataModels with source catalogs
    """
    return request.param
