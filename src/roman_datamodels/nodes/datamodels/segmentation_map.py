import numpy as np
import numpy.typing as npt

from roman_datamodels.stnode import rad

from .meta import (
    Basic,
    Program,
    Visit,
    WfiOpticalElement,
)

__all__ = ["SegmentationMap", "SegmentationMap_Meta"]


class SegmentationMap_Meta(rad.ImpliedNodeMixin, Basic):
    @classmethod
    def _asdf_implied_by(cls) -> type:
        return SegmentationMap

    @rad.field
    def optical_element(self) -> WfiOpticalElement:
        return WfiOpticalElement.F158

    @rad.field
    def program(self) -> Program:
        return Program()

    @rad.field
    def visit(self) -> Visit:
        return Visit()


class SegmentationMap(rad.TaggedObjectNode, rad.ArrayFieldMixin):
    @classmethod
    def _asdf_tag_uris(cls) -> dict[str, str]:
        return {
            "asdf://stsci.edu/datamodels/roman/tags/segmentation_map-1.0.0": "asdf://stsci.edu/datamodels/roman/schemas/segmentation_map-1.0.0"
        }

    @property
    def default_array_shape(self) -> tuple[int, int]:
        return (4096, 4096)

    @property
    def testing_array_shape(self) -> tuple[int, int]:
        return (8, 8)

    @rad.field
    def meta(self) -> SegmentationMap_Meta:
        return SegmentationMap_Meta()

    @rad.field
    def data(self) -> npt.NDArray[np.uint32]:
        return np.zeros(self.array_shape, dtype=np.uint32)
