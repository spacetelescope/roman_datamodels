"""
This module provides the same interface as the older, non-tag version of datamodels
for the whole asdf file. It will start very basic, initially only to support running
of the flat field step, but many other methods and capabilities will be added to
keep consistency with the JWST data model version.

It is to be subclassed by the various types of data model variants for products
"""

import warnings

import asdf
import numpy as np
import packaging.version

from roman_datamodels import stnode, validate

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

__all__ = [
    "ImageModel",
    "ScienceRawModel",
    "RampModel",
    "RampFitOutputModel",
    "GuidewindowModel",
    "FlatRefModel",
    "DarkRefModel",
    "DistortionRefModel",
    "GainRefModel",
    "LinearityRefModel",
    "MaskRefModel",
    "PixelareaRefModel",
    "ReadnoiseRefModel",
    "RefpixRefModel",
    "SuperbiasRefModel",
    "SaturationRefModel",
    "WfiImgPhotomRefModel",
    "AssociationsModel",
    "IpcRefModel",
    "InverseLinearityRefModel",
    "MosaicModel",
    "open",
]


class MosaicModel(DataModel):
    _node_type = stnode.WfiMosaic


class ImageModel(DataModel):
    _node_type = stnode.WfiImage


class ScienceRawModel(DataModel):
    _node_type = stnode.WfiScienceRaw


class RampModel(DataModel):
    _node_type = stnode.Ramp

    @classmethod
    def from_science_raw(cls, model):
        """
        Construct a RampModel from a ScienceRawModel

        Parameters
        ----------
        model : ScienceRawModel or RampModel
            The input science raw model (a RampModel will also work)
        """

        if isinstance(model, cls):
            return model

        if isinstance(model, ScienceRawModel):
            from roman_datamodels.maker_utils import mk_ramp

            instance = mk_ramp(shape=model.shape)

            # Copy input_model contents into RampModel
            for key in model:
                # If a dictionary (like meta), overwrite entries (but keep
                # required dummy entries that may not be in input_model)
                if isinstance(instance[key], dict):
                    instance[key].update(getattr(model, key))
                elif isinstance(instance[key], np.ndarray):
                    # Cast input ndarray as RampModel dtype
                    instance[key] = getattr(model, key).astype(instance[key].dtype)
                else:
                    instance[key] = getattr(model, key)

            return cls(instance)

        raise ValueError("Input model must be a ScienceRawModel or RampModel")


class RampFitOutputModel(DataModel):
    _node_type = stnode.RampFitOutput


class AssociationsModel(DataModel):
    # Need an init to allow instantiation from a JSON file
    _node_type = stnode.Associations

    @classmethod
    def is_association(cls, asn_data):
        """
        Test if an object is an association by checking for required fields
        """
        if isinstance(asn_data, dict):
            if "asn_id" in asn_data and "asn_pool" in asn_data:
                return True
        return False


class GuidewindowModel(DataModel):
    _node_type = stnode.Guidewindow


class FlatRefModel(DataModel):
    _node_type = stnode.FlatRef


class DarkRefModel(DataModel):
    _node_type = stnode.DarkRef


class DistortionRefModel(DataModel):
    _node_type = stnode.DistortionRef


class GainRefModel(DataModel):
    _node_type = stnode.GainRef


class IpcRefModel(DataModel):
    _node_type = stnode.IpcRef


class LinearityRefModel(DataModel):
    _node_type = stnode.LinearityRef

    def get_primary_array_name(self):
        """
        Returns the name "primary" array for this model, which
        controls the size of other arrays that are implicitly created.
        This is intended to be overridden in the subclasses if the
        primary array's name is not "data".
        """
        return "coeffs"


class InverseLinearityRefModel(DataModel):
    _node_type = stnode.InverseLinearityRef

    def get_primary_array_name(self):
        """
        Returns the name "primary" array for this model, which
        controls the size of other arrays that are implicitly created.
        This is intended to be overridden in the subclasses if the
        primary array's name is not "data".
        """
        return "coeffs"


class MaskRefModel(DataModel):
    _node_type = stnode.MaskRef

    def get_primary_array_name(self):
        """
        Returns the name "primary" array for this model, which
        controls the size of other arrays that are implicitly created.
        This is intended to be overridden in the subclasses if the
        primary array's name is not "data".
        """
        return "dq"


class PixelareaRefModel(DataModel):
    _node_type = stnode.PixelareaRef


class ReadnoiseRefModel(DataModel):
    _node_type = stnode.ReadnoiseRef


class SuperbiasRefModel(DataModel):
    _node_type = stnode.SuperbiasRef


class SaturationRefModel(DataModel):
    _node_type = stnode.SaturationRef


class WfiImgPhotomRefModel(DataModel):
    _node_type = stnode.WfiImgPhotomRef


class RefpixRefModel(DataModel):
    _node_type = stnode.RefpixRef


def open(init, memmap=False, target=None, **kwargs):
    """
    Data model factory function

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
