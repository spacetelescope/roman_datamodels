__all__ = ["rdm_open"]

from pathlib import Path

import asdf

from ._model import DataModel


def rdm_open(init: DataModel | str | Path | asdf.AsdfFile, memmap: bool = False, **kwargs) -> DataModel:
    """
    Datamodel open/create function.
        This function opens a Roman datamodel from an asdf file or generates
        the datamodel from an existing one.

    Parameters
    ----------
    init : str, Path, `RomanDataModel`, `asdf.AsdfFile`
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
    # Set the memmap option
    kwargs["copy_arrays"] = not memmap

    # Temp fix to catch JWST args before being passed to asdf open
    if "asn_n_members" in kwargs:
        del kwargs["asn_n_members"]

    if isinstance(init, DataModel):
        # Shallow the object so it won't close when this exits if it is used as a context
        init = init.copy(deepcopy=False)

    return DataModel.create_model(init, **kwargs)