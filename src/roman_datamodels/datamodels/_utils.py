"""
This module contains the utility functions for the datamodels sub-package. Mainly
    the open/factory function for creating datamodels
"""
import warnings

import asdf
import packaging.version

from roman_datamodels import validate

from ._core import MODEL_REGISTRY, DataModel

# .dev is included in the version comparison to allow for correct version
# comparisons with development versions of asdf 3.0
if packaging.version.Version(asdf.__version__) < packaging.version.Version("3.dev"):
    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            category=asdf.exceptions.AsdfDeprecationWarning,
            message=r"AsdfInFits has been deprecated.*",
        )
        from asdf.fits_embed import AsdfInFits
else:
    AsdfInFits = None


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
    kwargs:
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
            return init.copy()

        # Temp fix to catch JWST args before being passed to asdf open
        if "asn_n_members" in kwargs:
            del kwargs["asn_n_members"]

        if isinstance(init, asdf.AsdfFile):
            asdf_file = init
        else:
            asdf_file = _open_path_like(init, memmap=memmap, **kwargs)

        modeltype = type(asdf_file.tree["roman"])
        if modeltype in MODEL_REGISTRY:
            return MODEL_REGISTRY[modeltype](asdf_file, **kwargs)
        else:
            return DataModel(asdf_file, **kwargs)
