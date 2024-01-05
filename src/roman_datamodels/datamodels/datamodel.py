"""
This module contains the base class for all ASDF-serializable data models. These
models can be independently serialized and deserialized using the ASDF library.
"""
from __future__ import annotations

import abc
import warnings
from pathlib import Path

import asdf

from roman_datamodels.pydantic import BaseRomanDataModel

asdf_file = str | Path | asdf.AsdfFile | None


class RomanDataModel(BaseRomanDataModel):
    @abc.abstractproperty
    def tag_uri(cls) -> str:
        ...

    _shape: tuple[int, ...] | None = None
    _asdf: asdf.AsdfFile | None = None
    _asdf_external: bool = False

    @classmethod
    def from_asdf(cls, file: asdf_file = None) -> RomanDataModel:
        if not isinstance(file, asdf_file):
            raise TypeError("Expected file to be a string, Path, asdf.AsdfFile, or None")

        opened_file = False
        external_asdf = True

        if file is None:
            new_cls = cls.make_default()
            warnings.warn("No file provided, creating default model")
        else:
            if isinstance(file, (str, Path)):
                file = asdf.open(file)
                opened_file = True
                external_asdf = False

            new_cls = file.tree["roman"]

        # Check that the model is of the correct type and return it
        if isinstance(new_cls, cls):
            new_cls._asdf = file
            new_cls._asdf_external = external_asdf
            return new_cls

        # Close the asdf file before returning the error
        if opened_file:
            file.close()

        raise TypeError(f"Expected file containing model of type {cls.__name__}, got {type(new_cls).__name__}")

    # def to_asdf(self, file: asdf_file = None) -> asdf.AsdfFile:
    #     if file is None:
    #         file = asdf.AsdfFile()

    #     if isinstance(file, (str, Path)):
    #         file = asdf.AsdfFile.open(file)

    #     # Set the model in the ASDF file and return it
    #     file.tree["roman"] = self
    #     return file

    def close(self):
        if not (self._asdf_external or self._asdf is None):
            self._asdf.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
