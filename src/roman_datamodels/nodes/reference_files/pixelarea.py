import numpy as np
import numpy.typing as npt

from roman_datamodels.stnode import rad

from .ref import RefCommonRefOpticalElementRef, RefTypeEntry

__all__ = ["PixelareaRef", "PixelareaRef_Meta", "PixelareaRef_Meta_Photometry"]


class PixelareaRef_Meta_Photometry(rad.ImpliedNodeMixin, rad.ObjectNode):
    @classmethod
    def _asdf_implied_by(cls) -> type:
        return PixelareaRef_Meta

    @rad.field
    def pixelarea_steradians(self) -> float | None:
        return rad.NONUM

    @rad.field
    def pixelarea_arcsecsq(self) -> float | None:
        return rad.NONUM


class PixelareaRef_Meta(rad.ImpliedNodeMixin, RefCommonRefOpticalElementRef):
    @classmethod
    def _asdf_implied_by(cls) -> type:
        return PixelareaRef

    @rad.field
    def reftype(self) -> RefTypeEntry:
        return RefTypeEntry.AREA

    @rad.field
    def photometry(self) -> PixelareaRef_Meta_Photometry:
        return PixelareaRef_Meta_Photometry()


class PixelareaRef(rad.TaggedObjectNode, rad.ArrayFieldMixin):
    @classmethod
    def _asdf_tag_uris(cls) -> dict[str, str]:
        return {
            "asdf://stsci.edu/datamodels/roman/tags/reference_files/pixelarea-1.0.0": "asdf://stsci.edu/datamodels/roman/schemas/reference_files/pixelarea-1.0.0"
        }

    @property
    def default_array_shape(self) -> tuple[int, int]:
        return (4096, 4096)

    @property
    def testing_array_shape(self) -> tuple[int, int]:
        return (8, 8)

    @rad.field
    def meta(self) -> PixelareaRef_Meta:
        return PixelareaRef_Meta()

    @rad.field
    def data(self) -> npt.NDArray[np.float32]:
        return np.zeros(self.array_shape, dtype=np.float32)
