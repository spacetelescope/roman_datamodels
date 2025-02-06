import numpy as np
import numpy.typing as npt

from roman_datamodels.stnode import rad

from .meta import Common

__all__ = ["WfiScienceRaw", "WfiScienceRaw_Meta"]


class WfiScienceRaw_Meta(rad.ImpliedNodeMixin, Common):
    """
    The metadata for the WfiScienceRaw node
    -> only exists so that model_type can be correctly inferred
    """

    @classmethod
    def _asdf_implied_by(cls) -> type:
        return WfiScienceRaw


class WfiScienceRaw(rad.TaggedObjectNode, rad.ArrayFieldMixin):
    @classmethod
    def _asdf_tag_uris(cls) -> dict[str, str]:
        return {
            "asdf://stsci.edu/datamodels/roman/tags/wfi_science_raw-1.0.0": "asdf://stsci.edu/datamodels/roman/schemas/wfi_science_raw-1.0.0"
        }

    @property
    def default_array_shape(self) -> tuple[int, int, int]:
        return (8, 4096, 4096)

    @property
    def testing_array_shape(self) -> tuple[int, int, int]:
        return (2, 8, 8)

    @rad.field
    def meta(self) -> WfiScienceRaw_Meta:
        return WfiScienceRaw_Meta()

    @rad.field
    def data(self) -> npt.NDArray[np.uint16]:
        return np.zeros(self.array_shape, dtype=np.uint16)

    @rad.field
    def amp33(self) -> npt.NDArray[np.uint16]:
        return np.zeros((self.array_shape[0], self.array_shape[1], 128), dtype=np.uint16)

    @rad.field
    def resultantdq(self) -> npt.NDArray[np.uint8]:
        return np.zeros(self.array_shape, dtype=np.uint8)
