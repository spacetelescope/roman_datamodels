from typing import Any

import pytest
from asdf import AsdfFile
from asdf.schema import load_schema

from roman_datamodels._stnode._registry import (
    LIST_NODE_CLASSES_BY_PATTERN,
    MANIFEST_TAG_REGISTRY,
    NODE_CLASSES_BY_TAG,
    OBJECT_NODE_CLASSES_BY_PATTERN,
)
from roman_datamodels._stnode._stnode import _MANIFESTS as MANIFESTS
from roman_datamodels._stnode._tagged import TaggedListNode, TaggedObjectNode, tagged_type
from roman_datamodels.datamodels import MODEL_REGISTRY, DataModel


@pytest.fixture(scope="session", params=MANIFESTS)
def manifest(request):
    return request.param


@pytest.fixture(scope="session", params=MANIFEST_TAG_REGISTRY)
def manifest_uri(request):
    """Fixture to provide all manifest URIs for testing"""
    return request.param


@pytest.fixture(scope="session")
def manifest_schema(manifest_uri: str) -> Any:
    """Fixture to provide the schema corresponding to a given manifest URI for testing."""
    return load_schema(manifest_uri, resolve_references=True)


@pytest.fixture(scope="session")
def latest_manifest_uri() -> str:
    """Fixture to provide the latest manifest URI for testing"""
    return MANIFESTS[0]["id"]


@pytest.fixture(scope="module", params=NODE_CLASSES_BY_TAG)
def tag_uri(request) -> str:
    """Fixture for providing all tag URIs to test against."""
    return request.param


@pytest.fixture(scope="module")
def schema_uri(tag_uri: str) -> str:
    """Fixture to provide the schema URI corresponding to a given tag URI for testing"""
    with AsdfFile() as af:
        return af.extension_manager.get_tag_definition(tag_uri).schema_uris[0]


@pytest.fixture(scope="module")
def node_class(tag_uri: str) -> tagged_type:
    """Fixture for providing the node class corresponding to a given tag URI for testing."""
    return NODE_CLASSES_BY_TAG[tag_uri]


@pytest.fixture(scope="module")
def latest_tag_uri(node_class: tagged_type) -> str:
    """Fixture for providing the latest tag URI corresponding to a given node class for testing."""
    return node_class._default_tag


@pytest.fixture(scope="module")
def latest_schema_uri(latest_tag_uri: str) -> str:
    """Fixture for providing the latest schema URI corresponding to a given tag URI for testing."""
    with AsdfFile() as af:
        return af.extension_manager.get_tag_definition(latest_tag_uri).schema_uris[0]


@pytest.fixture(scope="module")
def schema(schema_uri: str) -> Any:
    """Fixture for providing the schema corresponding to a given schema URI for testing."""
    return load_schema(schema_uri, resolve_references=True)


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
