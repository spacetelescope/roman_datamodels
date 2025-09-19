"""
This module contains the utility functions for the datamodels sub-package. Mainly
    the open/factory function for creating datamodels
"""

from __future__ import annotations

import warnings
from collections.abc import Generator, Iterable, Mapping
from contextlib import contextmanager
from pathlib import Path
from typing import TYPE_CHECKING, Any

import asdf
import numpy as np

from ._core import MODEL_REGISTRY, DataModel

if TYPE_CHECKING:
    from astropy.time import Time

    from roman_datamodels.stnode import Stnode


__all__ = ["FilenameMismatchWarning", "node_update", "rdm_open", "temporary_update_filedate", "temporary_update_filename"]


class FilenameMismatchWarning(UserWarning):
    """
    Warning when the filename in the meta attribute does not match the filename
    of the file being opened.
    """


def _temporary_update(datamodel: DataModel, key: str, value: Any) -> Generator[None, None, None]:
    """
    Temporary update some meta key of a datamodel so that it can be saved with
    that value without changing the current model's version of that value.

    Parameters
    ----------
    datamodel :
        The datamodel instance to update.

    key : str
        The key to update in the datamodel's meta attribute.

    value : Any
        The value to set for the key in the datamodel's meta attribute.
    """
    if "meta" in datamodel._instance and key in datamodel._instance.meta:
        old_value = getattr(datamodel._instance.meta, key)
        setattr(datamodel._instance.meta, key, value)

        yield
        setattr(datamodel._instance.meta, key, old_value)
        return

    yield
    return


@contextmanager
def temporary_update_filename(datamodel: DataModel, filename: str) -> Generator[None, None, None]:
    """
    Context manager to temporarily update the filename of a datamodel so that it
    can be saved with that new file name without changing the current model's filename

    Parameters
    ----------
    datamodel : DataModel
        The datamodel instance to update.

    filename : str
        The new filename to use.
    """
    yield from _temporary_update(datamodel, "filename", filename)


@contextmanager
def temporary_update_filedate(datamodel: DataModel, file_date: Time) -> Generator[None, None, None]:
    """
    Context manager to temporarily update the filedate of a datamodel so that it
    can be saved with that new file date without changing the current model's filedate.

    Parameters
    ----------
    datamodel
        The datamodel instance to update.
    file_date
        The new file date to use.
    """
    yield from _temporary_update(datamodel, "file_date", file_date)


def node_update(
    to_node: Stnode,
    from_node: Stnode | DataModel,
    extras: Iterable[str] | None = None,
    extras_key: str | None = None,
    ignore: Iterable[str] | None = None,
) -> None:
    """Copy node contents from an existing node to another existing node

    How the copy occurs depends on existence of keys in `to_node`

    If key exists in `to_node`, contents are converted from `from_node` stnode type to
    the stnode type expected in order to preserve validation of the node.

    If key only exists in `from_node`, the contents are copied as-is.

    If key exists in the list `extras`, the contents are placed in the dict `["extras"]`.
    if `extras_key` is given, then the sub-dictionary `["extras"][extras_key]` is used.
    Extra keys are used to avoid collisions between node trees where the underlying structures are
    completely different.

    Keys in `ignore` are not considered.

    Keys are also

    Parameters
    ----------
    to_node : stnode
        Node to receive the contents.

    from_node : stnode, DataModel
        Node to copy from

    extras : [str[,...]]
        Keys that may create collisions between the two node trees. All such keys are placed
        in the `extras` key. If `extras_key` is defined, the contents are placed in a subdict
        of that name.

    extras_key : str or None
        See parameter `extras`.

    ignore : list-like or None
        Keys that should be completely ignored.
    """

    # Define utilities functions
    def _descend(attributes, key):
        next_attributes = []
        for item in attributes:
            level, _, name = item.partition(".")
            if level == key and name:
                next_attributes.append(name)
        return next_attributes

    def _traverse(to_node, from_node, extras=None, ignore=None):
        if extras is None:
            extras = ()
        new_extras = {}
        if ignore is None:
            ignore = ()

        for key in from_node.keys():
            if key in ignore:
                continue
            if key in extras:
                new_extras[key] = from_node[key]
                continue
            if key in to_node:
                if isinstance(to_node[key], Mapping):
                    next_extras = _descend(extras, key)
                    next_ignores = _descend(ignore, key)
                    returned_extras = _traverse(
                        getattr(to_node, key), getattr(from_node, key), extras=next_extras, ignore=next_ignores
                    )
                    if returned_extras:
                        new_extras[key] = returned_extras
                else:
                    if isinstance(to_node[key], list):
                        value = getattr(from_node, key).data
                    elif isinstance(to_node[key], np.ndarray):
                        value = getattr(from_node, key).astype(to_node[key].dtype)
                        value = getattr(value, "value", value)
                    else:
                        value = getattr(from_node, key)
                    setattr(to_node, key, value)
            else:
                to_node[key] = from_node[key]
        return new_extras

    # Now do the copy.
    new_extras = _traverse(to_node, from_node, extras=extras, ignore=ignore)
    if new_extras:
        if isinstance(to_node, Mapping):
            extras_node = to_node.get("extras", dict())

            if extras_key:
                extras_node[extras_key] = new_extras
            else:
                extras_node.update(new_extras)
            to_node["extras"] = extras_node


def _open_asdf(init, lazy_tree=True, **kwargs):
    """
    Open init with `asdf.open`.

    If init is a path-like object the ``roman.meta.filename`` attribute
    will be checked against ``Path.name`` and updated if they does not match.

    Parameters
    ----------
    init : str, ``Path`` or file-like
        An object that can be opened by `asdf.open`
    lazy_tree : bool
        If we should open the file with a "lazy tree"
    **kwargs:
        Any additional arguments to pass to asdf.open

    Returns
    -------
    `asdf.AsdfFile`
    """
    # asdf defaults to lazy_tree=False, this overwrites it to
    # lazy_tree=True for roman_datamodels
    kwargs["lazy_tree"] = lazy_tree
    if isinstance(init, str):
        path = Path(init)
    elif isinstance(init, Path):
        path = init
    else:
        path = None

    try:
        asdf_file = asdf.open(init, **kwargs)
    except ValueError as err:
        raise TypeError("Open requires a filepath, file-like object, or Roman datamodel") from err

    if (
        path is not None
        and "roman" in asdf_file
        and isinstance(asdf_file["roman"], Mapping)  # Fix issue for Python 3.10
        and "meta" in asdf_file["roman"]
        and "filename" in asdf_file["roman"]["meta"]
        and asdf_file["roman"]["meta"]["filename"] != path.name
    ):
        warnings.warn(
            f"meta.filename: {asdf_file['roman']['meta']['filename']} does not match filename: {path.name}, updating the filename in memory!",
            FilenameMismatchWarning,
            stacklevel=2,
        )
        asdf_file["roman"]["meta"]["filename"] = type(asdf_file["roman"]["meta"]["filename"])(path.name)

    return asdf_file


def rdm_open(init, memmap=False, **kwargs):
    """
    Datamodel open/create function.
        This function opens a Roman datamodel from an asdf file or generates
        the datamodel from an existing one.

    Parameters
    ----------
    init : str, ``Path``, `DataModel`, `asdf.AsdfFile`, file-like
        May be any one of the following types:
            - `asdf.AsdfFile` instance
            - string or ``Path`` indicating the path to an ASDF file
            - `DataModel` Roman data model instance
            - file-like object compatible with `asdf.open`
    memmap : bool
        Open ASDF file binary data using memmap (default: False)

    Returns
    -------
    `DataModel`
    """
    if isinstance(init, str | Path):
        if Path(init).suffix.lower() == ".json":
            try:
                from romancal.datamodels.library import ModelLibrary  # type: ignore[import-not-found]

                return ModelLibrary(init)
            except ImportError as err:
                raise ImportError("Please install romancal to allow opening associations with roman_datamodels") from err

    if isinstance(init, DataModel):
        # Copy the object so it knows not to close here
        return init.copy(deepcopy=False)

    # Temp fix to catch JWST args before being passed to asdf open
    kwargs.pop("asn_n_members", None)

    asdf_file = init if isinstance(init, asdf.AsdfFile) else _open_asdf(init, memmap=memmap, **kwargs)
    if (model_type := type(asdf_file.tree["roman"])) in MODEL_REGISTRY:
        return MODEL_REGISTRY[model_type](asdf_file, **kwargs)

    # Check if the datamodel is a GDPS datamodel
    try:
        import roman_gdps  # type: ignore[import-not-found]  # noqa: F401
    except ImportError as err:
        asdf_file.close()
        raise ImportError("Please install roman-gdps to allow opening GDPS datamodels") from err

    # We assume at this point that an asdf file with `roman` key is a GDPS datamodel
    if "roman" in asdf_file.tree:
        return asdf_file.tree["roman"]

    asdf_file.close()
    raise TypeError(f"Unknown datamodel type: {model_type}")
