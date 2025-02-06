from __future__ import annotations

import warnings
from collections.abc import Callable
from functools import wraps
from textwrap import indent
from typing import TYPE_CHECKING, Any, Generic, TypeVar, cast, overload

from ._typing import type_checked

if TYPE_CHECKING:
    from ..rad._asdf_schema import RadSchema
    from ._d_node import DNode

    _D = TypeVar("_D", bound=DNode[Any])

__all__ = ["FieldPropertyWarning", "field"]

_T = TypeVar("_T")


class FieldPropertyWarning(UserWarning):
    """
    Warning to be raised by a field property during its introspection
    """


def _default(function: Callable[[_D], _T]) -> Callable[[_D], _T]:
    """
    Wrap the function (which was defined like a property) on an ObjectNode so that
    two things are checked:
        1. Perform a check on the ObjectNode instance to provide a warning if the
           instance is not on the latest tag.
        2. Add a type check wrapper method which is only active during certain
           testing conditions (falling back on a no-op identity decorator when
           not testing).
    The resulting function will be used as a default value producer for the property
    on the node
    """

    @wraps(function)
    def wrapper(self: _D) -> _T:
        """
        Raises a warning if the tag does not match the latest one
        """
        from ..rad._tagged import TaggedObjectNode

        if isinstance(self, TaggedObjectNode) and self._tag != self.asdf_tag_uri:
            msg = (
                f"Node is not on the latest tag: {self._tag} != {self.asdf_tag_uri} "
                "and a default value is being created.\n"
                "This may result in a value that is inconsistent with the tag used, "
                "indeed this field may not even be present in the tag's schema!"
            )
            warnings.warn(msg, FieldPropertyWarning, stacklevel=2)

        return type_checked(function)(self)

    return wrapper


class field(property, Generic[_T]):
    """
    Field descriptor for fields under properties keywords in the RAD schemas
    """

    _schema: Callable[[], RadSchema] | None = None
    _docstring: str | None = None

    def __init__(
        self,
        fget: Callable[[_D], _T],
        fset: Callable[[_D, _T], None] | None = None,
        fdel: Callable[[_D], None] | None = None,
        doc: str | None = None,
    ) -> None:
        self.default = _default(fget)

        super().__init__(None, fset, fdel, None)

    # I should be able to use a lazyproperty here, but it gets overridden by the
    # initializer for `property` called by the `super().__init__`
    @property
    def __doc__(self) -> str:  # type: ignore[override]
        if self._docstring is None:
            docstring = f"{self.default.__doc__}\n\n" if self.default.__doc__ else ""

            if self._schema:
                docstring += indent(f"{self._schema().fields[self.default.__name__].docstring}", "    ")

            self._docstring = docstring

        return self._docstring

    @overload
    def __get__(self, obj: None, objtype: type | None) -> field[_T]: ...

    @overload
    def __get__(self, obj: _D, objtype: type | None = None) -> _T: ...

    def __get__(self, obj: _D | None, objtype: type | None = None) -> _T | field[_T]:
        if obj is None:
            # This is to handle the case where we do a getattr on the class itself
            # I don't want to confuse the normal operations with adding this to the
            return self

        # MyPy seems to have an issue with the type of obj for the `obj._get_node` call
        # it believes it is `_D@__get__` but it should be `_D@__init__`, not sure why.
        #
        # The specific cast here is to let the MyPy know that the generic _get_node method
        # will be return the correct for the descriptor.
        return cast(_T, obj._get_node(self.default.__name__, lambda: self.default(obj)))  # type: ignore[arg-type]
