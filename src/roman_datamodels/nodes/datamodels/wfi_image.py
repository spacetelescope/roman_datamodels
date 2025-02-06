import numpy as np
import numpy.typing as npt
from gwcs import WCS

from roman_datamodels.stnode import rad

from .meta import (
    CalLogs,
    Common,
    L2CalStep,
    OutlierDetection,
    Photometry,
    SkyBackground,
    SourceCatalog,
    Statistics,
    Wcsinfo,
)

__all__ = ["WfiImage", "WfiImage_Meta"]


class WfiImage_Meta(rad.ImpliedNodeMixin, Common):
    @classmethod
    def _asdf_implied_by(cls) -> type:
        return WfiImage

    @rad.field
    def background(self) -> SkyBackground:
        return SkyBackground()

    @rad.field
    def cal_logs(self) -> CalLogs:
        return CalLogs.default()

    @rad.field
    def cal_step(self) -> L2CalStep:
        return L2CalStep()

    @rad.field
    def outlier_detection(self) -> OutlierDetection:
        return OutlierDetection()

    @rad.field
    def photometry(self) -> Photometry:
        return Photometry()

    @rad.field
    def source_catalog(self) -> SourceCatalog:
        return SourceCatalog()

    @rad.field
    def statistics(self) -> Statistics:
        return Statistics()

    @rad.field
    def wcs(self) -> WCS | None:
        return rad.Wcs()

    @rad.field
    def wcsinfo(self) -> Wcsinfo:
        return Wcsinfo()


class WfiImage(rad.TaggedObjectNode, rad.ArrayFieldMixin):
    @classmethod
    def _asdf_tag_uris(cls) -> dict[str, str]:
        return {
            "asdf://stsci.edu/datamodels/roman/tags/wfi_image-1.0.0": "asdf://stsci.edu/datamodels/roman/schemas/wfi_image-1.0.0"
        }

    @property
    def _largest_array_shape_(self) -> tuple[int, ...] | None:
        """Override so that array_shape is the correct shape for construction"""
        if (shape := self.primary_array_shape) is None:
            return None

        if self._has_node("amp33"):
            n_groups: int = self.amp33.shape[0]
            return (n_groups, shape[0], shape[1])

        return None

    @property
    def default_array_shape(self) -> tuple[int, int, int]:
        return (8, 4088, 4088)

    @property
    def testing_array_shape(self) -> tuple[int, int, int]:
        return (8, 8, 8)

    @rad.field
    def meta(self) -> WfiImage_Meta:
        return WfiImage_Meta()

    @rad.field
    def data(self) -> npt.NDArray[np.float32]:
        return np.zeros(self.array_shape[1:], dtype=np.float32)

    @rad.field
    def dq(self) -> npt.NDArray[np.uint32]:
        return np.zeros(self.array_shape[1:], dtype=np.uint32)

    @rad.field
    def err(self) -> npt.NDArray[np.float32]:
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
    def amp33(self) -> npt.NDArray[np.uint16]:
        return np.zeros((self.array_shape[0], self.array_shape[1], 128), dtype=np.uint16)

    @rad.field
    def border_ref_pix_left(self) -> npt.NDArray[np.float32]:
        return np.zeros((self.array_shape[0], self.array_shape[1] + 8, 4), dtype=np.float32)

    @rad.field
    def border_ref_pix_right(self) -> npt.NDArray[np.float32]:
        return np.zeros((self.array_shape[0], self.array_shape[1] + 8, 4), dtype=np.float32)

    @rad.field
    def border_ref_pix_top(self) -> npt.NDArray[np.float32]:
        return np.zeros((self.array_shape[0], 4, self.array_shape[2] + 8), dtype=np.float32)

    @rad.field
    def border_ref_pix_bottom(self) -> npt.NDArray[np.float32]:
        return np.zeros((self.array_shape[0], 4, self.array_shape[2] + 8), dtype=np.float32)

    @rad.field
    def dq_border_ref_pix_left(self) -> npt.NDArray[np.uint32]:
        return np.zeros((self.array_shape[1] + 8, 4), dtype=np.uint32)

    @rad.field
    def dq_border_ref_pix_right(self) -> npt.NDArray[np.uint32]:
        return np.zeros((self.array_shape[1] + 8, 4), dtype=np.uint32)

    @rad.field
    def dq_border_ref_pix_top(self) -> npt.NDArray[np.uint32]:
        return np.zeros((4, self.array_shape[2] + 8), dtype=np.uint32)

    @rad.field
    def dq_border_ref_pix_bottom(self) -> npt.NDArray[np.uint32]:
        return np.zeros((4, self.array_shape[2] + 8), dtype=np.uint32)
