"""
This module exists due to the mixing of ref_common and ref_optical_element sharing the same field,
instrument. This meant I had to be extra careful in creating the class for this for everything to
work properly. Since this is reused in multiple places, I decided to make it a separate class.
It is its own module because it is a weird special case.
"""

from roman_datamodels.stnode import rad

from .ref_common import RefCommonRef, RefCommonRef_Instrument
from .ref_optical_element import RefOpticalElementRef, RefOpticalElementRef_Instrument

__all__ = ["RefCommonRefOpticalElementRef", "RefCommonRefOpticalElementRef_Instrument"]


class RefCommonRefOpticalElementRef_Instrument(RefCommonRef_Instrument, RefOpticalElementRef_Instrument, rad.ImpliedNodeMixin):
    @classmethod
    def _asdf_implied_by(cls) -> type:
        return RefCommonRefOpticalElementRef

    @classmethod
    def _asdf_required(cls) -> set[str]:
        return {
            *super()._asdf_required(),
            *RefCommonRef_Instrument._asdf_required(),
            *RefOpticalElementRef_Instrument._asdf_required(),
        }

    @property
    def schema_required(self) -> tuple[str, ...]:
        return tuple(self.asdf_required)


class RefCommonRefOpticalElementRef(RefCommonRef, RefOpticalElementRef):
    @classmethod
    def _asdf_required(cls) -> set[str]:
        return {
            *super()._asdf_required(),
            *RefCommonRef._asdf_required(),
            *RefOpticalElementRef._asdf_required(),
        }

    @rad.field
    def instrument(self) -> RefCommonRefOpticalElementRef_Instrument:  # type: ignore[override]
        return RefCommonRefOpticalElementRef_Instrument()
