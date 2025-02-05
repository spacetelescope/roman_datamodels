"""
The ASDF Converters to handle the serialization/deseialization of the STNode classes to ASDF.
"""

from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING, Any

from asdf import AsdfFile, get_config
from asdf.extension import Converter, ManifestExtension

from roman_datamodels.stnode.rad import RDM_NODE_REGISTRY, TaggedListNode, TaggedObjectNode

if TYPE_CHECKING:
    from roman_datamodels.stnode.rad import TagMixin

__all__ = ["NODE_EXTENSIONS"]


class _NodeConverter(Converter):
    """
    Converter for all node classes in the roman_datamodels package.
    """

    # Enable lazy-tree building for all converters.
    lazy = True

    @property
    def tags(self) -> list[str]:
        return list(RDM_NODE_REGISTRY.tagged_registry.keys())

    @property
    def types(self) -> list[type]:
        return list(RDM_NODE_REGISTRY.tagged_registry.values())

    def select_tag(self, obj: TagMixin, tags: list[str], ctx: AsdfFile) -> str:
        return obj._tag

    def to_yaml_tree(self, obj: TagMixin, tag: str, ctx: AsdfFile) -> dict[str, Any] | list[Any] | Any:
        from roman_datamodels.stnode.core import get_config

        return obj.to_asdf_tree(ctx, flush=get_config().flush_option)

    def from_yaml_tree(self, node: dict[str, Any] | Any, tag: str, ctx: AsdfFile) -> TagMixin:
        node_cls = RDM_NODE_REGISTRY.tagged_registry[tag]

        # Enum will do a form of validation (if not in enum Python will raise a ValueError)
        #    This prevents opening in these cases which is not ideal. This shorts that out
        #    as data in this case will not be wrapped into the enum
        if not get_config().validate_on_read and issubclass(node_cls, Enum):  # type: ignore[no-untyped-call]
            # MyPy cannot statically determine that `node` will be a scalar, that will be wrapped properly
            # by containing objects
            return node  # type: ignore[return-value]

        # Handle the tagged object and list nodes
        if issubclass(node_cls, TaggedObjectNode) or issubclass(node_cls, TaggedListNode):
            # MyPy doesn't know how to handle these having basically the same signature
            return node_cls(node, tag=tag)  # type: ignore[arg-type]

        # Handle the tagged scalar nodes
        # MyPy doesn't know how to handle this call
        out = node_cls(node)  # type: ignore[call-arg]
        out._instance_tag = tag
        # MyPy can't determine that the return value will be the correct type
        return out


# Create the ASDF extension for the STNode classes.
NODE_EXTENSIONS = [
    # ASDF has not implemented type hints so MyPy will complain about this
    # until they do.
    ManifestExtension.from_uri("asdf://stsci.edu/datamodels/roman/manifests/datamodels-1.0", converters=[_NodeConverter()]),  # type: ignore[no-untyped-call]
]
