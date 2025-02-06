from __future__ import annotations

import sys
from collections.abc import Callable, Generator
from contextlib import contextmanager
from os import PathLike
from pathlib import Path
from typing import Any, TypeVar, cast

from asdf import AsdfFile
from asdf.search import AsdfSearchResult

from roman_datamodels.stnode import DNode, TaggedObjectNode
from roman_datamodels.validate import nuke_validation

__all__ = ["AsdfFileMixin"]

_T = TypeVar("_T")


@contextmanager
def _temporary_update_filename(datamodel: AsdfFileMixin[_T], filename: PathLike[str] | str) -> Generator[None, None, None]:
    """
    Context manager to temporarily update the filename of a datamodel so that it
    can be saved with that new file name without changing the current model's filename
    """
    from roman_datamodels.nodes import Filename

    dm: DNode[DNode[_T]] = cast(DNode[DNode[_T]], datamodel)

    if "meta" in cast(DNode[_T], dm.fields) and "filename" in dm.meta.fields:
        old_filename = dm.meta.filename
        dm.meta.filename = cast(_T, Filename(filename))

        yield
        dm.meta.filename = old_filename
        return

    yield
    return


class AsdfFileMixin(DNode[DNode[_T] | _T]):
    _is_copy: bool = False
    _asdf: AsdfFile | None = None

    @classmethod
    def node_type(cls) -> type:
        """
        Get the top-level node type for this model
        -> this is assumed to be the last class in the multiple inheritance
        """
        return cls.__bases__[-1]

    def construct_node(self, data: dict[str, DNode[_T] | _T]) -> TaggedObjectNode:
        """
        Construct a new node (matching the node for this model) from the given data
        """
        # MyPy can't correctly infer the typing here
        return self.node_type()(data, _array_shape=self._array_shape_)  # type: ignore[no-any-return]

    def construct_model(self, data: dict[str, DNode[_T] | _T] | DNode[DNode[_T] | _T] | None) -> AsdfFileMixin[_T]:
        """
        Construct a new model from the given data
        """
        return type(self)(data, _array_shape=self._array_shape_)

    def _init_asdf_file(self) -> None:
        """
        Initialize the ASDF file
        """
        with nuke_validation():
            # ASDF has not implemented type hints so MyPy will complain about this
            # until they do.
            af = AsdfFile()  # type: ignore[no-untyped-call]

            af["roman"] = self.construct_node(self._data)
            # ASDF has not implemented type hints so MyPy will complain about this
            # until they do.
            af.validate()  # type: ignore[no-untyped-call]
            self._asdf = af

    @property
    def _asdf_file(self) -> AsdfFile:
        """Access the ASDF file"""
        if self._asdf is None:
            self._init_asdf_file()

        return cast(AsdfFile, self._asdf)

    def _check_type(self, asdf_file: AsdfFile) -> bool:
        """
        Check that the asdf_file is the proper type of node for the datamodel
        """
        if "roman" not in asdf_file.tree:
            raise ValueError('ASDF file does not have expected "roman" attribute')

        return type(asdf_file.tree["roman"]) is self.node_type()

    def close(self) -> None:
        """Close the associated ASDF file if it can be"""
        if not self._is_copy and self._asdf is not None:
            self._asdf.close()  # type: ignore[no-untyped-call]

    def open_asdf(self, init: PathLike[str] | str | None = None, lazy_tree: bool = True, **kwargs: Any) -> AsdfFile:
        """
        Attempt to open the ASDF path

        Parameters
        ----------
        init
            Path to the ASDF file
        lazy_tree
            Whether to load the tree lazily
        **kwargs
            Arguments to asdf open
        """
        from ._utils import _open_asdf

        with nuke_validation():
            if isinstance(init, str):
                return _open_asdf(init, lazy_tree=lazy_tree, **kwargs)

            return AsdfFile(init, **kwargs)  # type: ignore[no-untyped-call]

    def to_asdf(
        self, init: PathLike[str] | str, lazy_tree: bool = True, all_array_compression: str = "lz4", **kwargs: Any
    ) -> None:
        """
        Write to the ASDF File

        Parameters
        ----------
        init
            Path to the ASDF file
        lazy_tree
            Whether to load the tree lazily
        all_array_compression
            What (if any) compression to use on all arrays default is lz4
        **kwargs
            Keyword arguments to asdf open and asdf write_to
        """
        with nuke_validation(), _temporary_update_filename(self, Path(init).name):
            asdf_file = self.open_asdf(None, lazy_tree=lazy_tree, **kwargs)
            asdf_file["roman"] = self.construct_node(self._data)
            asdf_file.write_to(init, all_array_compression=all_array_compression, **kwargs)  # type: ignore[no-untyped-call]

    def save(
        self,
        path: PathLike[str] | str | Callable[[PathLike[str] | str], PathLike[str] | str],
        dir_path: PathLike[str] | None = None,
        **kwargs: Any,
    ) -> Path:
        path = Path(path(cast(str, cast(DNode[_T], self.meta).filename)) if callable(path) else path)
        output_path = Path(dir_path) / path.name if dir_path else path
        ext = path.suffix.decode(sys.getfilesystemencoding()) if isinstance(path.suffix, bytes) else path.suffix  # type: ignore[unreachable, redundant-expr]

        # TODO: Support gzip-compressed fits
        if ext == ".asdf":
            self.to_asdf(output_path, **kwargs)
        else:
            raise ValueError(f"unknown filetype {ext}")

        return output_path

    def validate(self) -> None:
        """Validate the ASDF file"""
        self._asdf_file.validate()  # type: ignore[no-untyped-call]

    def info(self, *args: Any, **kwargs: Any) -> None:
        """Pass through to the AsdfFile info method"""
        self._asdf_file.info(*args, **kwargs)  # type: ignore[no-untyped-call]

    def search(self, *args: Any, **kwargs: Any) -> AsdfSearchResult:
        """Pass through to the AsdfFile search method"""
        return cast(AsdfSearchResult, self._asdf_file.search(*args, **kwargs))  # type: ignore[no-untyped-call]

    def schema_info(self, *args: Any, **kwargs: Any) -> Any:
        """Pass through to the AsdfFile schema_info method"""
        return self._asdf_file.schema_info(*args, **kwargs)  # type: ignore[no-untyped-call]
