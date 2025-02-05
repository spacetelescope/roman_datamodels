from astropy.time import Time

from roman_datamodels.stnode import rad

from ...datamodels import InstrumentNameEntry, Telescope, WfiDetector, WfiOpticalElement

__all__ = [
    "RefCommonPedigreeEntry",
    "RefCommonRef",
    "RefCommonRef_Instrument",
    "RefCommonRef_InstrumentMixin",
    "RefTypeEntry",
]


class RefTypeEntry(rad.StrNodeMixin, rad.RadEnum, metaclass=rad.NodeEnumMeta):
    """
    Enum for the possible ref_type entries
        Note: this one doesn't actually exist but it is impled by each of the reftype entries
              in the reference_files schemas
    """

    ABVEGAOFFSET = "ABVEGAOFFSET"
    APCORR = "APCORR"
    DARK = "DARK"
    DISTORTION = "DISTORTION"
    EPSF = "EPSF"
    FLAT = "FLAT"
    GAIN = "GAIN"
    INVERSELINEARITY = "INVERSELINEARITY"
    IPC = "IPC"
    LINEARITY = "LINEARITY"
    MASK = "MASK"
    AREA = "AREA"  # for pixelarea
    READNOISE = "READNOISE"
    REFPIX = "REFPIX"
    SATURATION = "SATURATION"
    BIAS = "BIAS"  # for superbias
    PHOTOM = "PHOTOM"  # for wfi_img_photom
    NA = "N/A"  # for a default value in ref_common

    @classmethod
    def _asdf_schema(cls) -> rad.RadSchema:
        return rad.RadSchema({})


class RefCommonPedigreeEntry(rad.StrNodeMixin, rad.RadEnum, metaclass=rad.NodeEnumMeta):
    """
    Enum for the possible entries for pedigree in ref_common
    """

    GROUND = "GROUND"
    MODEL = "MODEL"
    DUMMY = "DUMMY"
    SIMULATION = "SIMULATION"

    @classmethod
    def _asdf_container(cls) -> type:
        return RefCommonRef

    @classmethod
    def _asdf_property_name(cls) -> str:
        return "pedigree"


class RefCommonRef_InstrumentMixin(rad.ExtraFieldsMixin):
    """Mixin things present in the constructors not present in the schema"""

    @rad.field
    def optical_element(self) -> WfiOpticalElement:
        return WfiOpticalElement.F158


class RefCommonRef_Instrument(RefCommonRef_InstrumentMixin, rad.ImpliedNodeMixin, rad.ObjectNode):
    @classmethod
    def _asdf_implied_by(cls) -> type:
        return RefCommonRef

    @rad.field
    def name(self) -> InstrumentNameEntry:
        return InstrumentNameEntry.WFI

    @rad.field
    def detector(self) -> WfiDetector:
        return WfiDetector.WFI01


class RefCommonRef(rad.SchemaObjectNode):
    @classmethod
    def _asdf_schema_uris(self) -> tuple[str]:
        return ("asdf://stsci.edu/datamodels/roman/schemas/reference_files/ref_common-1.0.0",)

    @rad.field
    def reftype(self) -> RefTypeEntry:
        return RefTypeEntry.NA

    @rad.field
    def pedigree(self) -> RefCommonPedigreeEntry:
        return RefCommonPedigreeEntry.GROUND

    @rad.field
    def description(self) -> str:
        return "blah blah blah"

    @rad.field
    def author(self) -> str:
        return "test system"

    @rad.field
    def useafter(self) -> Time:
        # Astropy has not implemented type hints for Time so MyPy will complain about this
        # until they do.
        return Time("2020-01-01T00:00:00.0", format="isot", scale="utc")  # type: ignore[no-untyped-call]

    @rad.field
    def telescope(self) -> Telescope | str:
        return Telescope.ROMAN

    @rad.field
    def origin(self) -> str:
        return "STSCI"

    @rad.field
    def instrument(self) -> RefCommonRef_Instrument:
        return RefCommonRef_Instrument()
