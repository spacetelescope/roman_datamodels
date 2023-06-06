"""
This module provides the same interface as the older, non-tag version of datamodels
for the whole asdf file. It will start very basic, initially only to support running
of the flat field step, but many other methods and capabilities will be added to
keep consistency with the JWST data model version.

It is to be subclassed by the various types of data model variants for products
"""

import numpy as np

from roman_datamodels import stnode

from ._core import DataModel

__all__ = []


class _DataModel(DataModel):
    """
    Exists only to populate the __all__ for this file automatically
        This is something which is easily missed, but is important for the automatic
        documentation generation to work properly.
    """

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if cls.__name__ in __all__:
            raise ValueError(f"Duplicate model type {cls.__name__}")

        __all__.append(cls.__name__)


class MosaicModel(_DataModel):
    _node_type = stnode.WfiMosaic


class ImageModel(_DataModel):
    _node_type = stnode.WfiImage


class ScienceRawModel(_DataModel):
    _node_type = stnode.WfiScienceRaw


class RampModel(_DataModel):
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


class RampFitOutputModel(_DataModel):
    _node_type = stnode.RampFitOutput


class AssociationsModel(_DataModel):
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


class GuidewindowModel(_DataModel):
    _node_type = stnode.Guidewindow


class FlatRefModel(_DataModel):
    _node_type = stnode.FlatRef


class DarkRefModel(_DataModel):
    _node_type = stnode.DarkRef


class DistortionRefModel(_DataModel):
    _node_type = stnode.DistortionRef


class GainRefModel(_DataModel):
    _node_type = stnode.GainRef


class IpcRefModel(_DataModel):
    _node_type = stnode.IpcRef


class LinearityRefModel(_DataModel):
    _node_type = stnode.LinearityRef

    def get_primary_array_name(self):
        """
        Returns the name "primary" array for this model, which
        controls the size of other arrays that are implicitly created.
        This is intended to be overridden in the subclasses if the
        primary array's name is not "data".
        """
        return "coeffs"


class InverseLinearityRefModel(_DataModel):
    _node_type = stnode.InverseLinearityRef

    def get_primary_array_name(self):
        """
        Returns the name "primary" array for this model, which
        controls the size of other arrays that are implicitly created.
        This is intended to be overridden in the subclasses if the
        primary array's name is not "data".
        """
        return "coeffs"


class MaskRefModel(_DataModel):
    _node_type = stnode.MaskRef

    def get_primary_array_name(self):
        """
        Returns the name "primary" array for this model, which
        controls the size of other arrays that are implicitly created.
        This is intended to be overridden in the subclasses if the
        primary array's name is not "data".
        """
        return "dq"


class PixelareaRefModel(_DataModel):
    _node_type = stnode.PixelareaRef


class ReadnoiseRefModel(_DataModel):
    _node_type = stnode.ReadnoiseRef


class SuperbiasRefModel(_DataModel):
    _node_type = stnode.SuperbiasRef


class SaturationRefModel(_DataModel):
    _node_type = stnode.SaturationRef


class WfiImgPhotomRefModel(_DataModel):
    _node_type = stnode.WfiImgPhotomRef


class RefpixRefModel(_DataModel):
    _node_type = stnode.RefpixRef
