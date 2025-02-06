from roman_datamodels.stnode import rad

__all__ = ["OutlierDetection"]


class OutlierDetection(rad.TaggedObjectNode):
    @classmethod
    def _asdf_tag_uris(cls) -> dict[str, str]:
        return {
            "asdf://stsci.edu/datamodels/roman/tags/outlier_detection-1.0.0": "asdf://stsci.edu/datamodels/roman/schemas/outlier_detection-1.0.0"
        }

    @rad.field
    def good_bits(self) -> str:
        return "NA"
