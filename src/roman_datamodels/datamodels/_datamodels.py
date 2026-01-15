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
import pathlib
from collections import abc
from typing import TYPE_CHECKING

import astropy.table.meta
import numpy as np
from astropy import time as _time
from astropy.modeling import models

from ._core import DataModel
from ._utils import node_update, temporary_update_filedate, temporary_update_filename

if TYPE_CHECKING:
    from typing import Any

# NOTE: this module does not have the typical `__all__`` present like most of the other
#    modules in `roman_datamodels``. The presence of the `__all__` variable causes is
#    entirely to control what is imported by the wildcard `*` import. This style of
#    import is used by `spiinx-automodapi` to determine what to document within a given
#    module. However, in this module's case we would have to list every single datamodel
#    in the `__all__` which would become tedious and error-prone. Therefore, we simply
#    omit the `__all__` variable and carefully control what we make publicly available
#    in the module's namespace via the use of `_` prefixes on private classes and avoiding
#    the import of items from other modules directly into this module's namespace and instead
#    importing them as the namespace from that module (e.g. `from astropy import time` and
#    using `time.Time` instead of `from astropy.time import Time` and using `Time` directly).
#    this prevents `spinx-automodapi` from documenting these items which can cause documentation
#    warnings and bloat.

DTYPE_MAP: dict[str, Any] = {}

# Define logging
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class _SourceCatalogMixin:
    from roman_datamodels._stnode import ImageSourceCatalogMixin

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

    @functools.wraps(ImageSourceCatalogMixin.get_column_definition)
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
        from roman_datamodels._stnode import DNode

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

        with temporary_update_filename(self, pathlib.Path(filepath).name), temporary_update_filedate(self, _time.Time.now()):
            # Construct flat metadata dict
            flat_meta = self.to_flat_dict()
        # select only meta items
        flat_meta = {k: str(v) for (k, v) in flat_meta.items() if k.startswith("roman.meta")}
        # Extract table metadata
        source_cat = self.source_catalog
        scmeta = source_cat.meta
        # Wrap it as a DNode so it can be flattened
        dn_scmeta = DNode(scmeta)
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


class _RomanDataModel(DataModel):
    __slots__ = ()

    def __init__(self, init=None, **kwargs):
        super().__init__(init, **kwargs)

        if init is not None:
            self.meta.model_type = type(self.get("meta", {}).get("model_type", ""))(self.__class__.__name__)

    @classmethod
    def _creator_defaults(
        cls, defaults: abc.MutableMapping[str, Any] | None = None, *, time: _time.Time | None = None
    ) -> abc.MutableMapping[str, Any]:
        """
        The default values for the create constructors, `create_minimal` and `create_fake_data`.

        Parameters
        ----------
        defaults : None or dict
            If provided, defaults will be used in place of schema
        time: default time value


        Returns
        -------
        dict
            The default values to use when creating a new model. This will include
            some values that we want to always set to a specific value.
        """

        def merge_dicts(dict1: abc.MutableMapping[str, Any], dict2: abc.MutableMapping[str, Any]) -> abc.MutableMapping[str, Any]:
            for key in dict2:
                if key in dict1:
                    dict1_is_mapping = isinstance(dict1[key], abc.MutableMapping)
                    dict2_is_mapping = isinstance(dict2[key], abc.MutableMapping)

                    if dict1_is_mapping and dict2_is_mapping:
                        dict1[key] = merge_dicts(dict1[key], dict2[key])

                    elif dict1_is_mapping ^ dict2_is_mapping:
                        raise ValueError("Cannot merge mapping with non-mapping")

                else:
                    dict1[key] = dict2[key]

            return dict1

        return merge_dicts(
            # deepcopy to avoid modifying input
            {} if defaults is None else copy.deepcopy(dict(defaults)),
            {
                "meta": {
                    "calibration_software_name": "RomanCAL",
                    "file_date": time or _time.Time.now(),
                    "origin": "STSCI/SOC",
                }
            },
        )

    @classmethod
    def create_minimal(cls, defaults=None, *, tag=None):
        """
        Class method that constructs an "minimal" model.

        The "minimal" model will contain schema-required attributes
        where a default value can be determined:

            * node class defining a default value
            * defined in the schema (for example single item enums)
            * empty container classes (for example a "meta" dict)
            * required items with a corresponding provided default

        Parameters
        ----------
        defaults : None or dict
            If provided, defaults will be used in place of schema
            defined values for required attributes.

        Returns
        -------
        DataModel
            "Empty" model with optional defaults. This will often
            be incomplete (invalid) as not all required attributes
            can be guessed.
        """
        return super().create_minimal(defaults=cls._creator_defaults(defaults), tag=tag)

    @classmethod
    def create_fake_data(cls, defaults=None, shape=None, *, tag=None):
        """
        Class method that constructs a model filled with fake data.

        Similar to `DataModel.create_minimal` this only creates
        required attributes.

        Fake arrays will have a number of dimensions matching
        the schema requirements. If shape is provided only the
        dimensions matching the schema requirements will be used.
        For example if a 3 dimensional shape is provided but a fake
        array only requires 2 dimensions only the first 2 values
        from shape will be used.

        Parameters
        ----------
        defaults : None or dict
            If provided, defaults will be used in place of schema
            defined or fake values for required attributes.

        shape : None or tuple of int
            When provided use this shape to determine the
            shape used to construct fake arrays.

        Returns
        -------
        DataModel
            A valid model with fake data.
        """
        return super().create_fake_data(
            defaults=cls._creator_defaults(defaults, time=_time.Time("2020-01-01T00:00:00.0", format="isot", scale="utc")),
            shape=shape,
            tag=tag,
        )


class MosaicModel(_RomanDataModel):
    from roman_datamodels._stnode import WfiMosaic

    __slots__ = ()
    _node_type = WfiMosaic


class ImageModel(_RomanDataModel):
    from roman_datamodels._stnode import WfiImage

    __slots__ = ()
    _node_type = WfiImage


class ScienceRawModel(_RomanDataModel):
    from roman_datamodels._stnode import WfiScienceRaw

    __slots__ = ()
    _node_type = WfiScienceRaw

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
            raw_model = cls.create_fake_data()
        else:
            raw_model = cls.create_minimal()

        node_update(raw_model._instance, model, extras=("meta.statistics",), extras_key="tvac", ignore=("meta.model_type",))

        # check for exposure data_problem
        if isinstance(raw_model.meta.exposure.data_problem, bool):
            if raw_model.meta.exposure.data_problem:
                raw_model.meta.exposure.data_problem = "True"
            else:
                raw_model.meta.exposure.data_problem = None

        return raw_model


class MsosStackModel(_RomanDataModel):
    from roman_datamodels._stnode import MsosStack

    __slots__ = ()
    _node_type = MsosStack


class RampModel(_RomanDataModel):
    from roman_datamodels._stnode import Ramp

    __slots__ = ()
    _node_type = Ramp

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
        ramp_model = cls.create_fake_data()

        shape = model.data.shape
        ramp_model.pixeldq = np.zeros(shape[1:], dtype=np.uint32)
        ramp_model.groupdq = np.zeros(shape, dtype=np.uint8)
        ramp_model.data = model.data.astype(np.float32)
        ramp_model.amp33 = model.amp33.copy()

        # check if the input model has a resultantdq from SDF
        if hasattr(model, "resultantdq"):
            ramp_model.groupdq = model.resultantdq.copy()

        node_update(ramp_model._instance, model, ignore=("resultantdq", "meta.model_type"))

        # check for exposure data_problem
        if isinstance(ramp_model.meta.exposure.data_problem, bool):
            if ramp_model.meta.exposure.data_problem:
                ramp_model.meta.exposure.data_problem = "True"
            else:
                ramp_model.meta.exposure.data_problem = None

        return ramp_model


class RampFitOutputModel(_RomanDataModel):
    from roman_datamodels._stnode import RampFitOutput

    __slots__ = ()
    _node_type = RampFitOutput


class L1FaceGuidewindowModel(_RomanDataModel):
    from roman_datamodels._stnode import L1FaceGuidewindow

    __slots__ = ()
    _node_type = L1FaceGuidewindow


class GuidewindowModel(_RomanDataModel):
    from roman_datamodels._stnode import Guidewindow

    __slots__ = ()
    _node_type = Guidewindow


class L1DetectorGuidewindowModel(_RomanDataModel):
    from roman_datamodels._stnode import L1DetectorGuidewindow

    __slots__ = ()
    _node_type = L1DetectorGuidewindow


class FlatRefModel(DataModel):
    from roman_datamodels._stnode import FlatRef

    __slots__ = ()
    _node_type = FlatRef


class AbvegaoffsetRefModel(DataModel):
    from roman_datamodels._stnode import AbvegaoffsetRef

    __slots__ = ()
    _node_type = AbvegaoffsetRef


class ApcorrRefModel(DataModel):
    from roman_datamodels._stnode import ApcorrRef

    __slots__ = ()
    _node_type = ApcorrRef


class DarkRefModel(DataModel):
    from roman_datamodels._stnode import DarkRef

    __slots__ = ()
    _node_type = DarkRef


class DetectorstatusRefModel(DataModel):
    from roman_datamodels._stnode import DetectorstatusRef

    __slots__ = ()
    _node_type = DetectorstatusRef


class DarkdecaysignalRefModel(DataModel):
    from roman_datamodels._stnode import DarkdecaysignalRef

    __slots__ = ()
    _node_type = DarkdecaysignalRef


class DistortionRefModel(DataModel):
    from roman_datamodels._stnode import DistortionRef

    __slots__ = ()
    _node_type = DistortionRef


class EpsfRefModel(DataModel):
    from roman_datamodels._stnode import EpsfRef

    __slots__ = ()
    _node_type = EpsfRef


class GainRefModel(DataModel):
    from roman_datamodels._stnode import GainRef

    __slots__ = ()
    _node_type = GainRef


class IpcRefModel(DataModel):
    from roman_datamodels._stnode import IpcRef

    __slots__ = ()
    _node_type = IpcRef


class LinearityRefModel(DataModel):
    from roman_datamodels._stnode import LinearityRef

    __slots__ = ()
    _node_type = LinearityRef

    def get_primary_array_name(self):
        """
        Returns the name "primary" array for this model, which
        controls the size of other arrays that are implicitly created.
        This is intended to be overridden in the subclasses if the
        primary array's name is not "data".
        """
        return "coeffs"


class IntegralnonlinearityRefModel(DataModel):
    from roman_datamodels._stnode import IntegralnonlinearityRef

    __slots__ = ()
    _node_type = IntegralnonlinearityRef

    def get_primary_array_name(self):
        """
        Returns the name "primary" array for this model, which
        controls the size of other arrays that are implicitly created.
        This is intended to be overridden in the subclasses if the
        primary array's name is not "data".
        """
        return "value"


class InverselinearityRefModel(DataModel):
    from roman_datamodels._stnode import InverselinearityRef

    __slots__ = ()
    _node_type = InverselinearityRef

    def get_primary_array_name(self):
        """
        Returns the name "primary" array for this model, which
        controls the size of other arrays that are implicitly created.
        This is intended to be overridden in the subclasses if the
        primary array's name is not "data".
        """
        return "coeffs"


class MaskRefModel(DataModel):
    from roman_datamodels._stnode import MaskRef

    __slots__ = ()
    _node_type = MaskRef

    def get_primary_array_name(self):
        """
        Returns the name "primary" array for this model, which
        controls the size of other arrays that are implicitly created.
        This is intended to be overridden in the subclasses if the
        primary array's name is not "data".
        """
        return "dq"


class MATableRefModel(DataModel):
    from roman_datamodels._stnode import MatableRef

    __slots__ = ()
    _node_type = MatableRef


class PixelareaRefModel(DataModel):
    from roman_datamodels._stnode import PixelareaRef

    __slots__ = ()
    _node_type = PixelareaRef


class ReadnoiseRefModel(DataModel):
    from roman_datamodels._stnode import ReadnoiseRef

    __slots__ = ()
    _node_type = ReadnoiseRef


class SkycellsRefModel(DataModel):
    from roman_datamodels._stnode import SkycellsRef

    __slots__ = ()
    _node_type = SkycellsRef


class SuperbiasRefModel(DataModel):
    from roman_datamodels._stnode import SuperbiasRef

    __slots__ = ()
    _node_type = SuperbiasRef


class SaturationRefModel(DataModel):
    from roman_datamodels._stnode import SaturationRef

    __slots__ = ()
    _node_type = SaturationRef


class WfiImgPhotomRefModel(DataModel):
    from roman_datamodels._stnode import WfiImgPhotomRef

    __slots__ = ()
    _node_type = WfiImgPhotomRef


class RefpixRefModel(DataModel):
    from roman_datamodels._stnode import RefpixRef

    __slots__ = ()
    _node_type = RefpixRef


class FpsModel(DataModel):
    from roman_datamodels._stnode import Fps

    __slots__ = ()
    _node_type = Fps


class TvacModel(DataModel):
    from roman_datamodels._stnode import Tvac

    __slots__ = ()
    _node_type = Tvac


class MosaicSourceCatalogModel(_RomanDataModel, _ParquetMixin, _SourceCatalogMixin):
    from roman_datamodels._stnode import MosaicSourceCatalog

    __slots__ = ()
    _node_type = MosaicSourceCatalog


class MultibandSourceCatalogModel(_RomanDataModel, _ParquetMixin, _SourceCatalogMixin):
    from roman_datamodels._stnode import MultibandSourceCatalog

    __slots__ = ()
    _node_type = MultibandSourceCatalog


class ForcedImageSourceCatalogModel(_RomanDataModel, _ParquetMixin, _SourceCatalogMixin):
    from roman_datamodels._stnode import ForcedImageSourceCatalog

    __slots__ = ()
    _node_type = ForcedImageSourceCatalog


class ForcedMosaicSourceCatalogModel(_RomanDataModel, _ParquetMixin, _SourceCatalogMixin):
    from roman_datamodels._stnode import ForcedMosaicSourceCatalog

    __slots__ = ()
    _node_type = ForcedMosaicSourceCatalog


class MosaicSegmentationMapModel(_RomanDataModel):
    from roman_datamodels._stnode import MosaicSegmentationMap

    __slots__ = ()
    _node_type = MosaicSegmentationMap


class MultibandSegmentationMapModel(_RomanDataModel):
    from roman_datamodels._stnode import MultibandSegmentationMap

    __slots__ = ()
    _node_type = MultibandSegmentationMap


class ImageSourceCatalogModel(_RomanDataModel, _ParquetMixin, _SourceCatalogMixin):
    from roman_datamodels._stnode import ImageSourceCatalog

    __slots__ = ()
    _node_type = ImageSourceCatalog


class SegmentationMapModel(_RomanDataModel):
    from roman_datamodels._stnode import SegmentationMap

    __slots__ = ()
    _node_type = SegmentationMap


class WfiWcsModel(_RomanDataModel):
    from roman_datamodels._stnode import WfiWcs

    __slots__ = ()
    _node_type = WfiWcs

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
