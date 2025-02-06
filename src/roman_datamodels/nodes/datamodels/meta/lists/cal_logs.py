from __future__ import annotations

from roman_datamodels.stnode import rad

__all__ = ["CalLogs"]


class CalLogs(rad.TaggedListNode):
    @classmethod
    def default(cls) -> CalLogs:
        return cls(
            [
                "2021-11-15T09:15:07.12Z :: FlatFieldStep :: INFO :: Completed",
                "2021-11-15T10:22.55.55Z :: RampFittingStep :: WARNING :: Wow, lots of Cosmic Rays detected",
            ]
        )

    @classmethod
    def _asdf_tag_uris(cls) -> dict[str, str]:
        return {
            "asdf://stsci.edu/datamodels/roman/tags/cal_logs-1.0.0": "asdf://stsci.edu/datamodels/roman/schemas/cal_logs-1.0.0"
        }
