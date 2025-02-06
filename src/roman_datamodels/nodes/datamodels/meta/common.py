from roman_datamodels.stnode import rad

from .basic import Basic
from .objects import (
    Coordinates,
    Ephemeris,
    Exposure,
    Guidestar,
    Observation,
    Pointing,
    Program,
    Rcs,
    RefFile,
    VelocityAberration,
    Visit,
    Wcsinfo,
    WfiMode,
)

__all__ = ["Common"]


class Common(Basic):
    @classmethod
    def _asdf_schema_uris(cls) -> tuple[str]:
        return ("asdf://stsci.edu/datamodels/roman/schemas/common-1.0.0",)

    @rad.field
    def coordinates(self) -> Coordinates:
        return Coordinates()

    @rad.field
    def ephemeris(self) -> Ephemeris:
        return Ephemeris()

    @rad.field
    def exposure(self) -> Exposure:
        return Exposure()

    @rad.field
    def guide_star(self) -> Guidestar:
        return Guidestar()

    @rad.field
    def instrument(self) -> WfiMode:
        return WfiMode()

    @rad.field
    def observation(self) -> Observation:
        return Observation()

    @rad.field
    def pointing(self) -> Pointing:
        return Pointing()

    @rad.field
    def program(self) -> Program:
        return Program()

    @rad.field
    def rcs(self) -> Rcs:
        return Rcs()

    @rad.field
    def ref_file(self) -> RefFile:
        return RefFile()

    @rad.field
    def velocity_aberration(self) -> VelocityAberration:
        return VelocityAberration()

    @rad.field
    def visit(self) -> Visit:
        return Visit()

    @rad.field
    def wcsinfo(self) -> Wcsinfo:
        return Wcsinfo()
