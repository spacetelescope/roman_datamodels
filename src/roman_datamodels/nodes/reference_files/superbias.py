import numpy as np
import numpy.typing as npt

from roman_datamodels.stnode import rad

from .ref import RefCommonRef, RefTypeEntry

__all__ = ["SuperbiasRef", "SuperbiasRef_Meta"]


class SuperbiasRef_Meta(rad.ImpliedNodeMixin, RefCommonRef):
    @classmethod
    def _asdf_implied_by(cls) -> type:
        return SuperbiasRef

    @rad.field
    def reftype(self) -> RefTypeEntry:
        return RefTypeEntry.BIAS


class SuperbiasRef(rad.TaggedObjectNode, rad.ArrayFieldMixin):
    @classmethod
    def _asdf_tag_uris(cls) -> dict[str, str]:
        return {
            "asdf://stsci.edu/datamodels/roman/tags/reference_files/superbias-1.0.0": "asdf://stsci.edu/datamodels/roman/schemas/reference_files/superbias-1.0.0"
        }

    @property
    def default_array_shape(self) -> tuple[int, int]:
        return (4096, 4096)

    @property
    def testing_array_shape(self) -> tuple[int, int]:
        return (8, 8)

    @rad.field
    def meta(self) -> SuperbiasRef_Meta:
        return SuperbiasRef_Meta()

    @rad.field
    def data(self) -> npt.NDArray[np.float32]:
        return np.zeros(self.array_shape, dtype=np.float32)

    @rad.field
    def dq(self) -> npt.NDArray[np.uint32]:
        return np.zeros(self.array_shape, dtype=np.uint32)

    @rad.field
    def err(self) -> npt.NDArray[np.float32]:
        return np.zeros(self.array_shape, dtype=np.float32)
