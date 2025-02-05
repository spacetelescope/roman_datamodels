import numpy as np
import numpy.typing as npt

from roman_datamodels.stnode import rad

from .ref import RefCommonRef, RefTypeEntry

__all__ = ["RefpixRef", "RefpixRef_Meta"]


class RefpixRef_Meta(rad.ImpliedNodeMixin, RefCommonRef):
    @classmethod
    def _asdf_implied_by(cls) -> type:
        return RefpixRef

    @rad.field
    def reftype(self) -> RefTypeEntry:
        return RefTypeEntry.REFPIX


class RefpixRef(rad.TaggedObjectNode, rad.ArrayFieldMixin):
    @classmethod
    def _asdf_tag_uris(cls) -> dict[str, str]:
        return {
            "asdf://stsci.edu/datamodels/roman/tags/reference_files/refpix-1.0.0": "asdf://stsci.edu/datamodels/roman/schemas/reference_files/refpix-1.0.0"
        }

    @property
    def primary_array_name(self) -> str:
        return "gamma"

    @property
    def default_array_shape(self) -> tuple[int, int]:
        return (32, 286721)

    @property
    def testing_array_shape(self) -> tuple[int, int]:
        return (32, 840)  # Chosen as the minimum size to do real testing

    @rad.field
    def meta(self) -> RefpixRef_Meta:
        return RefpixRef_Meta()

    @rad.field
    def gamma(self) -> npt.NDArray[np.complex128]:
        return np.zeros(self.array_shape, dtype=np.complex128)

    @rad.field
    def zeta(self) -> npt.NDArray[np.complex128]:
        return np.zeros(self.array_shape, dtype=np.complex128)

    @rad.field
    def alpha(self) -> npt.NDArray[np.complex128]:
        return np.zeros(self.array_shape, dtype=np.complex128)
