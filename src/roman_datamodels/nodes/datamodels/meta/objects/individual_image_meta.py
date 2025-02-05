from astropy.table import QTable, Table

from roman_datamodels.stnode import rad

__all__ = ["IndividualImageMeta"]


class IndividualImageMeta(rad.TaggedObjectNode):
    @classmethod
    def _asdf_tag_uris(cls) -> dict[str, str]:
        return {
            "asdf://stsci.edu/datamodels/roman/tags/individual_image_meta-1.0.0": "asdf://stsci.edu/datamodels/roman/schemas/individual_image_meta-1.0.0"
        }

    @rad.field
    def basic(self) -> Table:
        # Astropy has not implemented type hints for Table so MyPy will complain about this
        # until they do.
        return QTable({"dummy": [rad.NONUM]})  # type: ignore[no-untyped-call]

    @rad.field
    def background(self) -> Table:
        # Astropy has not implemented type hints for Table so MyPy will complain about this
        # until they do.
        return QTable({"dummy": [rad.NONUM]})  # type: ignore[no-untyped-call]

    @rad.field
    def cal_step(self) -> Table:
        # Astropy has not implemented type hints for Table so MyPy will complain about this
        # until they do.
        return QTable({"dummy": [rad.NONUM]})  # type: ignore[no-untyped-call]

    @rad.field
    def cal_logs(self) -> Table:
        # Astropy has not implemented type hints for Table so MyPy will complain about this
        # until they do.
        return QTable({"dummy": [rad.NONUM]})  # type: ignore[no-untyped-call]

    @rad.field
    def coordinates(self) -> Table:
        # Astropy has not implemented type hints for Table so MyPy will complain about this
        # until they do.
        return QTable({"dummy": [rad.NONUM]})  # type: ignore[no-untyped-call]

    @rad.field
    def ephemeris(self) -> Table:
        # Astropy has not implemented type hints for Table so MyPy will complain about this
        # until they do.
        return QTable({"dummy": [rad.NONUM]})  # type: ignore[no-untyped-call]

    @rad.field
    def exposure(self) -> Table:
        # Astropy has not implemented type hints for Table so MyPy will complain about this
        # until they do.
        return QTable({"dummy": [rad.NONUM]})  # type: ignore[no-untyped-call]

    @rad.field
    def guide_star(self) -> Table:
        # Astropy has not implemented type hints for Table so MyPy will complain about this
        # until they do.
        return QTable({"dummy": [rad.NONUM]})  # type: ignore[no-untyped-call]

    @rad.field
    def instrument(self) -> Table:
        # Astropy has not implemented type hints for Table so MyPy will complain about this
        # until they do.
        return QTable({"dummy": [rad.NONUM]})  # type: ignore[no-untyped-call]

    @rad.field
    def observation(self) -> Table:
        # Astropy has not implemented type hints for Table so MyPy will complain about this
        # until they do.
        return QTable({"dummy": [rad.NONUM]})  # type: ignore[no-untyped-call]

    @rad.field
    def outlier_detection(self) -> Table:
        # Astropy has not implemented type hints for Table so MyPy will complain about this
        # until they do.
        return QTable({"dummy": [rad.NONUM]})  # type: ignore[no-untyped-call]

    @rad.field
    def photometry(self) -> Table:
        # Astropy has not implemented type hints for Table so MyPy will complain about this
        # until they do.
        return QTable({"dummy": [rad.NONUM]})  # type: ignore[no-untyped-call]

    @rad.field
    def pointing(self) -> Table:
        # Astropy has not implemented type hints for Table so MyPy will complain about this
        # until they do.
        return QTable({"dummy": [rad.NONUM]})  # type: ignore[no-untyped-call]

    @rad.field
    def program(self) -> Table:
        # Astropy has not implemented type hints for Table so MyPy will complain about this
        # until they do.
        return QTable({"dummy": [rad.NONUM]})  # type: ignore[no-untyped-call]

    @rad.field
    def rcs(self) -> Table:
        # Astropy has not implemented type hints for Table so MyPy will complain about this
        # until they do.
        return QTable({"dummy": [rad.NONUM]})  # type: ignore[no-untyped-call]

    @rad.field
    def ref_file(self) -> Table:
        # Astropy has not implemented type hints for Table so MyPy will complain about this
        # until they do.
        return QTable({"dummy": [rad.NONUM]})  # type: ignore[no-untyped-call]

    @rad.field
    def source_catalog(self) -> Table:
        # Astropy has not implemented type hints for Table so MyPy will complain about this
        # until they do.
        return QTable({"dummy": [rad.NONUM]})  # type: ignore[no-untyped-call]

    @rad.field
    def velocity_aberration(self) -> Table:
        # Astropy has not implemented type hints for Table so MyPy will complain about this
        # until they do.
        return QTable({"dummy": [rad.NONUM]})  # type: ignore[no-untyped-call]

    @rad.field
    def visit(self) -> Table:
        # Astropy has not implemented type hints for Table so MyPy will complain about this
        # until they do.
        return QTable({"dummy": [rad.NONUM]})  # type: ignore[no-untyped-call]

    @rad.field
    def wcsinfo(self) -> Table:
        # Astropy has not implemented type hints for Table so MyPy will complain about this
        # until they do.
        return QTable({"dummy": [rad.NONUM]})  # type: ignore[no-untyped-call]
