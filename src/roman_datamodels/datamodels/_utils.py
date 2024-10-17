"""
This module contains the utility functions for the datamodels sub-package. Mainly
    the open/factory function for creating datamodels
"""

from pathlib import Path

import asdf

from roman_datamodels import validate

from ._core import MODEL_REGISTRY, DataModel

__all__ = ["rdm_open"]


def _open_path_like(init, lazy_tree=True, **kwargs):
    """
    Attempt to open init as if it was a path-like object.

    Parameters
    ----------
    init : str
        Any path-like object that can be opened by asdf such as a valid string
    memmap : bool
        If we should open the file with memmap
    **kwargs:
        Any additional arguments to pass to asdf.open

    Returns
    -------
    `asdf.AsdfFile`
    """
    # asdf defaults to lazy_tree=False, this overwrites it to
    # lazy_tree=True for roman_datamodels
    kwargs["lazy_tree"] = lazy_tree

    try:
        asdf_file = asdf.open(init, **kwargs)
    except ValueError as err:
        raise TypeError("Open requires a filepath, file-like object, or Roman datamodel") from err

    return asdf_file


def rdm_open(init, memmap=False, **kwargs):
    """
    Datamodel open/create function.
        This function opens a Roman datamodel from an asdf file or generates
        the datamodel from an existing one.

    Parameters
    ----------
    init : str, `DataModel`, `asdf.AsdfFile`
        May be any one of the following types:
            - `asdf.AsdfFile` instance
            - string indicating the path to an ASDF file
            - `DataModel` Roman data model instance
    memmap : bool
        Open ASDF file binary data using memmap (default: False)

    Returns
    -------
    `DataModel`
    """
    if isinstance(init, str | Path):
        if Path(init).suffix.lower() == ".json":
            try:
                from romancal.datamodels.library import ModelLibrary

                return ModelLibrary(init)
            except ImportError:
                raise ImportError("Please install romancal to allow opening associations with roman_datamodels")
    with validate.nuke_validation():
        if isinstance(init, DataModel):
            # Copy the object so it knows not to close here
            return init.copy(deepcopy=False)

        # Temp fix to catch JWST args before being passed to asdf open
        if "asn_n_members" in kwargs:
            del kwargs["asn_n_members"]

        asdf_file = init if isinstance(init, asdf.AsdfFile) else _open_path_like(init, memmap=memmap, **kwargs)
        if (model_type := type(asdf_file.tree["roman"])) in MODEL_REGISTRY:
            return MODEL_REGISTRY[model_type](asdf_file, **kwargs)

        asdf_file.close()
        raise TypeError(f"Unknown datamodel type: {model_type}")
