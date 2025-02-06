from roman_datamodels.stnode import rad

__all__ = ["SourceCatalog"]


class SourceCatalog(rad.TaggedObjectNode):
    @classmethod
    def _asdf_tag_uris(cls) -> dict[str, str]:
        return {
            "asdf://stsci.edu/datamodels/roman/tags/source_catalog-1.0.0": "asdf://stsci.edu/datamodels/roman/schemas/source_catalog-1.0.0"
        }

    @rad.field
    def tweakreg_catalog_name(self) -> str:
        return "catalog"
