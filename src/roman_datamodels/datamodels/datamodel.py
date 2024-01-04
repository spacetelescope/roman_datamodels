from __future__ import annotations

from typing import Any, ClassVar

from asdf import AsdfFile

from roman_datamodels.pydantic import RomanDataModel


class TaggedDataModel(RomanDataModel):
    _schema_uri: ClassVar[str | None] = None
    _tag_uri: ClassVar[str | None] = None

    _iscopy: bool = False
    _shape: tuple[int, ...] | None = None
    _asdf: AsdfFile | None = None

    def model_post_init(self, __context: Any) -> None:
        if self._asdf is None:
            self._asdf = AsdfFile()

    @property
    def tag_uri(self) -> str | None:
        return self._tag_uri

    @property
    def schema_uri(self) -> str | None:
        return self._schema_uri

    def close(self):
        if not (self._iscopy or self._asdf is None):
            self._asdf.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
