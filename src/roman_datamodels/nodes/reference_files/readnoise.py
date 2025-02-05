import numpy as np
import numpy.typing as npt

from roman_datamodels.stnode import rad

from .ref import RefCommonRef, RefExposureTypeRef, RefTypeEntry

__all__ = ["ReadnoiseRef", "ReadnoiseRef_Meta"]


class ReadnoiseRef_Meta(rad.ImpliedNodeMixin, RefCommonRef, RefExposureTypeRef):
    @classmethod
    def _asdf_implied_by(cls) -> type:
        return ReadnoiseRef

    @rad.field
    def reftype(self) -> RefTypeEntry:
        return RefTypeEntry.READNOISE


class ReadnoiseRef(rad.TaggedObjectNode, rad.ArrayFieldMixin):
    @classmethod
    def _asdf_tag_uris(cls) -> dict[str, str]:
        return {
            "asdf://stsci.edu/datamodels/roman/tags/reference_files/readnoise-1.0.0": "asdf://stsci.edu/datamodels/roman/schemas/reference_files/readnoise-1.0.0"
        }

    @property
    def default_array_shape(self) -> tuple[int, int]:
        return (4096, 4096)

    @property
    def testing_array_shape(self) -> tuple[int, int]:
        return (8, 8)

    @rad.field
    def meta(self) -> ReadnoiseRef_Meta:
        return ReadnoiseRef_Meta()

    @rad.field
    def data(self) -> npt.NDArray[np.float32]:
        return np.zeros(self.array_shape, dtype=np.float32)
