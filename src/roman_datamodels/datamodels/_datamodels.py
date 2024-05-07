"""
This module provides all the specific datamodels used by the Roman pipeline.
    These models are what will be read and written by the pipeline to ASDF files.
    Note that we require each model to specify a _node_type, which corresponds to
    the top-level STNode type that the datamodel wraps. This STNode type is derived
    from the schema manifest defined by RAD.
"""

import asdf
import numpy as np
from astropy.table import QTable

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
        """Register each subclass in the __all__ for this module"""
        super().__init_subclass__(**kwargs)

        # Don't register private classes
        if cls.__name__.startswith("_"):
            return

        if cls.__name__ in __all__:
            raise ValueError(f"Duplicate model type {cls.__name__}")

        __all__.append(cls.__name__)


class _RomanDataModel(_DataModel):
    def __init__(self, init=None, **kwargs):
        super().__init__(init, **kwargs)

        if init is not None:
            self.meta.model_type = self.__class__.__name__


class MosaicModel(_RomanDataModel):
    _node_type = stnode.WfiMosaic

    def append_individual_image_meta(self, meta):
        """
        Add the contents of meta to the appropriate keyword in individual_image_meta as an astropy QTable.

        Parameters
        ----------
        meta : roman_datamodels.stnode._node.DNode or dict
            Metadata from a component image of the mosiac.
        """

        # Convert input to a dictionary, if necessary
        if not isinstance(meta, dict):
            meta_dict = meta.to_flat_dict()
        else:
            meta_dict = meta

        # Storage for keys and values in the base meta layer
        basic_cols = []
        basic_vals = []

        # Sift through meta items to place in tables
        for key, value in meta_dict.items():
            # Skip wcs objects
            if key == "wcs":
                continue

            # Keys that are themselves Dnodes (subdirectories)
            # neccessitate a new table
            if isinstance(value, stnode.DNode):
                # Storage for keys and values
                subtable_cols = []
                subtable_vals = []

                # Loop over items within the node
                for subkey, subvalue in meta_dict[key].items():
                    # Skip ndarrays
                    if isinstance(subvalue, asdf.tags.core.ndarray.NDArrayType):
                        continue
                    # Skip QTables
                    if isinstance(subvalue, QTable):
                        continue

                    subtable_cols.append(subkey)

                    if isinstance(subvalue, (list, dict)):
                        subtable_vals.append([str(subvalue)])
                    else:
                        subtable_vals.append([subvalue])

                # Skip this Table if it would be empty
                if len(subtable_vals) == 0:
                    continue

                # Make new Keyword Table if needed
                if (key not in self.meta.individual_image_meta) or (self.meta.individual_image_meta[key].colnames == ["dummy"]):
                    self.meta.individual_image_meta[key] = QTable(names=subtable_cols, data=subtable_vals)
                else:
                    # Append to existing table
                    self.meta.individual_image_meta[key].add_row(subtable_vals)
            # Skip non-schema metas
            elif isinstance(value, dict):
                continue
            # Skip ndarrays
            elif isinstance(value.strip(), asdf.tags.core.ndarray.NDArrayType):
                continue
            # Skip QTables
            elif isinstance(value, QTable):
                continue
            else:
                # Store Basic keyword
                basic_cols.append(key)

                # Store value (lists converted to strings)
                if isinstance(value.strip(), list):
                    basic_vals.append([str(value)])
                else:
                    basic_vals.append([value])

        # Make Basic Table if needed
        if self.meta.individual_image_meta.basic.colnames == ["dummy"]:
            self.meta.individual_image_meta.basic = QTable(names=basic_cols, data=basic_vals)
        else:
            # Append to existing basic table
            self.meta.individual_image_meta.basic.add_row(basic_vals)


class ImageModel(_RomanDataModel):
    _node_type = stnode.WfiImage


class ScienceRawModel(_RomanDataModel):
    _node_type = stnode.WfiScienceRaw


class MsosStackModel(_RomanDataModel):
    _node_type = stnode.MsosStack


class RampModel(_RomanDataModel):
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


class RampFitOutputModel(_RomanDataModel):
    _node_type = stnode.RampFitOutput


class AssociationsModel(_DataModel):
    # Need an init to allow instantiation from a JSON file
    _node_type = stnode.Associations

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


class GuidewindowModel(_RomanDataModel):
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


class InverselinearityRefModel(_DataModel):
    _node_type = stnode.InverselinearityRef

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


class FpsModel(_DataModel):
    _node_type = stnode.Fps


class TvacModel(_DataModel):
    _node_type = stnode.Tvac


class MosaicSourceCatalogModel(_RomanDataModel):
    _node_type = stnode.MosaicSourceCatalog


class MosaicSegmentationMapModel(_RomanDataModel):
    _node_type = stnode.MosaicSegmentationMap


class SourceCatalogModel(_RomanDataModel):
    _node_type = stnode.SourceCatalog


class SegmentationMapModel(_RomanDataModel):
    _node_type = stnode.SegmentationMap
