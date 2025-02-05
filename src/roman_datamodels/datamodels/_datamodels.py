from __future__ import annotations

from collections.abc import Mapping
from enum import Enum
from typing import Any, cast

import asdf
import asdf.lazy_nodes
import numpy as np
from astropy.table import QTable

from roman_datamodels import nodes, stnode

from ._core import DataModel

__all__ = [
    "AbvegaoffsetRefModel",
    "ApcorrRefModel",
    "AssociationsModel",
    "DarkRefModel",
    "DistortionRefModel",
    "EpsfRefModel",
    "FlatRefModel",
    "FpsModel",
    "GainRefModel",
    "GuidewindowModel",
    "ImageModel",
    "ImageSourceCatalogModel",
    "InverselinearityRefModel",
    "IpcRefModel",
    "LinearityRefModel",
    "MaskRefModel",
    "MosaicModel",
    "MosaicSegmentationMapModel",
    "MosaicSourceCatalogModel",
    "MsosStackModel",
    "PixelareaRefModel",
    "RampFitOutputModel",
    "RampModel",
    "ReadnoiseRefModel",
    "RefpixRefModel",
    "SaturationRefModel",
    "ScienceRawModel",
    "SegmentationMapModel",
    "SuperbiasRefModel",
    "TvacModel",
    "WfiImageModel",
    "WfiImgPhotomRefModel",
    "WfiMosaicModel",
    "WfiScienceRawModel",
]


class AssociationsModel(DataModel[Any], nodes.Associations):
    """
    A model for the Roman associations file
    """

    @classmethod
    def is_association(cls, asn_data: dict[str, Any] | Any) -> bool:
        """
        Test if an object is an association by checking for required fields

        Parameters
        ----------
        asn_data :
            The data to be tested.
        """
        return isinstance(asn_data, dict) and "asn_id" in asn_data and "asn_pool" in asn_data


class GuidewindowModel(DataModel[Any], nodes.Guidewindow):
    """
    A model for the Roman guide window file
    """


class ImageSourceCatalogModel(DataModel[Any], nodes.ImageSourceCatalog):
    """
    A model for the Roman image source catalog file
    """


class MosaicSegmentationMapModel(DataModel[Any], nodes.MosaicSegmentationMap):
    """
    A model for the Roman mosaic segmentation map file
    """


class MosaicSourceCatalogModel(DataModel[Any], nodes.MosaicSourceCatalog):
    """
    A model for the Roman mosaic source catalog file
    """


class MsosStackModel(DataModel[Any], nodes.MsosStack):
    """
    A model for the Roman MSOS stack file
    """


class RampFitOutputModel(DataModel[Any], nodes.RampFitOutput):
    """
    A model for the Roman ramp fit output file
    """


class RampModel(DataModel[Any], nodes.Ramp):
    """
    A model for the Roman ramp file
    """

    @classmethod
    def from_science_raw(cls, model: RampModel | ScienceRawModel | FpsModel | TvacModel) -> RampModel:
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
        ramp = RampModel(_array_shape=model._array_shape_)

        # check if the input model has a resultantdq from SDF
        if hasattr(model, "resultantdq"):
            ramp.groupdq = model.resultantdq.copy()

        # Define how to recursively copy all attributes.
        def node_update(ramp: nodes.Ramp, other: RampModel | ScienceRawModel | FpsModel | TvacModel) -> None:
            """Implement update to directly access each value"""
            for key in other.keys():
                if key == "resultantdq":
                    continue
                if key in ramp.fields:
                    if isinstance(ramp[key], Mapping):
                        node_update(getattr(ramp, key), getattr(other, key))
                    elif isinstance(ramp[key], list):
                        setattr(ramp, key, getattr(other, key).data)
                    elif isinstance(ramp[key], np.ndarray):
                        setattr(ramp, key, getattr(other, key).astype(ramp[key].dtype))
                    else:
                        setattr(ramp, key, getattr(other, key))
                else:
                    # This covers anything not in the schema
                    ramp[key] = other[key]

        node_update(ramp, model)

        return ramp


class SegmentationMapModel(DataModel[Any], nodes.SegmentationMap):
    """
    A model for the Roman segmentation map file
    """


class ImageModel(DataModel[Any], nodes.WfiImage):
    """
    A model for the Roman WFI image file
    """


WfiImageModel = ImageModel


class MosaicModel(DataModel[Any], nodes.WfiMosaic):
    """
    A model for the Roman WFI mosaic file
    """

    # May want this to be ALL, so everything is included, but that maybe a lot of
    # dummy data
    def append_individual_image_meta(
        self,
        meta: stnode.DNode[Any] | dict[str, Any] | asdf.lazy_nodes.AsdfDictNode,
        flush: stnode.FlushOptions = stnode.FlushOptions.REQUIRED,
    ) -> None:
        """
        Add the contents of meta to the appropriate keyword in individual_image_meta as an astropy QTable.

        Parameters
        ----------
        meta
            Metadata from a component image of the mosiac.
        flush
            The method used to flush out the nodes if necessary.
        """

        # Convert input to a dictionary, if necessary
        if not isinstance(meta, dict | asdf.lazy_nodes.AsdfDictNode):
            meta_dict = meta.to_flat_dict()
        else:
            # Flush the meta node if it is an ObjectNode, so its properties are
            # all populated
            meta_dict = cast(dict[str, Any], meta)

        # Storage for keys and values in the base meta layer
        basic_cols = []
        basic_vals = []

        # MyPy can't correctly inver that we may be passing super classes of DNode
        # So it complains about the expression below
        iterator = (
            meta_dict.flat_items(flush=flush)
            if isinstance(meta_dict, stnode.ObjectNode)  # type: ignore[redundant-expr, unreachable]
            else meta_dict.items()
        )
        # Sift through meta items to place in tables
        for key, value in iterator:
            # Skip wcs objects
            if key == "wcs":
                continue

            # Keys that are themselves Dnodes (subdirectories)
            # neccessitate a new table
            if isinstance(value, dict | asdf.tags.core.ndarray.NDArrayType | QTable | asdf.lazy_nodes.AsdfDictNode):
                continue

            if isinstance(value, stnode.DNode):
                # Flush the node if it is an ObjectNode, so its properties are
                # all populated

                # Storage for keys and values
                subtable_cols = []
                subtable_vals = []

                sub_iterator = (
                    meta_dict[key].flat_items(flush=flush)
                    if isinstance(meta_dict[key], stnode.ObjectNode)
                    else meta_dict[key].items()
                )

                # Loop over items within the node
                for subkey, subvalue in sub_iterator:
                    # Skip ndarrays and QTables
                    if isinstance(subvalue, asdf.tags.core.ndarray.NDArrayType | QTable):
                        continue

                    # Unwrap Enum values
                    subvalue = subvalue.value if isinstance(subvalue, Enum) else subvalue
                    subvalue = np.nan if subvalue is None else subvalue
                    subtable_cols.append(subkey)
                    subtable_vals.append(
                        [str(subvalue)]
                        if isinstance(
                            subvalue, list | dict | asdf.lazy_nodes.AsdfDictNode | asdf.lazy_nodes.AsdfListNode | stnode.LNode
                        )
                        else [subvalue]
                    )

                # Skip this Table if it would be empty
                if subtable_vals:
                    # Make new Keyword Table if needed
                    if (key not in self.meta.individual_image_meta) or (
                        self.meta.individual_image_meta[key].colnames == ["dummy"]
                    ):
                        # Astropy has not implemented type hints for Table so MyPy will complain about this
                        # until they do.
                        self.meta.individual_image_meta[key] = QTable(names=subtable_cols, data=subtable_vals)  # type: ignore[no-untyped-call]
                    else:
                        # Append to existing table
                        self.meta.individual_image_meta[key].add_row(subtable_vals)
            else:
                # Store Basic keyword
                basic_cols.append(key)
                basic_vals.append([str(value)] if isinstance(value, list | asdf.lazy_nodes.AsdfListNode) else [value])

        # Make Basic Table if needed
        if self.meta.individual_image_meta.basic.colnames == ["dummy"]:
            # Astropy has not implemented type hints for Table so MyPy will complain about this
            # until they do.
            self.meta.individual_image_meta.basic = QTable(names=basic_cols, data=basic_vals)  # type: ignore[no-untyped-call]
        else:
            # Append to existing basic table
            # Astropy has not implemented type hints for Table so MyPy will complain about this
            # until they do.
            self.meta.individual_image_meta.basic.add_row(basic_vals)  # type: ignore[no-untyped-call]


WfiMosaicModel = MosaicModel


class ScienceRawModel(DataModel[Any], nodes.WfiScienceRaw):
    """
    A model for the Roman WFI science raw file
    """


WfiScienceRawModel = ScienceRawModel


class FpsModel(DataModel[Any], nodes.Fps):
    """
    A model for the Roman FPS file
    """


class AbvegaoffsetRefModel(DataModel[Any], nodes.AbvegaoffsetRef):
    """
    A model for the Roman ABVegaOffset file
    """


class ApcorrRefModel(DataModel[Any], nodes.ApcorrRef):
    """
    A model for the Roman APCorr reference file
    """


class DarkRefModel(DataModel[Any], nodes.DarkRef):
    """
    A model for the Roman dark reference file
    """


class DistortionRefModel(DataModel[Any], nodes.DistortionRef):
    """
    A model for the Roman distortion reference file
    """


class EpsfRefModel(DataModel[Any], nodes.EpsfRef):
    """
    A model for the Roman EPSF reference file
    """


class FlatRefModel(DataModel[Any], nodes.FlatRef):
    """
    A model for the Roman flat reference file
    """


class GainRefModel(DataModel[Any], nodes.GainRef):
    """
    A model for the Roman gain reference file
    """


class InverselinearityRefModel(DataModel[Any], nodes.InverselinearityRef):
    """
    A model for the Roman Inverse Linearity reference file
    """


class IpcRefModel(DataModel[Any], nodes.IpcRef):
    """
    A model for the Roman IPC reference file
    """


class LinearityRefModel(DataModel[Any], nodes.LinearityRef):
    """
    A model for the Roman Linearity reference file
    """


class MaskRefModel(DataModel[Any], nodes.MaskRef):
    """
    A model for the Roman mask reference file
    """


class PixelareaRefModel(DataModel[Any], nodes.PixelareaRef):
    """
    A model for the Roman pixel area reference file
    """


class ReadnoiseRefModel(DataModel[Any], nodes.ReadnoiseRef):
    """
    A model for the Roman readnoise reference file
    """


class RefpixRefModel(DataModel[Any], nodes.RefpixRef):
    """
    A model for the Roman Refpix reference file
    """


class SaturationRefModel(DataModel[Any], nodes.SaturationRef):
    """
    A model for the Roman saturation reference file
    """


class SuperbiasRefModel(DataModel[Any], nodes.SuperbiasRef):
    """
    A model for the Roman superbias reference file
    """


class WfiImgPhotomRefModel(DataModel[Any], nodes.WfiImgPhotomRef):
    """
    A model for the Roman WFI IMG photom reference file
    """


class TvacModel(DataModel[Any], nodes.Tvac):
    """
    A model for the Roman TVAC file
    """
