from astropy.modeling import Model
from astropy.modeling.models import Shift

from roman_datamodels.stnode import rad

from .ref import RefCommonRefOpticalElementRef, RefTypeEntry

__all__ = ["DistortionRef", "DistortionRef_Meta"]


class DistortionRef_Meta(rad.ImpliedNodeMixin, RefCommonRefOpticalElementRef):
    @classmethod
    def _asdf_implied_by(cls) -> type:
        return DistortionRef

    @rad.field
    def reftype(self) -> RefTypeEntry:
        return RefTypeEntry.DISTORTION


class DistortionRef(rad.TaggedObjectNode):
    @classmethod
    def _asdf_tag_uris(cls) -> dict[str, str]:
        return {
            "asdf://stsci.edu/datamodels/roman/tags/reference_files/distortion-1.0.0": "asdf://stsci.edu/datamodels/roman/schemas/reference_files/distortion-1.0.0"
        }

    @rad.field
    def meta(self) -> DistortionRef_Meta:
        return DistortionRef_Meta()

    @rad.field
    def coordinate_distortion_transform(self) -> Model:
        # Astropy has not implemented type hints for modeling so MyPy will complain about this
        # until they do.
        return Shift(1) & Shift(2)  # type: ignore[no-any-return, no-untyped-call, operator]
