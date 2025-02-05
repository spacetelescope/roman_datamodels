from __future__ import annotations

from astropy.time import Time

from roman_datamodels.stnode import rad

__all__ = ["FileDate"]


class FileDate(Time, rad.TaggedScalarNode):
    @classmethod
    def _asdf_tag_uris(cls) -> dict[str, str]:
        return {
            "asdf://stsci.edu/datamodels/roman/tags/file_date-1.0.0": "asdf://stsci.edu/datamodels/roman/schemas/tagged_scalars/file_date-1.0.0"
        }

    @classmethod
    def default(cls) -> FileDate:
        # Astropy has not implemented type hints for Time so MyPy will complain about this
        # until they do.
        return cls(Time("2020-01-01T00:00:00.0", format="isot", scale="utc"))  # type: ignore[no-untyped-call]
