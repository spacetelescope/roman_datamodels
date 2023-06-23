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


def rdm_open(init, memmap=False, target=None, **kwargs):
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
    target : `DataModel`
        If not None value, the `DataModel` implied by the init argument
        must be an instance of the target class. If the init value
        is already a data model, and matches the target, the init
        value is returned, not copied, as opposed to the case where
        the init value is a data model, and target is not supplied,
        and the returned value is a copy of the init value.

    Returns
    -------
    `DataModel`
    """
    with validate.nuke_validation():
        file_to_close = None
        if target is not None:
            if not issubclass(target, DataModel):
                raise ValueError("Target must be a subclass of DataModel")
        # Temp fix to catch JWST args before being passed to asdf open
        if "asn_n_members" in kwargs:
            del kwargs["asn_n_members"]
        if isinstance(init, asdf.AsdfFile):
            asdffile = init
        elif isinstance(init, DataModel):
            if target is not None:
                if not isinstance(init, target):
                    raise ValueError("First argument is not an instance of target")
                else:
                    return init
            # Copy the object so it knows not to close here
            return init.copy()
        else:
            try:
                kwargs["copy_arrays"] = not memmap
                asdffile = asdf.open(init, **kwargs)
                file_to_close = asdffile
            except ValueError:
                raise TypeError("Open requires a filepath, file-like object, or Roman datamodel")
            if AsdfInFits is not None and isinstance(asdffile, AsdfInFits):
                if file_to_close is not None:
                    file_to_close.close()
                raise TypeError("Roman datamodels does not accept FITS files or objects")
        modeltype = type(asdffile.tree["roman"])
        if modeltype in MODEL_REGISTRY:
            rmodel = MODEL_REGISTRY[modeltype](asdffile, **kwargs)
            if target is not None:
                if not issubclass(rmodel.__class__, target):
                    if file_to_close is not None:
                        file_to_close.close()
                    raise ValueError("Referenced ASDF file model type is not subclass of target")
            else:
                return rmodel
        else:
            return DataModel(asdffile, **kwargs)
