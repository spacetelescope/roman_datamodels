from __future__ import annotations

import copy
import sys
from collections.abc import Generator
from pathlib import PurePath
from types import TracebackType
from typing import Any, TypeVar, cast

import numpy.typing as npt
from asdf import AsdfFile
from asdf.exceptions import ValidationError

from roman_datamodels.stnode import DNode, rad

from ._api import StpipeAPIMixin

__all__ = ["DataModel"]

_T = TypeVar("_T")


class DataModel(StpipeAPIMixin[_T], rad.TagMixin):
    """
    Mixin class for all data models (top-level nodes)
    -> this will be mixed with a TaggedObject Node class
    """

    def __new__(cls, init: DataModel[_T] | None = None, **kwargs: Any) -> DataModel[_T]:
        """
        Handle the case where one passes in an already instantiated version
        of the model. In this case the constructor should just directly return
        the model.
        """
        if type(init) is cls:
            return init

        return super().__new__(cls)

    def _pre_initialize_node(self, init: dict[str, _T] | DNode[_T] | AsdfFile | None = None, **kwargs: Any) -> dict[str, Any]:  # type: ignore[override]
        """
        Overwrite the default node initializer function so that we can inject
        pre processiong of the input data
        """
        if init is None:
            return {}

        if isinstance(init, dict):
            init = self.node_type()(init)

        # Pass in a node/datamodel
        if isinstance(init, rad.TaggedObjectNode):
            if not isinstance(init, self.node_type()):
                # ASDF has not implemented type hints so MyPy will complain about this
                # until they do.
                raise ValidationError(  # type: ignore[no-untyped-call]
                    f"TaggedObjectNode: {type(init).__name__} is not of the type expected. Expected {self.node_type().__name__}"
                )

            # Return the raw data (this will go directly into the node initializer)
            return cast(DNode[_T], init)._data

        # Pass in a file path -> process into asdf file
        if isinstance(init, str | bytes | PurePath):
            if isinstance(init, PurePath):  # type: ignore[unreachable]
                init = str(init)
            if isinstance(init, bytes):
                init = init.decode(sys.getfilesystemencoding())

            # Open the ASDF file
            init = self.open_asdf(init, **kwargs)

        # Handle if init is an ASDF file (or retrieved ASDF file)
        if isinstance(init, AsdfFile):
            if not self._check_type(init):
                raise ValueError(f"ASDF file is not of the type expected. Expected {type(self).__name__}")

            # Set the data model state
            self._asdf = init

            # Return the raw data (this will go directly into the node initializer)
            return cast(dict[str, Any], self._asdf.tree["roman"]._data)

        raise OSError("Argument init does not appear to be a valid ASDFfile or TaggedObjectNode")

    def __del__(self) -> None:
        """
        Ensure closure of resources when deleted.

        Note that due to the perplexities of Python's garbage collection, this
        may not be called immediately upon the dereferencing of the object, instead
        it will be called when python decides to garbage collect the object.
        This may not happen at all, meaning that the resources will be left open
        upon python exit in this case (eg exceptions)
        """
        self.close()

    def __enter__(self) -> DataModel[_T]:
        """Return the data model object if it is acting as a context manager for itself"""
        return self

    def __exit__(self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: TracebackType | None) -> None:
        """Close the ASDF file when exiting the context manager defined by the object itself"""
        self.close()

    def copy(self, deepcopy: bool = True, memo: dict[int, Any] | None = None) -> DataModel[_T]:
        result = cast(DataModel[_T], self.construct_model(None))
        self.clone(result, self, deepcopy=deepcopy, memo=memo)
        return result

    __copy__ = __deepcopy__ = copy

    @staticmethod
    def clone(target: DataModel[_T], source: DataModel[_T], deepcopy: bool = False, memo: dict[int, Any] | None = None) -> None:
        if deepcopy:
            target._asdf = source._asdf_file.copy()  # type: ignore[no-untyped-call]
            target._data = copy.deepcopy(source._data, memo=memo)
        else:
            target._asdf = source._asdf_file
            target._data = source._data

        target._is_copy = True

    def get_primary_array_name(self) -> str:
        """
        Returns the name "primary" array for this model, which
        controls the size of other arrays that are implicitly created.
        This is intended to be overridden in the subclasses if the
        primary array's name is not "data".
        """
        if isinstance(self, rad.ArrayFieldMixin):
            return self.primary_array_name

        return "data" if hasattr(self, "data") else ""

    @property
    def override_handle(self) -> str:
        """override_handle identifies in-memory models where a filepath
        would normally be used.
        """
        # Arbitrary choice to look something like crds://
        return f"override://{type(self).__name__}"

    @property
    def shape(self) -> tuple[int, ...] | None:
        """Return the shape of the model's primary array"""
        if (array := getattr(self, self.get_primary_array_name(), None)) is not None:
            return cast(tuple[int, ...], cast(npt.NDArray[Any], array.shape))
        return None

    def to_flat_dict(self, include_arrays: bool = True, recursive: bool = True) -> dict[str, Any]:
        """
        Get a flattened dictionary of the model's data
        """
        return {f"roman.{key}": val for key, val in super().to_flat_dict(include_arrays, recursive).items()}

    def __setitem__(self, key: str, value: DNode[_T] | _T) -> None:
        """
        Set an item in the data model
        """
        if key.startswith("_"):
            raise ValueError("May not specify attributes/keys that start with _")
        super().__setitem__(key, value)

    # For backwards compatibility with the old version of the datamodels which
    # did not directly inherit from their respective node types, we need to
    # override the items method to ensure that the correct items are returned
    def items(self) -> Generator[tuple[str, Any], None, None]:  # type: ignore[override]
        """
        Iterates over all of the model items in a flat way.

        Each element is a pair (``key``, ``value``).  Each ``key`` is a
        dot-separated name.  For example, the schema element
        ``meta.observation.date`` will end up in the result as::

            ("meta.observation.date": "2012-04-22T03:22:05.432")

        Unlike the JWST DataModel implementation, this does not use
        schemas directly.
        """

        yield from self._recursive_items()
