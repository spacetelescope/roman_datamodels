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

    @classmethod
    def create_default(cls, shape=(4088, 4088), n_images=2, filepath=None, **kwargs):
        """
        Create a MosaicModel with all data required for writing a file filled.

        Parameters
        ----------
        shape : tuple, int
            (optional, keyword-only) Shape (y, x) of data array in the model (and
            its corresponding dq/err arrays). Default is 4088 x 4088.
            If shape is a tuple of length 3, the first element is assumed to be
            n_images and will override the n_images parameter.

        n_images : int
            Number of images used to create the level 3 image. Defaults to 2.

        filepath : str
            (optional) File name and path to write model to.

        kwargs : dict[str, Any]
            (optional) Override default construction for any node
        """

        return super().create_default(shape=shape, n_images=n_images, filepath=filepath, **kwargs)

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

    @classmethod
    def create_default(cls, shape=(4088, 4088), n_groups=8, filepath=None, **kwargs):
        """
        Create a ImageModel with all data required for writing a file filled.

        Parameters
        ----------
        shape : tuple, int
            (optional, keyword-only) Shape (y, x) of data array in the model (and
            its corresponding dq/err arrays). This specified size does NOT include
            the four-pixel border of reference pixels - those are trimmed at level
            2.  This size, however, is used to construct the additional arrays that
            contain the original border reference pixels (i.e if shape = (10, 10),
            the border reference pixel arrays will have (y, x) dimensions (14, 4)
            and (4, 14)). Default is 4088 x 4088.
            If shape is a tuple of length 3, the first element is assumed to be the
            n_groups and will override any settings there.

        n_groups : int
            (optional, keyword-only) The level 2 file is flattened, but it contains
            arrays for the original reference pixels which remain 3D. n_groups
            specifies what the z dimension of these arrays should be. Defaults to 8.

        filepath : str
            (optional) File name and path to write model to.

        kwargs : dict[str, Any]
            (optional) Override default construction for any node
        """
        return super().create_default(shape=shape, n_groups=n_groups, filepath=filepath, **kwargs)


class ScienceRawModel(_RomanDataModel):
    _node_type = stnode.WfiScienceRaw

    @classmethod
    def create_default(cls, shape=(8, 4096, 4096), dq=False, filepath=None, **kwargs):
        """
        Create a default instance of this model using the maker_utils

        Parameters
        ----------
        shape : tuple, int
            (optional, keyword-only) (z, y, x) Shape of data array. This includes a
            four-pixel border representing the reference pixels. Default is
                (8, 4096, 4096)
            (8 integrations, 4088 x 4088 represent the science pixels, with the
            additional being the border reference pixels).

        dq : bool
            (optional, keyword-only) Toggle to add a data quality array for
            dropout pixels

        filepath : str
            (optional) File name and path to write model to.

        kwargs : dict[str, Any]
            (optional) Override default construction for any node
        """
        return super().create_default(shape=shape, dq=dq, filepath=filepath, **kwargs)


class MsosStackModel(_RomanDataModel):
    _node_type = stnode.MsosStack

    @classmethod
    def create_default(cls, shape=(4096, 4096), filepath=None, **kwargs):
        """
        Create a MsosStackModel with all data required for writing the maker_utils

        Parameters
        ----------
        shape : tuple, int
            (optional, keyword-only) File name and path to write model to.

        filepath : str
            (optional) File name and path to write model to.

        kwargs : dict[str, Any]
            (optional) Override default construction for any node
        """
        return super().create_default(shape=shape, filepath=filepath, **kwargs)


class RampModel(_RomanDataModel):
    _node_type = stnode.Ramp

    @classmethod
    def create_default(cls, shape=(8, 4096, 4096), filepath=None, **kwargs):
        """
        Create a RampModel with all data required for writing the maker_utils

        Parameters
        ----------
        shape : tuple, int
            (optional) Shape (z, y, x) of data array in the model (and its
            corresponding dq/err arrays). This specified size includes the
            four-pixel border of reference pixels. Default is 8 x 4096 x 4096.

        filepath : str
            (optional) File name and path to write model to.

        kwargs : dict[str, Any]
            (optional) Override default construction for any node
        """
        return super().create_default(shape=shape, filepath=filepath, **kwargs)

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

    @classmethod
    def create_default(cls, shape=(8, 4096, 4096), filepath=None, **kwargs):
        """
        Create a RampFitOutputModel with all data required for writing the maker_utils

        Parameters
        ----------
        shape : tuple, int
            (optional) Shape (z, y, x) of data array in the model (and its
            corresponding dq/err arrays). This specified size includes the
            four-pixel border of reference pixels. Default is 8 x 4096 x 4096.

        filepath : str
            (optional) File name and path to write model to.

        kwargs : dict[str, Any]
            (optional) Override default construction for any node
        """
        return super().create_default(shape=shape, filepath=filepath, **kwargs)


class AssociationsModel(_DataModel):
    # Need an init to allow instantiation from a JSON file
    _node_type = stnode.Associations

    @classmethod
    def create_default(cls, shape=(8, 4096, 4096), filepath=None, **kwargs):
        """
        Create a AssociationsModel with all data required for writing the maker_utils

        Parameters
        ----------
        shape : tuple, int
            (optional, keyword-only) The shape of the member elements of products.

        filepath : str
            (optional) File name and path to write model to.

        kwargs : dict[str, Any]
            (optional) Override default construction for any node
        """
        return super().create_default(shape=shape, filepath=filepath, **kwargs)

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

    @classmethod
    def create_default(cls, shape=(2, 8, 16, 32, 32), filepath=None, **kwargs):
        """
        Create a GuideWondowModel with all data required for writing the maker_utils

        Parameters
        ----------
        shape : tuple, int
            (optional, keyword-only) Shape of arrays in the model.

        filepath : str
            (optional) File name and path to write model to.

        kwargs : dict[str, Any]
            (optional) Override default construction for any node
        """
        return super().create_default(shape=shape, filepath=filepath, **kwargs)


class FlatRefModel(_DataModel):
    _node_type = stnode.FlatRef

    @classmethod
    def create_default(cls, shape=(4096, 4096), filepath=None, **kwargs):
        """
        Create a FlatRefModel with all data required for writing the maker_utils

        Parameters
        ----------
        shape : tuple, int
            (optional, keyword-only) Shape of arrays in the model.

        filepath : str
            (optional) File name and path to write model to.

        kwargs : dict[str, Any]
            (optional) Override default construction for any node
        """
        return super().create_default(shape=shape, filepath=filepath, **kwargs)


class AbvegaoffsetRefModel(_DataModel):
    _node_type = stnode.AbvegaoffsetRef

    @classmethod
    def create_default(cls, filepath=None, **kwargs):
        """
        Create a AbvegaoffsetRefModel with all data required for writing the maker_utils

        Parameters
        ----------
        filepath : str
            (optional) File name and path to write model to.

        kwargs : dict[str, Any]
            (optional) Override default construction for any node
        """
        return super().create_default(filepath=filepath, **kwargs)


class ApcorrRefModel(_DataModel):
    _node_type = stnode.ApcorrRef

    @classmethod
    def create_default(cls, shape=(10,), filepath=None, **kwargs):
        """
        Create a ApcorrRefModel with all data required for writing the maker_utils

        Parameters
        ----------
        shape : tuple, int
            (optional, keyword-only) Shape of arrays in the model.

        filepath : str
            (optional) File name and path to write model to.

        kwargs : dict[str, Any]
            (optional) Override default construction for any node
        """
        return super().create_default(shape=shape, filepath=filepath, **kwargs)


class DarkRefModel(_DataModel):
    _node_type = stnode.DarkRef

    @classmethod
    def create_default(cls, shape=(2, 4096, 4096), filepath=None, **kwargs):
        """
        Create a DarkRefModel with all data required for writing the maker_utils

        Parameters
        ----------
        shape : tuple, int
            (optional, keyword-only) Shape of arrays in the model.

        filepath : str
            (optional) File name and path to write model to.

        kwargs : dict[str, Any]
            (optional) Override default construction for any node
        """
        return super().create_default(shape=shape, filepath=filepath, **kwargs)


class DistortionRefModel(_DataModel):
    _node_type = stnode.DistortionRef

    @classmethod
    def create_default(cls, filepath=None, **kwargs):
        """
        Create a DistortionRefModel with all data required for writing the maker_utils

        Parameters
        ----------
        filepath : str
            (optional) File name and path to write model to.

        kwargs : dict[str, Any]
            (optional) Override default construction for any node
        """
        return super().create_default(filepath=filepath, **kwargs)


class EpsfRefModel(_DataModel):
    _node_type = stnode.EpsfRef

    @classmethod
    def create_default(cls, shape=(3, 6, 9, 361, 361), filepath=None, **kwargs):
        """
        Create EpsfRefModel with all data required for writing the maker_utils

        Parameters
        ----------
        shape : tuple, int
            (optional, keyword-only) Shape of arrays in the model.

        filepath : str
            (optional) File name and path to write model to.

        kwargs : dict[str, Any]
            (optional) Override default construction for any node
        """
        return super().create_default(shape=shape, filepath=filepath, **kwargs)


class GainRefModel(_DataModel):
    _node_type = stnode.GainRef

    @classmethod
    def create_default(cls, shape=(4096, 4096), filepath=None, **kwargs):
        """
        Create GainRefModel with all data required for writing the maker_utils

        Parameters
        ----------
        shape : tuple, int
            (optional, keyword-only) Shape of arrays in the model.

        filepath : str
            (optional) File name and path to write model to.

        kwargs : dict[str, Any]
            (optional) Override default construction for any node
        """
        return super().create_default(shape=shape, filepath=filepath, **kwargs)


class IpcRefModel(_DataModel):
    _node_type = stnode.IpcRef

    @classmethod
    def create_default(cls, shape=(3, 3), filepath=None, **kwargs):
        """
        Create IpcRefModel with all data required for writing the maker_utils

        Parameters
        ----------
        shape : tuple, int
            (optional, keyword-only) Shape of arrays in the model.

        filepath : str
            (optional) File name and path to write model to.

        kwargs : dict[str, Any]
            (optional) Override default construction for any node
        """
        return super().create_default(shape=shape, filepath=filepath, **kwargs)


class LinearityRefModel(_DataModel):
    _node_type = stnode.LinearityRef

    @classmethod
    def create_default(cls, shape=(2, 4096, 4096), filepath=None, **kwargs):
        """
        Create LinearityRefModel with all data required for writing the maker_utils

        Parameters
        ----------
        shape : tuple, int
            (optional, keyword-only) Shape of arrays in the model.

        filepath : str
            (optional) File name and path to write model to.

        kwargs : dict[str, Any]
            (optional) Override default construction for any node
        """
        return super().create_default(shape=shape, filepath=filepath, **kwargs)

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

    @classmethod
    def create_default(cls, shape=(2, 4096, 4096), filepath=None, **kwargs):
        """
        Create InverselinearityRefModel with all data required for writing the maker_utils

        Parameters
        ----------
        shape : tuple, int
            (optional, keyword-only) Shape of arrays in the model.

        filepath : str
            (optional) File name and path to write model to.

        kwargs : dict[str, Any]
            (optional) Override default construction for any node
        """
        return super().create_default(shape=shape, filepath=filepath, **kwargs)

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

    @classmethod
    def create_default(cls, shape=(4096, 4096), filepath=None, **kwargs):
        """
        Create MaskRefModel with all data required for writing the maker_utils

        Parameters
        ----------
        shape : tuple, int
            (optional, keyword-only) Shape of arrays in the model.

        filepath : str
            (optional) File name and path to write model to.

        kwargs : dict[str, Any]
            (optional) Override default construction for any node
        """
        return super().create_default(shape=shape, filepath=filepath, **kwargs)

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

    @classmethod
    def create_default(cls, shape=(4096, 4096), filepath=None, **kwargs):
        """
        Create PixelareaRefModel with all data required for writing the maker_utils

        Parameters
        ----------
        shape : tuple, int
            (optional, keyword-only) Shape of arrays in the model.

        filepath : str
            (optional) File name and path to write model to.

        kwargs : dict[str, Any]
            (optional) Override default construction for any node
        """
        return super().create_default(shape=shape, filepath=filepath, **kwargs)


class ReadnoiseRefModel(_DataModel):
    _node_type = stnode.ReadnoiseRef

    @classmethod
    def create_default(cls, shape=(4096, 4096), filepath=None, **kwargs):
        """
        Create ReadnoiseRefModel with all data required for writing the maker_utils

        Parameters
        ----------
        shape : tuple, int
            (optional, keyword-only) Shape of arrays in the model.

        filepath : str
            (optional) File name and path to write model to.

        kwargs : dict[str, Any]
            (optional) Override default construction for any node
        """
        return super().create_default(shape=shape, filepath=filepath, **kwargs)


class SuperbiasRefModel(_DataModel):
    _node_type = stnode.SuperbiasRef

    @classmethod
    def create_default(cls, shape=(4096, 4096), filepath=None, **kwargs):
        """
        Create SuperbiasRefModel with all data required for writing the maker_utils

        Parameters
        ----------
        shape : tuple, int
            (optional, keyword-only) Shape of arrays in the model.

        filepath : str
            (optional) File name and path to write model to.

        kwargs : dict[str, Any]
            (optional) Override default construction for any node
        """
        return super().create_default(shape=shape, filepath=filepath, **kwargs)


class SaturationRefModel(_DataModel):
    _node_type = stnode.SaturationRef

    @classmethod
    def create_default(cls, shape=(4096, 4096), filepath=None, **kwargs):
        """
        Create SaturationRefModel with all data required for writing the maker_utils

        Parameters
        ----------
        shape : tuple, int
            (optional, keyword-only) Shape of arrays in the model.

        filepath : str
            (optional) File name and path to write model to.

        kwargs : dict[str, Any]
            (optional) Override default construction for any node
        """
        return super().create_default(shape=shape, filepath=filepath, **kwargs)


class WfiImgPhotomRefModel(_DataModel):
    _node_type = stnode.WfiImgPhotomRef

    @classmethod
    def create_default(cls, filepath=None, **kwargs):
        """
        Create WfiImgPhotomRefModel with all data required for writing the maker_utils

        Parameters
        ----------
        shape : tuple, int
            (optional, keyword-only) Shape of arrays in the model.

        filepath : str
            (optional) File name and path to write model to.

        kwargs : dict[str, Any]
            (optional) Override default construction for any node
        """
        return super().create_default(filepath=filepath, **kwargs)


class RefpixRefModel(_DataModel):
    _node_type = stnode.RefpixRef

    @classmethod
    def create_default(cls, shape=(32, 286721), filepath=None, **kwargs):
        """
        Create RefpixRefModel with all data required for writing the maker_utils

        Parameters
        ----------
        shape : tuple, int
            (optional, keyword-only) Shape of arrays in the model.

        filepath : str
            (optional) File name and path to write model to.

        kwargs : dict[str, Any]
            (optional) Override default construction for any node
        """
        return super().create_default(shape=shape, filepath=filepath, **kwargs)


class FpsModel(_DataModel):
    _node_type = stnode.Fps

    @classmethod
    def create_default(cls, shape=(8, 4096, 4096), filepath=None, **kwargs):
        """
        Create FpsModel with all data required for writing the maker_utils

        Parameters
        ----------
        shape : tuple, int
            (optional, keyword-only) (z, y, x) Shape of data array. This includes a
            four-pixel border representing the reference pixels. Default is
                (8, 4096, 4096)
            (8 integrations, 4088 x 4088 represent the science pixels, with the
            additional being the border reference pixels).

        filepath : str
            (optional) File name and path to write model to.

        kwargs : dict[str, Any]
            (optional) Override default construction for any node
        """
        return super().create_default(shape=shape, filepath=filepath, **kwargs)


class TvacModel(_DataModel):
    _node_type = stnode.Tvac

    @classmethod
    def create_default(cls, shape=(8, 4096, 4096), filepath=None, **kwargs):
        """
        Create TvacModel with all data required for writing the maker_utils

        Parameters
        ----------
        shape : tuple, int
            (optional, keyword-only) (z, y, x) Shape of data array. This includes a
            four-pixel border representing the reference pixels. Default is
                (8, 4096, 4096)
            (8 integrations, 4088 x 4088 represent the science pixels, with the
            additional being the border reference pixels).

        filepath : str
            (optional) File name and path to write model to.

        kwargs : dict[str, Any]
            (optional) Override default construction for any node
        """
        return super().create_default(shape=shape, filepath=filepath, **kwargs)


class MosaicSourceCatalogModel(_RomanDataModel):
    _node_type = stnode.MosaicSourceCatalog

    @classmethod
    def create_default(cls, filepath=None, **kwargs):
        """
        Create MosaicSourceCatalogModel with all data required for writing the maker_utils

        Parameters
        ----------
        filepath : str
            (optional) File name and path to write model to.

        kwargs : dict[str, Any]
            (optional) Override default construction for any node
        """
        return super().create_default(filepath=filepath, **kwargs)


class MosaicSegmentationMapModel(_RomanDataModel):
    _node_type = stnode.MosaicSegmentationMap

    @classmethod
    def create_default(cls, shape=(4096, 4096), filepath=None, **kwargs):
        """
        Create a MosaicSegmentationMapModel with all data required for writing the maker_utils

        Parameters
        ----------
        shape : tuple, int
            (optional, keyword-only) File name and path to write model to.

        filepath : str
            (optional) File name and path to write model to.

        kwargs : dict[str, Any]
            (optional) Override default construction for any node
        """
        return super().create_default(shape=shape, filepath=filepath, **kwargs)


class SourceCatalogModel(_RomanDataModel):
    _node_type = stnode.SourceCatalog

    @classmethod
    def create_default(cls, filepath=None, **kwargs):
        """
        Create SourceCatalogModel with all data required for writing the maker_utils

        Parameters
        ----------
        filepath : str
            (optional) File name and path to write model to.

        kwargs : dict[str, Any]
            (optional) Override default construction for any node
        """
        return super().create_default(filepath=filepath, **kwargs)


class SegmentationMapModel(_RomanDataModel):
    _node_type = stnode.SegmentationMap

    @classmethod
    def create_default(cls, shape=(4096, 4096), filepath=None, **kwargs):
        """
        Create a SegmentationMapModel with all data required for writing the maker_utils

        Parameters
        ----------
        shape : tuple, int
            (optional, keyword-only) File name and path to write model to.

        filepath : str
            (optional) File name and path to write model to.

        kwargs : dict[str, Any]
            (optional) Override default construction for any node
        """
        return super().create_default(shape=shape, filepath=filepath, **kwargs)
