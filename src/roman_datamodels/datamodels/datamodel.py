"""
This module contains the base class for all ASDF-serializable data models. These
models can be independently serialized and deserialized using the ASDF library.
"""
from __future__ import annotations

import abc
from typing import Any

from asdf import AsdfFile

from roman_datamodels.pydantic import RomanDataModel


class TaggedDataModel(RomanDataModel):
    @abc.abstractproperty
    def tag_uri(cls) -> str:
        ...

    _iscopy: bool = False
    _shape: tuple[int, ...] | None = None
    _asdf: AsdfFile | None = None

    def model_post_init(self, __context: Any) -> None:
        if self._asdf is None:
            self._asdf = AsdfFile()

    def close(self):
        if not (self._iscopy or self._asdf is None):
            self._asdf.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
