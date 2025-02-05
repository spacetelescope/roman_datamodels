import numpy as np
import numpy.typing as npt

from roman_datamodels.stnode import rad

from .ref import (
    RefCommonRefOpticalElementRef,
    RefExposureTypeRef,
    RefTypeEntry,
)
from .ref.ref_exposure_type import RefExposureTypeRef_Exposure

__all__ = ["DarkRef", "DarkRef_Meta", "DarkRef_Meta_Exposure"]


class DarkRef_Meta_Exposure(RefExposureTypeRef_Exposure, rad.ImpliedNodeMixin):
    """
    This class is the result of a very weird mixture similar to the ref_mixes but only
    applies to the dark schema.
    """

    @classmethod
    def _asdf_implied_by(cls) -> type:
        return DarkRef_Meta

    @classmethod
    def _asdf_required(cls) -> set[str]:
        return {
            *super()._asdf_required(),
            *RefExposureTypeRef_Exposure._asdf_required(),
        }

    @property
    def schema_required(self) -> tuple[str, ...]:
        return tuple(self.asdf_required)

    @rad.field
    def ma_table_name(self) -> str:
        return rad.NOSTR

    @rad.field
    def ma_table_number(self) -> int:
        return rad.NOINT


class DarkRef_Meta(rad.ImpliedNodeMixin, RefCommonRefOpticalElementRef, RefExposureTypeRef):  # type: ignore[misc]
    @classmethod
    def _asdf_implied_by(cls) -> type:
        return DarkRef

    @classmethod
    def _asdf_required(cls) -> set[str]:
        return {
            *super()._asdf_required(),
            *RefCommonRefOpticalElementRef._asdf_required(),
            *RefExposureTypeRef._asdf_required(),
        }

    @rad.field
    def reftype(self) -> RefTypeEntry:
        return RefTypeEntry.DARK

    @rad.field
    def exposure(self) -> DarkRef_Meta_Exposure:  # type: ignore[override]
        return DarkRef_Meta_Exposure()


class DarkRef(rad.TaggedObjectNode, rad.ArrayFieldMixin):
    @classmethod
    def _asdf_tag_uris(cls) -> dict[str, str]:
        return {
            "asdf://stsci.edu/datamodels/roman/tags/reference_files/dark-1.0.0": "asdf://stsci.edu/datamodels/roman/schemas/reference_files/dark-1.0.0"
        }

    @property
    def default_array_shape(self) -> tuple[int, int, int]:
        return (2, 4096, 4096)

    @property
    def testing_array_shape(self) -> tuple[int, int, int]:
        return (2, 8, 8)

    @rad.field
    def meta(self) -> DarkRef_Meta:
        return DarkRef_Meta()

    @rad.field
    def data(self) -> npt.NDArray[np.float32]:
        return np.zeros(self.array_shape, dtype=np.float32)

    @rad.field
    def dq(self) -> npt.NDArray[np.uint32]:
        return np.zeros(self.array_shape[1:], dtype=np.uint32)

    @rad.field
    def dark_slope(self) -> npt.NDArray[np.float32]:
        return np.zeros(self.array_shape[1:], dtype=np.float32)

    @rad.field
    def dark_slope_error(self) -> npt.NDArray[np.float32]:
        return np.zeros(self.array_shape[1:], dtype=np.float32)
