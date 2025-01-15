"""
This module provides all the specific datamodels used by the Roman pipeline.
    These models are what will be read and written by the pipeline to ASDF files.
    Note that we require each model to specify a _node_type, which corresponds to
    the top-level STNode type that the datamodel wraps. This STNode type is derived
    from the schema manifest defined by RAD.
"""

from collections.abc import Mapping

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
        if not isinstance(meta, dict | asdf.lazy_nodes.AsdfDictNode):
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
            if isinstance(value, dict | asdf.tags.core.ndarray.NDArrayType | QTable | asdf.lazy_nodes.AsdfDictNode):
                continue

            if isinstance(value, stnode.DNode):
                # Storage for keys and values
                subtable_cols = []
                subtable_vals = []

                # Loop over items within the node
                for subkey, subvalue in meta_dict[key].items():
                    # Skip ndarrays and QTables
                    if isinstance(subvalue, asdf.tags.core.ndarray.NDArrayType | QTable):
                        continue

                    subtable_cols.append(subkey)
                    subtable_vals.append(
                        [str(subvalue)]
                        if isinstance(subvalue, list | dict | asdf.lazy_nodes.AsdfDictNode | asdf.lazy_nodes.AsdfListNode)
                        else [subvalue]
                    )

                # Skip this Table if it would be empty
                if subtable_vals:
                    # Make new Keyword Table if needed
                    if (key not in self.meta.individual_image_meta) or (
                        self.meta.individual_image_meta[key].colnames == ["dummy"]
                    ):
                        self.meta.individual_image_meta[key] = QTable(names=subtable_cols, data=subtable_vals)
                    else:
                        # Append to existing table
                        self.meta.individual_image_meta[key].add_row(subtable_vals)
            else:
                # Store Basic keyword
                basic_cols.append(key)
                basic_vals.append([str(value)] if isinstance(value, list | asdf.lazy_nodes.AsdfListNode) else [value])

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
        Attempt to construct a RampModel from a DataModel

        If the model has a resultantdq attribute, this is copied into
        the RampModel.groupdq attribute.

        Parameters
        ----------
        model : ScienceRawModel, TvacModel
            The input data model (a RampModel will also work).

        Returns
        -------
        ramp_model : RampModel
            The RampModel built from the input model. If the input is already
            a RampModel, it is simply returned.
        """
        ALLOWED_MODELS = (FpsModel, RampModel, ScienceRawModel, TvacModel)

        if isinstance(model, cls):
            return model
        if not isinstance(model, ALLOWED_MODELS):
            raise ValueError(f"Input must be one of {ALLOWED_MODELS}")

        # Create base ramp node with dummy values (for validation)
        from roman_datamodels.maker_utils import mk_ramp

        ramp = mk_ramp(shape=model.shape)

        # check if the input model has a resultantdq from SDF
        if hasattr(model, "resultantdq"):
            ramp.groupdq = model.resultantdq.copy()

        # Define how to recursively copy all attributes.
        def node_update(ramp, other):
            """Implement update to directly access each value"""
            for key in other.keys():
                if key == "resultantdq":
                    continue
                if key in ramp:
                    if isinstance(ramp[key], Mapping):
                        node_update(getattr(ramp, key), getattr(other, key))
                    elif isinstance(ramp[key], list):
                        setattr(ramp, key, getattr(other, key).data)
                    elif isinstance(ramp[key], np.ndarray):
                        setattr(ramp, key, getattr(other, key).astype(ramp[key].dtype))
                    else:
                        setattr(ramp, key, getattr(other, key))
                else:
                    ramp[key] = other[key]

        node_update(ramp, model)

        # Create model from node
        ramp_model = RampModel(ramp)
        return ramp_model


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


class AbvegaoffsetRefModel(_DataModel):
    _node_type = stnode.AbvegaoffsetRef


class ApcorrRefModel(_DataModel):
    _node_type = stnode.ApcorrRef


class DarkRefModel(_DataModel):
    _node_type = stnode.DarkRef


class DistortionRefModel(_DataModel):
    _node_type = stnode.DistortionRef


class EpsfRefModel(_DataModel):
    _node_type = stnode.EpsfRef


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


class ImageSourceCatalogModel(_RomanDataModel):
    _node_type = stnode.ImageSourceCatalog


class SegmentationMapModel(_RomanDataModel):
    _node_type = stnode.SegmentationMap
