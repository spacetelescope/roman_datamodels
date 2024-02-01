"""
This module contains the utility functions for the datamodels sub-package. Mainly
    the open/factory function for creating datamodels
"""

import warnings
from pathlib import Path

import asdf
from astropy.utils import minversion

from roman_datamodels import validate

from ._core import MODEL_REGISTRY, DataModel

# .dev is included in the version comparison to allow for correct version
# comparisons with development versions of asdf 3.0
if minversion(asdf, "3.dev"):
    AsdfInFits = None
else:
    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            category=asdf.exceptions.AsdfDeprecationWarning,
            message=r"AsdfInFits has been deprecated.*",
        )
        from asdf.fits_embed import AsdfInFits


__all__ = ["rdm_open"]


def _open_path_like(init, memmap=False, **kwargs):
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
    kwargs["copy_arrays"] = not memmap

    try:
        asdf_file = asdf.open(init, **kwargs)
    except ValueError as err:
        raise TypeError("Open requires a filepath, file-like object, or Roman datamodel") from err

    # This is only needed until we move min asdf version to 3.0
    if AsdfInFits is not None and isinstance(asdf_file, AsdfInFits):
        asdf_file.close()
        raise TypeError("Roman datamodels does not accept FITS files or objects")

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

        if isinstance(init, str):
            exts = Path(init).suffixes
            if not exts:
                raise ValueError(f"Input file path does not have an extension: {init}")

            # Assume json files are asn and return them
            if exts[0] == "json":
                return init

        asdf_file.close()
        raise TypeError(f"Unknown datamodel type: {model_type}")
