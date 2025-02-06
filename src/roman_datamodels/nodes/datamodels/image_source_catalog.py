from astropy.table import Table

from roman_datamodels.stnode import rad

from .meta import (
    Basic,
    Exposure,
    Photometry,
    Program,
    Visit,
    WfiOpticalElement,
)

__all__ = ["ImageSourceCatalog", "ImageSourceCatalog_Meta"]


class ImageSourceCatalog_Meta(rad.ImpliedNodeMixin, Basic):
    @classmethod
    def _asdf_implied_by(cls) -> type:
        return ImageSourceCatalog

    @rad.field
    def optical_element(self) -> WfiOpticalElement:
        return WfiOpticalElement.F158

    @rad.field
    def exposure(self) -> Exposure:
        return Exposure()

    @rad.field
    def photometry(self) -> Photometry:
        return Photometry()

    @rad.field
    def program(self) -> Program:
        return Program()

    @rad.field
    def visit(self) -> Visit:
        return Visit()


class ImageSourceCatalog(rad.TaggedObjectNode):
    @classmethod
    def _asdf_tag_uris(cls) -> dict[str, str]:
        return {
            "asdf://stsci.edu/datamodels/roman/tags/image_source_catalog-1.0.0": "asdf://stsci.edu/datamodels/roman/schemas/image_source_catalog-1.0.0"
        }

    @rad.field
    def meta(self) -> ImageSourceCatalog_Meta:
        return ImageSourceCatalog_Meta()

    @rad.field
    def source_catalog(self) -> Table:
        # Astropy has not implemented type hints for Table so MyPy will complain about this
        # until they do.
        return Table([range(3), range(3)], names=["a", "b"])  # type: ignore[no-untyped-call]
