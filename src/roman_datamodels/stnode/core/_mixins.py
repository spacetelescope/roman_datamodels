from __future__ import annotations

from abc import ABC, abstractmethod
from enum import StrEnum, auto
from typing import TYPE_CHECKING, Any, Generic, TypeVar

from asdf import AsdfFile

if TYPE_CHECKING:
    from ._d_node import DNode

__all__ = [
    "AsdfNodeMixin",
    "FlushOptions",
    "NodeKeyMixin",
]

_T = TypeVar("_T")


class NodeKeyMixin:
    """
    Mixin to enable correct handling of node keys vs field keys
        Note: This is the ``pass`` vs ``pass_`` issue.
    """

    @staticmethod
    def _to_schema_key(key: str) -> str:
        """
        This exists to make it so that the _data storage always
        uses "pass" instead of "pass_" as the key.

        This is a workaround for the fact that "pass" is a very
        reserved word in Python and can't be used as function name
        for example.

        Note that this means that "pass_" and "pass" will be equivalent
        for the purposes of DNode.

        Any time we access self._data this should be used to make sure
        pass is correctly handled.
        """
        return "pass" if key == "pass_" else key

    @staticmethod
    def _to_field_key(key: str) -> str:
        """
        Matching to _handle_data_key, this is used to make sure that
        when we are using keys in reference to property (fields) names that
        "pass_" is used instead of "pass".

        Anytime fields is accessed this should be used to make sure pass is correctly handled.
        """

        return "pass_" if key == "pass" else key


class FlushOptions(StrEnum):
    """
    Options for flushing out required fields
        - NONE: Do not flush out any fields,
            - this may result in an invalid object for asdf writing
        - REQUIRED: Flush out only the required fields with their default values
        - ALL: Flush out all fields with their default values
            - this fills in all the fields listed in the schema with their default values
        - EXTRA: Flush out all fields with their default values including fields not listed in the schema
            - fills in everything from ALL, then fills in fields that are not in the schema
    """

    NONE = auto()
    REQUIRED = auto()
    ALL = auto()
    EXTRA = auto()

    @classmethod
    def get_fields(cls, node: DNode[_T], flush: FlushOptions) -> tuple[str, ...]:
        """
        Get the fields to flush out on the node based on the flush option.
        """
        match flush:
            case cls.NONE:
                return ()
            case cls.REQUIRED:
                return node.schema_required
            case cls.ALL:
                return node.defined_fields
            case cls.EXTRA:
                return node.fields
            case _:
                raise ValueError(f"Invalid flush option: {flush}")


class AsdfNodeMixin(NodeKeyMixin, Generic[_T], ABC):
    """Mixin so that Nodes can have an asdf context."""

    @abstractmethod
    def __asdf_traverse__(self) -> dict[str, _T] | list[_T] | _T:
        """Traverse the object to create the tree for the ASDF file."""

    @abstractmethod
    def unwrap(self) -> dict[str, _T] | list[_T] | _T:
        """
        Unwrap the current object into its native Python form.
            -> dict
            -> list
            -> base scalar
        """

    @abstractmethod
    def to_asdf_tree(
        self, ctx: AsdfFile, flush: FlushOptions = FlushOptions.REQUIRED, warn: bool = False
    ) -> dict[str, Any] | list[Any] | Any:
        """
        Convert the object into a form that can be written to an ASDF file.
            -> flush out any required fields
            -> traverse the container and recursively convert not-tagged objects

        Parameters
        ----------
        ctx
            The ASDF context to use for the conversion
        flush
            Options for flushing out required fields, see FlushOptions for more info
        warn
            If `True`, warn if any required fields are missing.
        """
