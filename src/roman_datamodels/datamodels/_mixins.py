"""
This module provides all the Mixin classes which will be dynamically mixed into
    the DataModel classes at import time.
    The name of the mixin must be of the form <DataModelName>Mixin in order for
    this to work properly.
"""
import numpy as np


class RampModelMixin:
    """
    Mixin class for dynamically generated RampModel
    """

    @classmethod
    def from_science_raw(cls, model):
        """
        Construct a RampModel from a ScienceRawModel

        Parameters
        ----------
        model : ScienceRawModel or RampModel
            The input science raw model (a RampModel will also work)
        """
        from roman_datamodels.datamodels import ScienceRawModel

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


class AssociationsModelMixin:
    """
    Mixin class for dynamically generated AssociationsModel
    """

    @classmethod
    def is_association(cls, asn_data):
        """
        Test if an object is an association by checking for required fields

        Parameters
        ----------
        asn_data :
            The data to be tested.
        """
        return isinstance(asn_data, dict) and "asn_id" in asn_data and "asn_pool" in asn_data


class LinearityRefModelMixin:
    """
    Mixin class for dynamically generated LinearityRefModel
    """

    def get_primary_array_name(self):
        """
        Returns the name "primary" array for this model, which
        controls the size of other arrays that are implicitly created.
        This is intended to be overridden in the subclasses if the
        primary array's name is not "data".
        """
        return "coeffs"


class InverseLinearityRefModelMixin(LinearityRefModelMixin):
    """
    Mixin class for dynamically generated InverseLinearityRefModel
    """

    pass


class MaskRefModelMixin:
    """
    Mixin class for dynamically generated MaskRefModel
    """

    def get_primary_array_name(self):
        """
        Returns the name "primary" array for this model, which
        controls the size of other arrays that are implicitly created.
        This is intended to be overridden in the subclasses if the
        primary array's name is not "data".
        """
        return "dq"
