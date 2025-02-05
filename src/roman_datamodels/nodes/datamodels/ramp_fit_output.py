import numpy as np
import numpy.typing as npt

from roman_datamodels.stnode import rad

from .meta.common import Common

__all__ = ["RampFitOutput", "RampFitOutput_Meta"]


class RampFitOutput_Meta(rad.ImpliedNodeMixin, Common):
    """
    The metadata for the RampFitOutput node
    -> only exists so that model_type can be correctly inferred
    """

    @classmethod
    def _asdf_implied_by(cls) -> type:
        return RampFitOutput


class RampFitOutput(rad.TaggedObjectNode, rad.ArrayFieldMixin):
    @classmethod
    def _asdf_tag_uris(cls) -> dict[str, str]:
        return {
            "asdf://stsci.edu/datamodels/roman/tags/ramp_fit_output-1.0.0": "asdf://stsci.edu/datamodels/roman/schemas/ramp_fit_output-1.0.0"
        }

    @property
    def primary_array_name(self) -> str:
        return "slope"

    @property
    def default_array_shape(self) -> tuple[int, int, int]:
        return (8, 4096, 4096)

    @property
    def testing_array_shape(self) -> tuple[int, int, int]:
        return (2, 8, 8)

    @rad.field
    def meta(self) -> RampFitOutput_Meta:
        return RampFitOutput_Meta()

    @rad.field
    def slope(self) -> npt.NDArray[np.float32]:
        return np.zeros(self.array_shape, dtype=np.float32)

    @rad.field
    def sigslope(self) -> npt.NDArray[np.float32]:
        return np.zeros(self.array_shape, dtype=np.float32)

    @rad.field
    def yint(self) -> npt.NDArray[np.float32]:
        return np.zeros(self.array_shape, dtype=np.float32)

    @rad.field
    def sigyint(self) -> npt.NDArray[np.float32]:
        return np.zeros(self.array_shape, dtype=np.float32)

    @rad.field
    def pedestal(self) -> npt.NDArray[np.float32]:
        return np.zeros(self.array_shape[1:], dtype=np.float32)

    @rad.field
    def weights(self) -> npt.NDArray[np.float32]:
        return np.zeros(self.array_shape, dtype=np.float32)

    @rad.field
    def crmag(self) -> npt.NDArray[np.float32]:
        return np.zeros(self.array_shape, dtype=np.float32)

    @rad.field
    def var_poisson(self) -> npt.NDArray[np.float32]:
        return np.zeros(self.array_shape, dtype=np.float32)

    @rad.field
    def var_rnoise(self) -> npt.NDArray[np.float32]:
        return np.zeros(self.array_shape, dtype=np.float32)
