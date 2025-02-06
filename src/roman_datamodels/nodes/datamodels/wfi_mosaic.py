import numpy as np
import numpy.typing as npt
from gwcs import WCS

from roman_datamodels.stnode import rad

from .meta import (
    Basic,
    CalLogs,
    Coordinates,
    IndividualImageMeta,
    L3CalStep,
    MosaicAssociations,
    MosaicBasic,
    MosaicWcsinfo,
    Photometry,
    Program,
    RefFile,
    Resample,
)

__all__ = ["WfiMosaic", "WfiMosaic_Meta"]


class WfiMosaic_Meta(rad.ImpliedNodeMixin, Basic):
    @classmethod
    def _asdf_implied_by(cls) -> type:
        return WfiMosaic

    @rad.field
    def asn(self) -> MosaicAssociations:
        return MosaicAssociations()

    @rad.field
    def basic(self) -> MosaicBasic:
        return MosaicBasic()

    @rad.field
    def cal_step(self) -> L3CalStep:
        return L3CalStep()

    @rad.field
    def coordinates(self) -> Coordinates:
        return Coordinates()

    @rad.field
    def individual_image_meta(self) -> IndividualImageMeta:
        return IndividualImageMeta()

    @rad.field
    def photometry(self) -> Photometry:
        return Photometry()

    @rad.field
    def program(self) -> Program:
        return Program()

    @rad.field
    def ref_file(self) -> RefFile:
        return RefFile()

    @rad.field
    def resample(self) -> Resample:
        return Resample()

    @rad.field
    def wcs(self) -> WCS | None:
        return rad.Wcs()

    @rad.field
    def wcsinfo(self) -> MosaicWcsinfo:
        return MosaicWcsinfo()


class WfiMosaic(rad.TaggedObjectNode, rad.ArrayFieldMixin):
    @classmethod
    def _asdf_tag_uris(cls) -> dict[str, str]:
        return {
            "asdf://stsci.edu/datamodels/roman/tags/wfi_mosaic-1.0.0": "asdf://stsci.edu/datamodels/roman/schemas/wfi_mosaic-1.0.0"
        }

    @property
    def default_array_shape(self) -> tuple[int, int, int]:
        return (2, 4088, 4088)

    @property
    def testing_array_shape(self) -> tuple[int, int, int]:
        return (2, 8, 8)

    @property
    def _largest_array_shape_(self) -> tuple[int, ...] | None:
        """Override so that array_shape is the correct shape for construction"""
        if (shape := self.primary_array_shape) is None:
            return None

        if self._has_node("context"):
            n_images: int = self.context.shape[0]
            return (n_images, shape[0], shape[1])

        return None

    @rad.field
    def meta(self) -> WfiMosaic_Meta:
        return WfiMosaic_Meta()

    @rad.field
    def data(self) -> npt.NDArray[np.float32]:
        return np.zeros(self.array_shape[1:], dtype=np.float32)

    @rad.field
    def err(self) -> npt.NDArray[np.float32]:
        return np.zeros(self.array_shape[1:], dtype=np.float32)

    @rad.field
    def context(self) -> npt.NDArray[np.uint32]:
        return np.zeros(self.array_shape, dtype=np.uint32)

    @rad.field
    def weight(self) -> npt.NDArray[np.float32]:
        return np.zeros(self.array_shape[1:], dtype=np.float32)

    @rad.field
    def var_poisson(self) -> npt.NDArray[np.float32]:
        return np.zeros(self.array_shape[1:], dtype=np.float32)

    @rad.field
    def var_rnoise(self) -> npt.NDArray[np.float32]:
        return np.zeros(self.array_shape[1:], dtype=np.float32)

    @rad.field
    def var_flat(self) -> npt.NDArray[np.float32]:
        return np.zeros(self.array_shape[1:], dtype=np.float32)

    @rad.field
    def cal_logs(self) -> CalLogs:
        return CalLogs.default()
