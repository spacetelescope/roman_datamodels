import numpy as np
import numpy.typing as npt

from roman_datamodels.stnode import rad

from .ref import RefCommonRefOpticalElementRef, RefTypeEntry

__all__ = ["IpcRef", "IpcRef_Meta"]


class IpcRef_Meta(rad.ImpliedNodeMixin, RefCommonRefOpticalElementRef):
    @classmethod
    def _asdf_implied_by(cls) -> type:
        return IpcRef

    @rad.field
    def reftype(self) -> RefTypeEntry:
        return RefTypeEntry.IPC


class IpcRef(rad.TaggedObjectNode, rad.ArrayFieldMixin):
    @classmethod
    def _asdf_tag_uris(cls) -> dict[str, str]:
        return {
            "asdf://stsci.edu/datamodels/roman/tags/reference_files/ipc-1.0.0": "asdf://stsci.edu/datamodels/roman/schemas/reference_files/ipc-1.0.0"
        }

    @property
    def default_array_shape(self) -> tuple[int, int]:
        return (3, 3)

    @property
    def testing_array_shape(self) -> tuple[int, int]:
        return self.default_array_shape

    @rad.field
    def meta(self) -> IpcRef_Meta:
        return IpcRef_Meta()

    @rad.field
    def data(self) -> npt.NDArray[np.float32]:
        data = np.zeros(self.array_shape, dtype=np.float32)
        data[int(np.floor(self.array_shape[0] / 2))][int(np.floor(self.array_shape[1] / 2))] = 1.0
        return data
