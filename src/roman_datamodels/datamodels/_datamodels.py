"""
This module provides all the specific datamodels used by the Roman pipeline.
    These models are what will be read and written by the pipeline to ASDF files.
    Note that we require each model to specify a _node_type, which corresponds to
    the top-level STNode type that the datamodel wraps. This STNode type is derived
    from the schema manifest defined by RAD.
"""

from __future__ import annotations

import copy
import functools
import itertools
import logging
from pathlib import Path
from typing import TYPE_CHECKING

import astropy.table.meta
import numpy as np
from astropy.modeling import models
from astropy.time import Time

from .. import stnode
from ._core import DataModel
from ._utils import node_update, temporary_update_filedate, temporary_update_filename

if TYPE_CHECKING:
    from typing import Any

__all__ = []

DTYPE_MAP: dict[str, Any] = {}

# Define logging
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class _SourceCatalogMixin:
    __slots__ = ()

    def create_empty_catalog(self, aperture_radii=None, filters=None):
        """
        Create an empty but valid source catalog table

        Parameters
        ----------
        aperture_radii: list of int (optional)
            Aperture radii in tenths of an arcsecond.

        filters: list of str (optional)
            List of filters (for example: "f184")

        Returns
        -------
        Table
        """
        if aperture_radii:
            aperture_radii = [f"{i:02}" for i in aperture_radii]

        return self._instance._create_empty_catalog(aperture_radii, filters)

    @functools.wraps(stnode.ImageSourceCatalogMixin.get_column_definition)
    def get_column_definition(self, name):
        return self._instance.get_column_definition(name)


class _ParquetMixin:
    """Gives SourceCatalogModels the ability to save to parquet files."""

    __slots__ = ()

    def to_parquet(self, filepath):
        """
        Save catalog in parquet format.

        Defers import of parquet to minimize import overhead for all other models.
        """
        # parquet does not provide validation so validate first with asdf
        self.validate()

        global DTYPE_MAP
        import pyarrow as pa
        import pyarrow.parquet as pq

        if not DTYPE_MAP:
            DTYPE_MAP.update(
                {
                    "bool": pa.bool_(),
                    "uint8": pa.uint8(),
                    "uint16": pa.uint16(),
                    "uint32": pa.uint32(),
                    "uint64": pa.uint64(),
                    "int8": pa.int8(),
                    "int16": pa.int16(),
                    "int32": pa.int32(),
                    "int64": pa.int64(),
                    "float16": pa.float16(),
                    "float32": pa.float32(),
                    "float64": pa.float64(),
                }
            )

        with temporary_update_filename(self, Path(filepath).name), temporary_update_filedate(self, Time.now()):
            # Construct flat metadata dict
            flat_meta = self.to_flat_dict()
        # select only meta items
        flat_meta = {k: str(v) for (k, v) in flat_meta.items() if k.startswith("roman.meta")}
        # Extract table metadata
        source_cat = self.source_catalog
        scmeta = source_cat.meta
        # Wrap it as a DNode so it can be flattened
        dn_scmeta = stnode.DNode(scmeta)
        flat_scmeta = dn_scmeta.to_flat_dict(recursive=True)
        # Add prefix to flattened keys to indicate table metadata
        flat_scmeta = {"source_catalog." + k: str(v) for (k, v) in flat_scmeta.items()}
        # merge the two meta dicts
        flat_meta.update(flat_scmeta)
        # Turn numpy structured array into list of arrays
        keys = list(source_cat.columns.keys())
        arrs = [np.array(source_cat[key]) for key in keys]
        units = [str(source_cat[key].unit) for key in keys]
        dtypes = [DTYPE_MAP[np.array(source_cat[key]).dtype.name] for key in keys]
        fields = [
            pa.field(key, type=dtype, metadata={"unit": unit}) for (key, dtype, unit) in zip(keys, dtypes, units, strict=False)
        ]
        extra_astropy_metadata = astropy.table.meta.get_yaml_from_table(source_cat)
        flat_meta["table_meta_yaml"] = "\n".join(extra_astropy_metadata)
        schema = pa.schema(fields, metadata=flat_meta)
        table = pa.Table.from_arrays(arrs, schema=schema)
        pq.write_table(table, filepath, compression=None)


class _DataModel(DataModel):
    """
    Exists only to populate the __all__ for this file automatically
        This is something which is easily missed, but is important for the automatic
        documentation generation to work properly.
    """

    __slots__ = ()

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
    __slots__ = ()

    def __init__(self, init=None, **kwargs):
        super().__init__(init, **kwargs)

        if init is not None:
            self.meta.model_type = self.__class__.__name__


class MosaicModel(_RomanDataModel):
    __slots__ = ()
    _node_type = stnode.WfiMosaic  # type: ignore[attr-defined]


class ImageModel(_RomanDataModel):
    __slots__ = ()
    _node_type = stnode.WfiImage  # type: ignore[attr-defined]


class ScienceRawModel(_RomanDataModel):
    __slots__ = ()
    _node_type = stnode.WfiScienceRaw  # type: ignore[attr-defined]

    @classmethod
    def from_tvac_raw(cls, model):
        """Convert TVAC/FPS into ScienceRawModel

        romancal supports processing a selection of files which use an outdated
        schema. It supports these with a bespoke method that converts the files
        to the new format when they are read in dq_init. This conversion does
        not do a detailed mapping between all of the new and old metadata, but
        instead opportunistically looks for fields with common names and
        assigns them. Other metadata with non-matching names is simply copied
        in place. This allows processing to proceed and preserves the original
        metadata, but the resulting files have duplicates of many entries.

        Parameters
        ----------
        model : ScienceRawModel, TvacModel, FpsModel
          Model to convert from.

        Returns
        -------
        science_raw_model : ScienceRawModel
            The ScienceRawModel built from the input model.
            If the input was a ScienceRawModel, that model is simply returned.

        """
        ALLOWED_MODELS = (FpsModel, ScienceRawModel, TvacModel)

        if isinstance(model, cls):
            return model
        if not isinstance(model, ALLOWED_MODELS):
            raise ValueError(f"Input must be one of {ALLOWED_MODELS}")

        # Create base raw node with dummy values (for validation)
        if isinstance(model, (FpsModel | TvacModel)):
            raw = stnode.WfiScienceRaw.create_fake_data()
        else:
            raw = stnode.WfiScienceRaw.create_minimal()

        node_update(raw, model, extras=("meta.statistics",), extras_key="tvac")

        # check for exposure data_problem
        if isinstance(raw.meta.exposure.data_problem, bool):
            if raw.meta.exposure.data_problem:
                raw.meta.exposure.data_problem = "True"
            else:
                raw.meta.exposure.data_problem = None

        # Create model from node
        raw_model = ScienceRawModel(raw)
        return raw_model


class MsosStackModel(_RomanDataModel):
    __slots__ = ()
    _node_type = stnode.MsosStack  # type: ignore[attr-defined]


class RampModel(_RomanDataModel):
    __slots__ = ()
    _node_type = stnode.Ramp  # type: ignore[attr-defined]

    @classmethod
    def from_science_raw(cls, model):
        """Attempt to construct a RampModel from a DataModel

        If the model has a resultantdq attribute, this is copied into
        the RampModel.groupdq attribute.

        Otherwise, this conversion does not do a detailed mapping between all
        of the new and old metadata, but instead opportunistically looks for
        fields with common names and assigns them. Other metadata with
        non-matching names is simply copied in place. This allows processing to
        proceed and preserves the original metadata, but the resulting files
        have duplicates of many entries.

        Parameters
        ----------
        model : FpsModel, RampModel, ScienceRawModel, TvacModel
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
        ramp = stnode.Ramp.create_minimal()
        ramp.meta.cal_step = stnode.L2CalStep.create_minimal()
        ramp.meta.cal_logs = stnode.CalLogs()
        shape = model.data.shape
        ramp.pixeldq = np.zeros(shape[1:], dtype=np.uint32)
        ramp.groupdq = np.zeros(shape, dtype=np.uint8)
        ramp.data = model.data.astype(np.float32)
        ramp.err = np.zeros_like(ramp.data)
        ramp.amp33 = model.amp33.copy()

        # check if the input model has a resultantdq from SDF
        if hasattr(model, "resultantdq"):
            ramp.groupdq = model.resultantdq.copy()

        node_update(ramp, model, ignore=("resultantdq",))

        # check for exposure data_problem
        if isinstance(ramp.meta.exposure.data_problem, bool):
            if ramp.meta.exposure.data_problem:
                ramp.meta.exposure.data_problem = "True"
            else:
                ramp.meta.exposure.data_problem = None

        # Create model from node
        ramp_model = RampModel(ramp)
        return ramp_model


class RampFitOutputModel(_RomanDataModel):
    __slots__ = ()
    _node_type = stnode.RampFitOutput  # type: ignore[attr-defined]


class L1FaceGuidewindowModel(_RomanDataModel):
    __slots__ = ()
    _node_type = stnode.L1FaceGuidewindow  # type: ignore[attr-defined]


class GuidewindowModel(_RomanDataModel):
    __slots__ = ()
    _node_type = stnode.Guidewindow  # type: ignore[attr-defined]


class L1DetectorGuidewindowModel(_RomanDataModel):
    __slots__ = ()
    _node_type = stnode.L1DetectorGuidewindow  # type: ignore[attr-defined]


class FlatRefModel(_DataModel):
    __slots__ = ()
    _node_type = stnode.FlatRef  # type: ignore[attr-defined]


class AbvegaoffsetRefModel(_DataModel):
    __slots__ = ()
    _node_type = stnode.AbvegaoffsetRef  # type: ignore[attr-defined]


class ApcorrRefModel(_DataModel):
    __slots__ = ()
    _node_type = stnode.ApcorrRef  # type: ignore[attr-defined]


class DarkRefModel(_DataModel):
    __slots__ = ()
    _node_type = stnode.DarkRef  # type: ignore[attr-defined]


class DistortionRefModel(_DataModel):
    __slots__ = ()
    _node_type = stnode.DistortionRef  # type: ignore[attr-defined]


class EpsfRefModel(_DataModel):
    __slots__ = ()
    _node_type = stnode.EpsfRef  # type: ignore[attr-defined]


class GainRefModel(_DataModel):
    __slots__ = ()
    _node_type = stnode.GainRef  # type: ignore[attr-defined]


class IpcRefModel(_DataModel):
    __slots__ = ()
    _node_type = stnode.IpcRef  # type: ignore[attr-defined]


class LinearityRefModel(_DataModel):
    __slots__ = ()
    _node_type = stnode.LinearityRef  # type: ignore[attr-defined]

    def get_primary_array_name(self):
        """
        Returns the name "primary" array for this model, which
        controls the size of other arrays that are implicitly created.
        This is intended to be overridden in the subclasses if the
        primary array's name is not "data".
        """
        return "coeffs"


class InverselinearityRefModel(_DataModel):
    __slots__ = ()
    _node_type = stnode.InverselinearityRef  # type: ignore[attr-defined]

    def get_primary_array_name(self):
        """
        Returns the name "primary" array for this model, which
        controls the size of other arrays that are implicitly created.
        This is intended to be overridden in the subclasses if the
        primary array's name is not "data".
        """
        return "coeffs"


class MaskRefModel(_DataModel):
    __slots__ = ()
    _node_type = stnode.MaskRef  # type: ignore[attr-defined]

    def get_primary_array_name(self):
        """
        Returns the name "primary" array for this model, which
        controls the size of other arrays that are implicitly created.
        This is intended to be overridden in the subclasses if the
        primary array's name is not "data".
        """
        return "dq"


class MATableRefModel(_DataModel):
    __slots__ = ()
    _node_type = stnode.MatableRef  # type: ignore[attr-defined]


class PixelareaRefModel(_DataModel):
    __slots__ = ()
    _node_type = stnode.PixelareaRef  # type: ignore[attr-defined]


class ReadnoiseRefModel(_DataModel):
    __slots__ = ()
    _node_type = stnode.ReadnoiseRef  # type: ignore[attr-defined]


class SkycellsRefModel(_DataModel):
    __slots__ = ()
    _node_type = stnode.SkycellsRef  # type: ignore[attr-defined]


class SuperbiasRefModel(_DataModel):
    __slots__ = ()
    _node_type = stnode.SuperbiasRef  # type: ignore[attr-defined]


class SaturationRefModel(_DataModel):
    __slots__ = ()
    _node_type = stnode.SaturationRef  # type: ignore[attr-defined]


class WfiImgPhotomRefModel(_DataModel):
    __slots__ = ()
    _node_type = stnode.WfiImgPhotomRef  # type: ignore[attr-defined]


class RefpixRefModel(_DataModel):
    __slots__ = ()
    _node_type = stnode.RefpixRef  # type: ignore[attr-defined]


class FpsModel(_DataModel):
    __slots__ = ()
    _node_type = stnode.Fps  # type: ignore[attr-defined]


class TvacModel(_DataModel):
    __slots__ = ()
    _node_type = stnode.Tvac  # type: ignore[attr-defined]


class MosaicSourceCatalogModel(_RomanDataModel, _ParquetMixin, _SourceCatalogMixin):
    __slots__ = ()
    _node_type = stnode.MosaicSourceCatalog  # type: ignore[attr-defined]


class MultibandSourceCatalogModel(_RomanDataModel, _ParquetMixin, _SourceCatalogMixin):
    __slots__ = ()
    _node_type = stnode.MultibandSourceCatalog  # type: ignore[attr-defined]


class ForcedImageSourceCatalogModel(_RomanDataModel, _ParquetMixin, _SourceCatalogMixin):
    __slots__ = ()
    _node_type = stnode.ForcedImageSourceCatalog  # type: ignore[attr-defined]


class ForcedMosaicSourceCatalogModel(_RomanDataModel, _ParquetMixin, _SourceCatalogMixin):
    __slots__ = ()
    _node_type = stnode.ForcedMosaicSourceCatalog  # type: ignore[attr-defined]


class MosaicSegmentationMapModel(_RomanDataModel):
    __slots__ = ()
    _node_type = stnode.MosaicSegmentationMap  # type: ignore[attr-defined]


class ImageSourceCatalogModel(_RomanDataModel, _ParquetMixin, _SourceCatalogMixin):
    __slots__ = ()
    _node_type = stnode.ImageSourceCatalog  # type: ignore[attr-defined]


class SegmentationMapModel(_RomanDataModel):
    __slots__ = ()
    _node_type = stnode.SegmentationMap  # type: ignore[attr-defined]


class WfiWcsModel(_RomanDataModel):
    __slots__ = ()
    _node_type = stnode.WfiWcs  # type: ignore[attr-defined]

    @classmethod
    def from_model_with_wcs(cls, model, l1_border=4):
        """Extract the WCS information from an exposure model post-assign_wcs

        Construct a `WfiWcsModel` from any model that is used post-assign_wcs step
        in the ELP pipeline. The WCS information is extracted out of the input model.
        The wcs-related meta information is copied verbatim from the input model.

        However, the WCS object itself is placed into the attribute 'wcs_l2'. Furthermore, a
        modified GWCS, applicable to the Level 1 version of the input model, is created
        and stored in the attribute 'wcs_l1'.

        Parameters
        ----------
        model : ImageModel
            The input data model.

        l1_border : int
            The extra border to add for the L1 wcs.

        Returns
        -------
        wfiwcs_model : WfiWcsModel
            The WfiWcsModel built from the input model.

        """
        if not isinstance(model, ImageModel):
            raise ValueError("Input must be an ImageModel")

        # Retrieve the needed meta components
        wfi_wcs = cls()
        wfi_wcs.meta = {}
        schema = wfi_wcs.get_schema()
        for k in itertools.chain(*(ss["properties"].keys() for ss in schema["properties"]["meta"]["allOf"])):
            if k in model.meta:
                wfi_wcs.meta[k] = copy.deepcopy(model.meta[k])

        # Check that a WCS has been defined.
        if model.meta.wcs is None:
            log.info("Model has no WCS defined. Will not populate the WCS components.")
            return wfi_wcs

        # Assign the model WCS to the L2-specified wcs attribute
        wfi_wcs.wcs_l2 = copy.deepcopy(model.meta.wcs)

        # Create an L1 WCS that accounts for the extra border.
        l1_wcs = copy.deepcopy(model.meta.wcs)
        l1_shift = models.Shift(-l1_border) & models.Shift(-l1_border)
        l1_wcs.insert_transform("detector", l1_shift, after=True)
        bb = wfi_wcs["wcs_l2"].bounding_box
        if bb is not None:
            l1_wcs.bounding_box = ((bb[0][0], bb[0][1] + 2 * l1_border), (bb[1][0], bb[1][1] + 2 * l1_border))
        wfi_wcs.wcs_l1 = l1_wcs

        # Get alignment results, if available
        if hasattr(model.meta, "wcs_fit_results"):
            wfi_wcs.meta.wcs_fit_results = copy.deepcopy(model.meta["wcs_fit_results"])

        # That's all folks.
        return wfi_wcs
