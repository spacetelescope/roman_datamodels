import asdf
import pytest

from roman_datamodels._stnode import REGISTRY, TaggedObjectNode


@pytest.fixture(scope="session", params=REGISTRY.manifest)
def manifest(request):
    return request.param


@pytest.fixture(scope="session", params=list(REGISTRY.pattern.object.values()))
def object_node(request) -> type[TaggedObjectNode]:
    return request.param


@pytest.fixture(scope="session")
def object_node_default_uri(object_node) -> str:
    return REGISTRY.tag.schema[object_node._default_tag]


@pytest.fixture(scope="session")
def object_node_uris(object_node_default_uri) -> tuple[str, ...]:
    prefix_uri = f"{object_node_default_uri.rsplit('-', 1)[0]}-"

    return tuple(schema_uri for schema_uri in asdf.get_config().resource_manager if schema_uri.startswith(prefix_uri))
