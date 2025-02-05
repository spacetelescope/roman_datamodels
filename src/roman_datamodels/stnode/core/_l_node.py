from __future__ import annotations

from collections import UserList
from typing import TYPE_CHECKING, Annotated, Any, TypeVar

from asdf import AsdfFile
from asdf.lazy_nodes import AsdfListNode

from ._mixins import AsdfNodeMixin, FlushOptions

if TYPE_CHECKING:
    from ..rad import TagMixin

__all__ = ["LNode"]

_T = TypeVar("_T")


# Once we are >3.11 -> LNode[T] can replace the Generic[T] in the class definition
class LNode(AsdfNodeMixin[_T], UserList[_T]):
    """
    Base class describing all "array" (list-like) data nodes for STNode classes.
    """

    def __init__(self, node: list[_T] | AsdfListNode | LNode[_T] | None = None) -> None:
        self.data: list[_T] | AsdfListNode  # type: ignore[assignment]
        if node is None:
            self.data = []
        elif isinstance(node, list | AsdfListNode):
            self.data = node
        elif isinstance(node, LNode):
            self.data = node.data
        else:
            raise ValueError("Initializer only accepts lists")

    def __class_getitem__(cls, item_type: _T) -> LNode[_T]:
        """Enable type hinting for the class"""

        # Annotated for __class_getitem__ does not quite work in MyPy
        # see python/mypy#11501
        return Annotated[cls, item_type]  # type: ignore[return-value]

    def unwrap(self) -> list[_T]:
        return list(self)

    def to_asdf_tree(
        self, ctx: AsdfFile, flush: FlushOptions = FlushOptions.REQUIRED, warn: bool = False
    ) -> list[dict[str, Any] | list[Any] | Any | _T | TagMixin]:
        from ..rad import TagMixin

        return [
            item.to_asdf_tree(ctx, flush=flush, warn=warn)
            # Only wrap if it is an AsdfNode, but not tagged,
            # ASDF will handle the tagged objects in the tree
            # itself
            if isinstance(item, AsdfNodeMixin) and not isinstance(item, TagMixin)
            else item
            for item in self.unwrap()
        ]

    def __asdf_traverse__(self) -> list[_T]:
        return self.unwrap()
