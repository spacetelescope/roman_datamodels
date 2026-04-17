from collections.abc import Generator

import asdf
import pytest

from roman_datamodels._stnode._stnode import _MANIFESTS as MANIFESTS
from roman_datamodels._stnode._tagged import SerializationNode, TaggedObjectNode
from roman_datamodels.datamodels import DataModel


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


def datamodel_types(cls: type[DataModel]) -> Generator[type[DataModel], None, None]:
    for subclass in cls.__subclasses__():
        if hasattr(subclass, "_node_type"):
            yield subclass
        else:
            yield from datamodel_types(subclass)


@pytest.fixture(scope="module", params=list(datamodel_types(DataModel)))
def model(request) -> type[DataModel]:
    return request.param


@pytest.fixture(scope="module")
def node(model) -> type[TaggedObjectNode]:
    return model._node_type
