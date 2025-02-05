from astropy.table import Table

from roman_datamodels.stnode import rad

from .meta import (
    Basic,
    MosaicBasic,
    Photometry,
    Program,
)

__all__ = ["MosaicSourceCatalog", "MosaicSourceCatalog_Meta"]


class MosaicSourceCatalog_Meta(rad.ImpliedNodeMixin, Basic):
    @classmethod
    def _asdf_implied_by(cls) -> type:
        return MosaicSourceCatalog

    @rad.field
    def basic(self) -> MosaicBasic:
        return MosaicBasic()

    @rad.field
    def photometry(self) -> Photometry:
        return Photometry()

    @rad.field
    def program(self) -> Program:
        return Program()


class MosaicSourceCatalog(rad.TaggedObjectNode):
    @classmethod
    def _asdf_tag_uris(cls) -> dict[str, str]:
        return {
            "asdf://stsci.edu/datamodels/roman/tags/mosaic_source_catalog-1.0.0": "asdf://stsci.edu/datamodels/roman/schemas/mosaic_source_catalog-1.0.0"
        }

    @rad.field
    def meta(self) -> MosaicSourceCatalog_Meta:
        return MosaicSourceCatalog_Meta()

    @rad.field
    def source_catalog(self) -> Table:
        # Astropy has not implemented type hints for Table so MyPy will complain about this
        # until they do.
        return Table([range(3), range(3)], names=["a", "b"])  # type: ignore[no-untyped-call]
