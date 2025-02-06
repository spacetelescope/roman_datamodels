import numpy as np
import numpy.typing as npt

from roman_datamodels.stnode import rad

from .meta import (
    Basic,
    MosaicBasic,
    Program,
)

__all__ = ["MosaicSegmentationMap", "MosaicSegmentationMap_Meta"]


class MosaicSegmentationMap_Meta(rad.ImpliedNodeMixin, Basic):
    @classmethod
    def _asdf_implied_by(cls) -> type:
        return MosaicSegmentationMap

    @rad.field
    def basic(self) -> MosaicBasic:
        return MosaicBasic()

    @rad.field
    def program(self) -> Program:
        return Program()


class MosaicSegmentationMap(rad.TaggedObjectNode, rad.ArrayFieldMixin):
    @classmethod
    def _asdf_tag_uris(cls) -> dict[str, str]:
        return {
            "asdf://stsci.edu/datamodels/roman/tags/mosaic_segmentation_map-1.0.0": "asdf://stsci.edu/datamodels/roman/schemas/mosaic_segmentation_map-1.0.0"
        }

    @property
    def default_array_shape(self) -> tuple[int, int]:
        return (4096, 4096)

    @property
    def testing_array_shape(self) -> tuple[int, int]:
        return (8, 8)

    @rad.field
    def meta(self) -> MosaicSegmentationMap_Meta:
        return MosaicSegmentationMap_Meta()

    @rad.field
    def data(self) -> npt.NDArray[np.uint32]:
        return np.zeros(self.array_shape, dtype=np.uint32)
