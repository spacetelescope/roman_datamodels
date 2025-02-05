import numpy as np
import numpy.typing as npt

from roman_datamodels.stnode import rad

from .meta.common import Common

__all__ = ["MsosStack", "MsosStack_Meta"]


class MsosStack_Meta(rad.ImpliedNodeMixin, Common):
    @classmethod
    def _asdf_implied_by(cls) -> type:
        return MsosStack

    @rad.field
    def image_list(self) -> str:
        return rad.NOSTR


class MsosStack(rad.TaggedObjectNode, rad.ArrayFieldMixin):
    @classmethod
    def _asdf_tag_uris(cls) -> dict[str, str]:
        return {
            "asdf://stsci.edu/datamodels/roman/tags/msos_stack-1.0.0": "asdf://stsci.edu/datamodels/roman/schemas/msos_stack-1.0.0"
        }

    @property
    def default_array_shape(self) -> tuple[int, int]:
        return (4096, 4096)

    @property
    def testing_array_shape(self) -> tuple[int, int]:
        return (8, 8)

    @rad.field
    def meta(self) -> MsosStack_Meta:
        return MsosStack_Meta()

    @rad.field
    def data(self) -> npt.NDArray[np.float64]:
        return np.zeros(self.array_shape, dtype=np.float64)

    @rad.field
    def uncertainty(self) -> npt.NDArray[np.float64]:
        return np.zeros(self.array_shape, dtype=np.float64)

    @rad.field
    def mask(self) -> npt.NDArray[np.uint8]:
        return np.zeros(self.array_shape, dtype=np.uint8)

    @rad.field
    def coverage(self) -> npt.NDArray[np.uint8]:
        return np.zeros(self.array_shape, dtype=np.uint8)
