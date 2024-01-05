"""
This module contains the base class for all ASDF-serializable data models. These
models can be independently serialized and deserialized using the ASDF library.
"""
from __future__ import annotations

import abc
import warnings
from contextlib import contextmanager
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

    @contextmanager
    def _temporary_filename_update(self, filename: str) -> None:
        """
        Context manager to temporally update the meta.filename attribute (if it exists), then
        restore it to its original value after the context exits.
            This is to facilitate writing the resulting model to a new ASDF file while enabling
            the filename in the newly written file to make sense, while retaining the original filename
            for the model in memory.
        """
        if hasattr(self, "meta") and hasattr(self.meta, "filename"):
            old_filename = self.meta.filename
            self.meta.filename = filename
            yield
            self.meta.filename = old_filename
        else:
            yield

        return

    @staticmethod
    def open_asdf(file: asdf_file = None, **kwargs) -> asdf.AsdfFile:
        """
        Attempt to open an ASDF file.

        Parameters
        ----------
        file: str, Path, asdf.AsdfFile, or None
            The "file" to open, default is None.
            - If None, a new ASDF file is created.
            - If str or Path, the file is opened using asdf.open().
            - If asdf.AsdfFile, the object is still passed through to asdf.AsdfFile(), but that
              should just return the same object back.
        **kwargs :
            Additional keyword arguments passed to asdf.open() or asdf.AsdfFile().

        Returns
        -------
        An asdf.AsdfFile object.
        """
        if not isinstance(file, asdf_file):
            raise TypeError(f"Expected file to be a string, Path, asdf.AsdfFile, or None; not {type(file).__name__}")

        return asdf.open(file, **kwargs) if isinstance(file, (str, Path)) else asdf.AsdfFile(file, **kwargs)

    def to_asdf(self, file: str | Path, *args, **kwargs) -> asdf.AsdfFile:
        """
        Write the model to an ASDF file.
        """
        if not isinstance(file, (str, Path)):
            raise TypeError(f"Expected file to be a string or Path; not {type(file).__name__}")

        with self._temporary_filename_update(Path(file).name):
            # Open a blank ASDF file to write model to (note file not passed to open_asdf())
            af = self.open_asdf(**kwargs)
            af.tree = {"roman": self}
            af.write_to(file, *args, **kwargs)

            return af

    @classmethod
    def from_asdf(cls, file: asdf_file = None) -> RomanDataModel:
        """
        Read a RomanDataModel from an ASDF file.

        Parameters
        ----------
        file : str, Path, asdf.AsdfFile, or None
            The ASDF file to read from.
            - If None, a new model is created using the default values.
            - If str or Path, the file is opened using asdf.open(). Note the model
              will attempt to close the file when it is "closed".
            - If asdf.AsdfFile, that file is assumed to contain the model. Note
              that if a file is directly passed in, the resulting model will not
              attempt to close the file when it is closed.

        Returns
        -------
        A RomanDataModel from the ASDF file.
        """
        if not isinstance(file, asdf_file):
            raise TypeError(f"Expected file to be a string, Path, asdf.AsdfFile, or None; not {type(file).__name__}")

        # Handle closing the file if/when necessary
        opened_file = False
        external_asdf = True

        if file is None:
            # Create a new model with the default values
            new_cls = cls.make_default()
            warnings.warn("No file provided, creating default model")
        else:
            # Attempt to open a file if necessary
            if isinstance(file, (str, Path)):
                file = asdf.open(file)
                opened_file = True
                external_asdf = False

            # Attempt to grab the model from the file.
            #    Note that roman_datamodels always assumes that the model is stored
            #    under the "roman" keyword branching off the asdf tree root.
            try:
                new_cls = file.tree["roman"]
            except KeyError as err:
                if opened_file:
                    file.close()
                raise KeyError(f"{cls.__name__}.from_asdf expects a file with a 'roman' key") from err

        # Check that the model is of the correct type and return it
        if isinstance(new_cls, cls):
            new_cls._asdf = file
            new_cls._asdf_external = external_asdf
            return new_cls

        # Close the asdf file before returning the error
        if opened_file:
            file.close()

        raise TypeError(f"Expected file containing model of type {cls.__name__}, got {type(new_cls).__name__}")

    def close(self):
        if not (self._asdf_external or self._asdf is None):
            self._asdf.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
