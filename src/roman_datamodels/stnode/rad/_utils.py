from __future__ import annotations

from inspect import getattr_static, isclass
from typing import TYPE_CHECKING, Any, TypeVar, get_args

if TYPE_CHECKING:
    from ._node import ScalarNode

from ..core import DNode, LNode, PatternDNode, field
from ._node import ExtraFieldsMixin

_T = TypeVar("_T")

__all__ = [
    "camel_case_to_snake_case",
    "class_name_from_uri",
    "get_all_fields",
    "get_node_fields",
    "get_nodes",
    "wrap_into_node",
]


def class_name_from_uri(uri: str) -> str:
    """
    Compute the name of the schema from the uri.

    Parameters
    ----------
    uri
        The uri to find the name from
    """
    name = uri.split("/")[-1].split("-")[0]
    if "/tvac/" in uri and "tvac" not in name:
        name = "tvac_" + uri.split("/")[-1].split("-")[0]
    elif "/fps/" in uri and "fps" not in name:
        name = "fps_" + uri.split("/")[-1].split("-")[0]

    name = "".join([p.capitalize() for p in name.split("_")])

    if "reference_files" in uri:
        name += "Ref"

    return name


def camel_case_to_snake_case(value: str) -> str:
    """
    Courtesy of https://stackoverflow.com/a/1176023
    """
    import re

    return re.sub(r"(?<!^)(?=[A-Z])", "_", value).lower()


def _add_nodes(node: type, nodes: dict[str, type], sub_nodes: dict[str, type], base_cls: type) -> None:
    """
    Add the sub-nodes to the nodes dictionary.

    Parameters
    ----------
    node
        The node the sub-nodes are from.
    nodes
        The nodes to add to.
    sub_nodes
        The sub-nodes to add.
    base_cls
        The base class to start from.
    """
    for name, sub_node in sub_nodes.items():
        if name in nodes and nodes[name] != sub_node:
            raise RuntimeError(f"{base_cls.__name__} class '{node.__name__}' has conflicting sub-node '{name}'")

        nodes[name] = sub_node


def get_nodes(cls: type, filter_types: tuple[type, ...]) -> dict[str, type]:
    """
    Get all the nodes from the class. Starting from the base class.
        Mapping: class_name -> class

    Parameters
    ----------
    cls
        The class to get the nodes from.
    filter_types
        The types to filter out.
    """

    def _get_nodes(cls: type, base_cls: type, filter_types: tuple[type, ...]) -> dict[str, type]:
        nodes: dict[str, type] = {}
        for node in cls.__subclasses__():
            _add_nodes(node, nodes, _get_nodes(node, base_cls, filter_types), base_cls)

            if node not in filter_types:
                nodes[node.__name__] = node

        return nodes

    return _get_nodes(cls, cls, filter_types)


def get_all_fields(cls: type) -> set[str]:
    """
    Get all the fields from the class.

    Parameters
    ----------
    cls
        The class to get the fields from.
    """

    return {property_name for property_name in dir(cls) if isinstance(getattr_static(cls, property_name), field)}


def _get_mixin_fields(cls: type) -> set[str]:
    """
    Get all the mixin fields from the class.

    Parameters
    ----------
    cls
        The class to get the mixin fields from.

    Returns
    -------
        The mixin fields of the class.
    """

    mixin_fields = set()
    if issubclass(cls, ExtraFieldsMixin):
        for base in cls.__bases__:
            if issubclass(base, ExtraFieldsMixin):
                if base is ExtraFieldsMixin:
                    # This means that cls is the actual mixin class
                    new_fields = get_all_fields(cls)
                else:
                    # This means cls is a child of the class with the mixin
                    new_fields = _get_mixin_fields(base)
                mixin_fields.update(new_fields)
    return mixin_fields


def get_node_fields(cls: type) -> tuple[str, ...]:
    """
    Get all the node fields from the class.
        This excludes the reserved fields and mixin fields.

    Parameters
    ----------
    cls
        The class to get the node fields from.
    """
    from ._registry import RDM_NODE_REGISTRY

    return tuple(
        property_name
        for property_name in get_all_fields(cls)
        if (
            property_name not in (*RDM_NODE_REGISTRY.reserved_fields, *_get_mixin_fields(cls))
            and not property_name.startswith("_")
        )
    )


def wrap_into_node(
    value: Any, signature: type[DNode[_T] | LNode[_T] | ScalarNode | _T]
) -> DNode[_T] | LNode[_T] | ScalarNode | _T | Any:
    """
    Wrap things into node containers if necessary.

    Parameters
    ----------
    value
        The value to coerce.
    signature
        A type annotation
    """
    from ._node import ScalarNode

    args = get_args(signature)

    # This is a true type
    # -> signature is the type
    if not args:
        # Only coerce nodes
        if issubclass(signature, DNode) or issubclass(signature, LNode) or issubclass(signature, ScalarNode):
            # Skip if we are already the correct type
            if not isinstance(value, signature):
                # ScalarNode is detected as having no args, it will be
                # mixed with something that has an initializer that takes
                # a single argument
                return signature(value)  # type: ignore[call-arg]

    # This is a annotated type
    if args:
        # These will always be a tuple (type, metadata)
        container, metadata = args

        # Handle DNodes and pattern nodes
        if container is DNode or (isclass(container) and issubclass(container, PatternDNode)):
            # Skip if we are already a DNode
            if not isinstance(value, container):
                # DNodes only need the container metadata
                entry = metadata

                # Coerce the dictionary entries if necessary
                try:
                    return container({key: wrap_into_node(sub_val, entry) for key, sub_val in value.items()})
                except AttributeError:
                    return value

        # handle LNodes
        if container is LNode:
            if not isinstance(value, LNode):
                # LNodes are hinted as lists, so 1 metadata entry, entry
                # Coerce the list entries to the correct type
                return LNode([wrap_into_node(sub_val, metadata) for sub_val in value])

        return wrap_into_node(value, container)

    return value
