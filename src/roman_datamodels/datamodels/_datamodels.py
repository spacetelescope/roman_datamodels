"""
This module provides all the specific datamodels used by the Roman pipeline.
    These models are what will be read and written by the pipeline to ASDF files.
    Note that we require each model to specify a node_type, which corresponds to
    the top-level STNode type that the datamodel wraps. This STNode type is derived
    from the schema manifest defined by RAD.
"""

from __future__ import annotations

import copy
import functools
import itertools
import logging
import pathlib
import warnings
from collections import abc
from typing import TYPE_CHECKING

import astropy.table.meta
import numpy as np
from astropy import time as _time
from astropy.modeling import models

from ._core import DataModel
from ._utils import _temporary_update_filedate, _temporary_update_filename, node_update

if TYPE_CHECKING:
    from os import PathLike
    from typing import Any, Self

    from astropy.table import Table

    _DataModel = DataModel
else:
    _DataModel = object

# NOTE: this module does not have the typical `__all__`` present like most of the other
#    modules in `roman_datamodels``. The presence of the `__all__` variable causes is
#    entirely to control what is imported by the wildcard `*` import. This style of
#    import is used by `sphinx.ext.autosummary` to determine what to document within a given
#    module. However, in this module's case we would have to list every single datamodel
#    in the `__all__` which would become tedious and error-prone. Therefore, we simply
#    omit the `__all__` variable and carefully control what we make publicly available
#    in the module's namespace via the use of `_` prefixes on private classes and avoiding
#    the import of items from other modules directly into this module's namespace and instead
#    importing them as the namespace from that module (e.g. `from astropy import time` and
#    using `time.Time` instead of `from astropy.time import Time` and using `Time` directly).
#    this prevents `sphinx.ext.autosummary` from documenting these items which can cause
#    documentation warnings and bloat.

DTYPE_MAP: dict[str, Any] = {}

# Define logging
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class _SourceCatalogMixin(_DataModel):
    from roman_datamodels._stnode import ImageSourceCatalogMixin as _Mixin

    __slots__ = ()

    def create_empty_catalog(self, aperture_radii: list[int] | None = None, filters: list[str] | None = None) -> Table:
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
            An empty but valid source catalog table.
        """
        radii = None if aperture_radii is None else [f"{i:02}" for i in aperture_radii]

        return self._instance._create_empty_catalog(radii, filters)

    @functools.wraps(_Mixin.get_column_definition)
    def get_column_definition(self, name):
        return self._instance.get_column_definition(name)


class _ParquetMixin(_DataModel):
    """Gives SourceCatalogModels the ability to save to parquet files."""

    __slots__ = ()

    def to_parquet(self, filepath: PathLike) -> None:
        """
        Save catalog in parquet format.

        Defers import of parquet to minimize import overhead for all other models.

        Parameters
        ----------
        filepath :
            The path to save the parquet file to.
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

        with _temporary_update_filename(self, pathlib.Path(filepath).name), _temporary_update_filedate(self, _time.Time.now()):
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
        defaults :
            If provided, defaults will be used in place of schema
        time :
            default time value


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
    @functools.wraps(DataModel.create_minimal.__func__)  # type: ignore[attr-defined]
    def create_minimal(cls, defaults=None, *, tag=None):
        return super().create_minimal(defaults=cls._creator_defaults(defaults), tag=tag)

    @classmethod
    @functools.wraps(DataModel.create_fake_data.__func__)  # type: ignore[attr-defined]
    def create_fake_data(cls, defaults=None, shape=None, *, tag=None):
        return super().create_fake_data(
            defaults=cls._creator_defaults(defaults, time=_time.Time("2020-01-01T00:00:00.0", format="isot", scale="utc")),
            shape=shape,
            tag=tag,
        )


class MosaicModel(_RomanDataModel):
    from roman_datamodels._stnode import WfiMosaic as _node_type

    __slots__ = ()


class ImageModel(_RomanDataModel):
    from roman_datamodels._stnode import WfiImage as _node_type

    __slots__ = ()


class ScienceRawModel(_RomanDataModel):
    from roman_datamodels._stnode import WfiScienceRaw as _node_type

    __slots__ = ()

    @classmethod
    def from_tvac_raw(cls, model: ScienceRawModel | TvacModel | FpsModel) -> Self:
        """
        Convert TVAC/FPS into ScienceRawModel

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
        model :
            Model to convert from.

        Returns
        -------
            The ScienceRawModel built from the input model.
            If the input was a ScienceRawModel, that model is simply returned.
        """
        warnings.warn("from_tvac_raw is deprecated. Use create_from_model instead", DeprecationWarning, stacklevel=2)
        ALLOWED_MODELS = (FpsModel, ScienceRawModel, TvacModel)

        if isinstance(model, cls):
            return model
        if not isinstance(model, ALLOWED_MODELS):
            raise ValueError(f"Input must be one of {ALLOWED_MODELS}")

        # Create base raw node with dummy values (for validation)
        if isinstance(model, (FpsModel | TvacModel)):
            # Limitation of MyPy with the functools.wraps
            raw_model: Self = cls.create_fake_data()  # type: ignore[call-arg]
        else:
            raw_model = cls.create_minimal()  # type: ignore[call-arg]

        node_update(raw_model._instance, model, extras=("meta.statistics",), extras_key="tvac", ignore=("meta.model_type",))

        # check for exposure data_problem
        if isinstance(raw_model.meta.exposure.data_problem, bool):
            if raw_model.meta.exposure.data_problem:
                raw_model.meta.exposure.data_problem = "True"
            else:
                raw_model.meta.exposure.data_problem = None

        return raw_model


class MsosStackModel(_RomanDataModel):
    from roman_datamodels._stnode import MsosStack as _node_type

    __slots__ = ()


class RampModel(_RomanDataModel):
    from roman_datamodels._stnode import Ramp as _node_type

    __slots__ = ()

    @classmethod
    def from_science_raw(cls, model: FpsModel | RampModel | ScienceRawModel | TvacModel) -> Self:
        """
        Attempt to construct a RampModel from a DataModel

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
            The RampModel built from the input model. If the input is already
            a RampModel, it is simply returned.

        """
        warnings.warn("from_science_raw is deprecated. Use create_from_model instead", DeprecationWarning, stacklevel=2)
        ALLOWED_MODELS = (FpsModel, RampModel, ScienceRawModel, TvacModel)

        if isinstance(model, cls):
            return model
        if not isinstance(model, ALLOWED_MODELS):
            raise ValueError(f"Input must be one of {ALLOWED_MODELS}")

        # Create base ramp node with dummy values (for validation)
        # Limitation of MyPy with the functools.wraps
        ramp_model: Self = cls.create_minimal()  # type: ignore[call-arg]

        # make cal_step
        ramp_model.meta.cal_step = {}
        for step_name in ramp_model.schema_info("required")["roman"]["meta"]["cal_step"]["required"].info:
            ramp_model.meta.cal_step[step_name] = "INCOMPLETE"

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
    from roman_datamodels._stnode import RampFitOutput as _node_type

    __slots__ = ()


class L1FaceGuidewindowModel(_RomanDataModel):
    from roman_datamodels._stnode import L1FaceGuidewindow as _node_type

    __slots__ = ()


class GuidewindowModel(_RomanDataModel):
    from roman_datamodels._stnode import Guidewindow as _node_type

    __slots__ = ()


class L1DetectorGuidewindowModel(_RomanDataModel):
    from roman_datamodels._stnode import L1DetectorGuidewindow as _node_type

    __slots__ = ()


class FlatRefModel(DataModel):
    from roman_datamodels._stnode import FlatRef as _node_type

    __slots__ = ()


class AbvegaoffsetRefModel(DataModel):
    from roman_datamodels._stnode import AbvegaoffsetRef as _node_type

    __slots__ = ()


class ApcorrRefModel(DataModel):
    from roman_datamodels._stnode import ApcorrRef as _node_type

    __slots__ = ()


class DarkRefModel(DataModel):
    from roman_datamodels._stnode import DarkRef as _node_type

    __slots__ = ()


class DetectorstatusRefModel(DataModel):
    from roman_datamodels._stnode import DetectorstatusRef as _node_type

    __slots__ = ()


class DarkdecaysignalRefModel(DataModel):
    from roman_datamodels._stnode import DarkdecaysignalRef as _node_type

    __slots__ = ()


class DistortionRefModel(DataModel):
    from roman_datamodels._stnode import DistortionRef as _node_type

    __slots__ = ()


class EpsfRefModel(DataModel):
    from roman_datamodels._stnode import EpsfRef as _node_type

    __slots__ = ()


class EtcRefModel(DataModel):
    from roman_datamodels._stnode import EtcRef as _node_type

    __slots__ = ()


class GainRefModel(DataModel):
    from roman_datamodels._stnode import GainRef as _node_type

    __slots__ = ()


class IpcRefModel(DataModel):
    from roman_datamodels._stnode import IpcRef as _node_type

    __slots__ = ()


class LinearityRefModel(DataModel):
    from roman_datamodels._stnode import LinearityRef as _node_type

    __slots__ = ()

    def get_primary_array_name(self):
        """
        Returns the name "primary" array for this model, which
        controls the size of other arrays that are implicitly created.
        This is intended to be overridden in the subclasses if the
        primary array's name is not "data".
        """
        return "coeffs"


class IntegralnonlinearityRefModel(DataModel):
    from roman_datamodels._stnode import IntegralnonlinearityRef as _node_type

    __slots__ = ()

    @functools.wraps(DataModel.get_primary_array_name)
    def get_primary_array_name(self):
        return "value"


class InverselinearityRefModel(DataModel):
    from roman_datamodels._stnode import InverselinearityRef as _node_type

    __slots__ = ()

    @functools.wraps(DataModel.get_primary_array_name)
    def get_primary_array_name(self):
        return "coeffs"


class MaskRefModel(DataModel):
    from roman_datamodels._stnode import MaskRef as _node_type

    __slots__ = ()

    @functools.wraps(DataModel.get_primary_array_name)
    def get_primary_array_name(self):
        return "dq"


class MATableRefModel(DataModel):
    from roman_datamodels._stnode import MatableRef as _node_type

    __slots__ = ()


class PixelareaRefModel(DataModel):
    from roman_datamodels._stnode import PixelareaRef as _node_type

    __slots__ = ()


class ReadnoiseRefModel(DataModel):
    from roman_datamodels._stnode import ReadnoiseRef as _node_type

    __slots__ = ()


class SkycellsRefModel(DataModel):
    from roman_datamodels._stnode import SkycellsRef as _node_type

    __slots__ = ()

    @functools.wraps(DataModel.to_asdf)
    def to_asdf(self, *args, **kwargs):
        # Set all SkycellRefModel arrays to internal so test
        # files with unrealistically small arrays don't get inlined
        # triggering: https://github.com/spacetelescope/rad/issues/887
        kwargs.pop("all_array_storage")
        return super().to_asdf(*args, all_array_storage="internal", **kwargs)


class SuperbiasRefModel(DataModel):
    from roman_datamodels._stnode import SuperbiasRef as _node_type

    __slots__ = ()


class SaturationRefModel(DataModel):
    from roman_datamodels._stnode import SaturationRef as _node_type

    __slots__ = ()


class WfiImgPhotomRefModel(DataModel):
    from roman_datamodels._stnode import WfiImgPhotomRef as _node_type

    __slots__ = ()


class RefpixRefModel(DataModel):
    from roman_datamodels._stnode import RefpixRef as _node_type

    __slots__ = ()


class FpsModel(DataModel):
    from roman_datamodels._stnode import Fps as _node_type

    __slots__ = ()


class TvacModel(DataModel):
    from roman_datamodels._stnode import Tvac as _node_type

    __slots__ = ()


class MosaicSourceCatalogModel(_RomanDataModel, _ParquetMixin, _SourceCatalogMixin):
    from roman_datamodels._stnode import MosaicSourceCatalog as _node_type

    __slots__ = ()


class MultibandSourceCatalogModel(_RomanDataModel, _ParquetMixin, _SourceCatalogMixin):
    from roman_datamodels._stnode import MultibandSourceCatalog as _node_type

    __slots__ = ()


class ForcedImageSourceCatalogModel(_RomanDataModel, _ParquetMixin, _SourceCatalogMixin):
    from roman_datamodels._stnode import ForcedImageSourceCatalog as _node_type

    __slots__ = ()


class ForcedMosaicSourceCatalogModel(_RomanDataModel, _ParquetMixin, _SourceCatalogMixin):
    from roman_datamodels._stnode import ForcedMosaicSourceCatalog as _node_type

    __slots__ = ()


class MosaicSegmentationMapModel(_RomanDataModel):
    from roman_datamodels._stnode import MosaicSegmentationMap as _node_type

    __slots__ = ()


class MultibandSegmentationMapModel(_RomanDataModel):
    from roman_datamodels._stnode import MultibandSegmentationMap as _node_type

    __slots__ = ()


class ImageSourceCatalogModel(_RomanDataModel, _ParquetMixin, _SourceCatalogMixin):
    from roman_datamodels._stnode import ImageSourceCatalog as _node_type

    __slots__ = ()


class SegmentationMapModel(_RomanDataModel):
    from roman_datamodels._stnode import SegmentationMap as _node_type

    __slots__ = ()


class WfiWcsModel(_RomanDataModel):
    from roman_datamodels._stnode import WfiWcs as _node_type

    __slots__ = ()

    @classmethod
    def from_model_with_wcs(cls, model: ImageModel, l1_border: int = 4) -> Self:
        """
        Extract the WCS information from an exposure

        Construct a `WfiWcsModel` from any model that is used post-assign_wcs step
        in the ELP pipeline. The WCS information is extracted out of the input model.
        The wcs-related meta information is copied verbatim from the input model.

        However, the WCS object itself is placed into the attribute 'wcs_l2'. Furthermore, a
        modified GWCS, applicable to the Level 1 version of the input model, is created
        and stored in the attribute 'wcs_l1'.

        Parameters
        ----------
        model :
            The input data model.

        l1_border :
            The extra border to add for the L1 wcs.

        Returns
        -------
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
