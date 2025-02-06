from astropy.time import Time

from roman_datamodels.stnode import core, rad

__all__ = [
    "Visit",
    "VisitEngineeringQualityEntry",
    "VisitPointingEngineeringSourceEntry",
    "VisitStatusEntry",
    "VisitTypeEntry",
    "Visit_Dither",
]


class VisitEngineeringQualityEntry(rad.StrNodeMixin, rad.RadEnum, metaclass=rad.NodeEnumMeta):
    """
    Enum for the possible entries for quality in visit engineering
    """

    OK = "OK"
    SUSPECT = "SUSPECT"

    @classmethod
    def _asdf_container(cls) -> type:
        return Visit

    @classmethod
    def _asdf_property_name(cls) -> str:
        return "engineering_quality"


class VisitPointingEngineeringSourceEntry(rad.StrNodeMixin, rad.RadEnum, metaclass=rad.NodeEnumMeta):
    """
    Enum for the possible entries for source in visit pointing engineering
    """

    CALCULATED = "CALCULATED"
    PLANNED = "PLANNED"

    @classmethod
    def _asdf_container(cls) -> type:
        return Visit

    @classmethod
    def _asdf_property_name(cls) -> str:
        return "pointing_engineering_source"


class VisitTypeEntry(rad.StrNodeMixin, rad.RadEnum, metaclass=rad.NodeEnumMeta):
    """
    Enum for the possible entries for type in visit
    """

    GENERAL_ENGINEERING = "GENERAL_ENGINEERING"
    GENERIC = "GENERIC"
    PARALLEL = "PARALLEL"
    PRIME_TARGETED_FIXED = "PRIME_TARGETED_FIXED"
    PRIME_UNTARGETED = "PRIME_UNTARGETED"

    @classmethod
    def _asdf_container(cls) -> type:
        return Visit

    @classmethod
    def _asdf_property_name(cls) -> str:
        return "type"


class VisitStatusEntry(rad.StrNodeMixin, rad.RadEnum, metaclass=rad.NodeEnumMeta):
    """
    Enum for the possible entries for status in visit
    """

    DATALOSS = "DATALOSS"
    SUCCESSFUL = "SUCCESSFUL"
    UNSUCCESSFUL = "UNSUCCESSFUL"

    @classmethod
    def _asdf_container(cls) -> type:
        return Visit

    @classmethod
    def _asdf_property_name(cls) -> str:
        return "status"


class Visit_Dither(rad.ImpliedNodeMixin, rad.ObjectNode):
    @classmethod
    def _asdf_implied_by(cls) -> type:
        return Visit

    @rad.field
    def primary_name(self) -> str | None:
        return "None"

    @rad.field
    def subpixel_name(self) -> str | None:
        return "None"

    @rad.field
    def executed_pattern(self) -> core.LNode[float] | None:
        return core.LNode([float(v) for v in range(1, 10)])


class Visit(rad.TaggedObjectNode):
    @classmethod
    def _asdf_tag_uris(cls) -> dict[str, str]:
        return {
            "asdf://stsci.edu/datamodels/roman/tags/visit-1.0.0": "asdf://stsci.edu/datamodels/roman/schemas/visit-1.0.0",
        }

    @rad.field
    def dither(self) -> Visit_Dither:
        return Visit_Dither()

    @rad.field
    def engineering_quality(self) -> VisitEngineeringQualityEntry:
        return VisitEngineeringQualityEntry.OK

    @rad.field
    def pointing_engineering_source(self) -> VisitPointingEngineeringSourceEntry:
        return VisitPointingEngineeringSourceEntry.CALCULATED

    @rad.field
    def type(self) -> VisitTypeEntry:
        return VisitTypeEntry.PRIME_TARGETED_FIXED

    @rad.field
    def start_time(self) -> Time:
        # Astropy has not implemented type hints for Time so MyPy will complain about this
        # until they do.
        return Time("2020-01-01T00:00:00.0", format="isot", scale="utc")  # type: ignore[no-untyped-call]

    @rad.field
    def end_time(self) -> Time:
        # Astropy has not implemented type hints for Time so MyPy will complain about this
        # until they do.
        return Time("2020-01-01T00:00:00.0", format="isot", scale="utc")  # type: ignore[no-untyped-call]

    @rad.field
    def status(self) -> VisitStatusEntry:
        return VisitStatusEntry.UNSUCCESSFUL

    @rad.field
    def nexposures(self) -> int:
        return rad.NOINT

    @rad.field
    def internal_target(self) -> bool:
        return False
