import numpy as np
import numpy.typing as npt

from roman_datamodels.stnode import rad

from .ref import RefCommonRef, RefTypeEntry

__all__ = ["MaskRef", "MaskRef_Meta"]


class MaskRef_Meta(rad.ImpliedNodeMixin, RefCommonRef):
    @classmethod
    def _asdf_implied_by(cls) -> type:
        return MaskRef

    @rad.field
    def reftype(self) -> RefTypeEntry:
        return RefTypeEntry.MASK


class MaskRef(rad.TaggedObjectNode, rad.ArrayFieldMixin):
    @classmethod
    def _asdf_tag_uris(cls) -> dict[str, str]:
        return {
            "asdf://stsci.edu/datamodels/roman/tags/reference_files/mask-1.0.0": "asdf://stsci.edu/datamodels/roman/schemas/reference_files/mask-1.0.0"
        }

    @property
    def primary_array_name(self) -> str:
        return "dq"

    @property
    def default_array_shape(self) -> tuple[int, int]:
        return (4096, 4096)

    @property
    def testing_array_shape(self) -> tuple[int, int]:
        return (8, 8)

    @rad.field
    def meta(self) -> MaskRef_Meta:
        return MaskRef_Meta()

    @rad.field
    def dq(self) -> npt.NDArray[np.uint32]:
        return np.zeros(self.array_shape, dtype=np.uint32)
