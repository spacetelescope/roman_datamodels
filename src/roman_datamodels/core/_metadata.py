"""
This module is to make accessing the archive_catalog and sdf metadata in the
schemas easier in a more organized way.
"""
from __future__ import annotations

from pydantic import BaseModel


class SdfOrigin(BaseModel):
    origin: str
    function: str | None = None


class Sdf(BaseModel):
    special_processing: str
    source: SdfOrigin


class ArchiveCatalog(BaseModel):
    datatype: str
    destination: list[str]


class Archive(BaseModel):
    sdf: Sdf | None = None
    archive_catalog: ArchiveCatalog | None = None

    @property
    def has_info(self):
        return self.sdf is not None or self.archive_catalog is not None


Archives = dict[str, Archive]
