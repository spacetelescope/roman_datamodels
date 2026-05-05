import pytest
from asdf import get_config

from roman_datamodels._stnode import TaggedListNode, TaggedObjectNode
from roman_datamodels._stnode._registry import (
    LIST_NODE_CLASSES_BY_PATTERN,
    NODE_CLASSES_BY_TAG,
    NODES_BY_PATTERN,
    OBJECT_NODE_CLASSES_BY_PATTERN,
    SCHEMA_URIS_BY_TAG,
)
from roman_datamodels._stnode._tagged import _TaggedNodeMixin
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
def tagged_node_class(tag_uri: str) -> type[_TaggedNodeMixin]:
    """Fixture to provide the node class associated with each of the RAD tags"""
    return NODE_CLASSES_BY_TAG[tag_uri]


@pytest.fixture(scope="module", params=NODES_BY_PATTERN.values())
def node_class(request) -> type[_TaggedNodeMixin]:
    """Fixture to provide all of the node classes"""
    return request.param


@pytest.fixture(scope="module", params=OBJECT_NODE_CLASSES_BY_PATTERN.values())
def object_node_class(request) -> type[TaggedObjectNode]:
    """Fixture to provide all of the object node classes"""
    return request.param


@pytest.fixture(scope="module", params=LIST_NODE_CLASSES_BY_PATTERN.values())
def list_node_class(request) -> type[TaggedListNode]:
    """Fixture to provide all of the list node classes"""
    return request.param


@pytest.fixture(scope="module", params=(*OBJECT_NODE_CLASSES_BY_PATTERN.values(), *LIST_NODE_CLASSES_BY_PATTERN.values()))
def container_node_class(request) -> type[TaggedObjectNode] | type[TaggedListNode]:
    """Fixture to provide all of the container node classes (object and list)"""
    return request.param


@pytest.fixture(scope="module")
def object_node_default_uri(object_node_class):
    return SCHEMA_URIS_BY_TAG[object_node_class._default_tag]


@pytest.fixture(scope="module")
def object_node_uris(object_node_default_uri):
    prefix_uri = f"{object_node_default_uri.rsplit('-', 1)[0]}-"

    return [schema_uri for schema_uri in get_config().resource_manager if schema_uri.startswith(prefix_uri)]


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
