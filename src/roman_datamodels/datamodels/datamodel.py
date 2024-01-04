from __future__ import annotations

from typing import ClassVar

from asdf import AsdfFile

from roman_datamodels.pydantic import RomanDataModel


class TaggedDataModel(RomanDataModel):
    _tag_uri: ClassVar[str | None] = None

    _iscopy: bool = False
    _shape: tuple[int, ...] | None = None
    _instance: TaggedDataModel | None = None
    _asdf: AsdfFile | None = None
