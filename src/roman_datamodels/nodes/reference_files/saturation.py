import numpy as np
import numpy.typing as npt

from roman_datamodels.stnode import rad

from .ref import RefCommonRef, RefTypeEntry

__all__ = ["SaturationRef", "SaturationRef_Meta"]


class SaturationRef_Meta(rad.ImpliedNodeMixin, RefCommonRef):
    @classmethod
    def _asdf_implied_by(cls) -> type:
        return SaturationRef

    @rad.field
    def reftype(self) -> RefTypeEntry:
        return RefTypeEntry.SATURATION


class SaturationRef(rad.TaggedObjectNode, rad.ArrayFieldMixin):
    @classmethod
    def _asdf_tag_uris(cls) -> dict[str, str]:
        return {
            "asdf://stsci.edu/datamodels/roman/tags/reference_files/saturation-1.0.0": "asdf://stsci.edu/datamodels/roman/schemas/reference_files/saturation-1.0.0"
        }

    @property
    def default_array_shape(self) -> tuple[int, int]:
        return (4096, 4096)

    @property
    def testing_array_shape(self) -> tuple[int, int]:
        return (8, 8)

    @rad.field
    def meta(self) -> SaturationRef_Meta:
        return SaturationRef_Meta()

    @rad.field
    def data(self) -> npt.NDArray[np.float32]:
        return np.zeros(self.array_shape, dtype=np.float32)

    @rad.field
    def dq(self) -> npt.NDArray[np.uint32]:
        return np.zeros(self.array_shape, dtype=np.uint32)
