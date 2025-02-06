from __future__ import annotations

from roman_datamodels.stnode import rad

__all__ = ["ProductType"]


class ProductType(str, rad.TaggedScalarNode):
    @classmethod
    def _asdf_tag_uris(cls) -> dict[str, str]:
        return {
            "asdf://stsci.edu/datamodels/roman/tags/product_type-1.0.0": "asdf://stsci.edu/datamodels/roman/schemas/tagged_scalars/product_type-1.0.0"
        }

    @classmethod
    def default(cls) -> ProductType:
        return cls("l2")
