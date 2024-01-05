"""
This module contains the base class for all ASDF-serializable data models. These
models can be independently serialized and deserialized using the ASDF library.
"""
from __future__ import annotations

import abc
import sys
import warnings
from collections.abc import Callable
from contextlib import contextmanager
from pathlib import Path
from typing import Any, ClassVar

import asdf

from roman_datamodels.pydantic import BaseRomanDataModel

asdf_file = str | Path | asdf.AsdfFile | None


class RomanDataModel(BaseRomanDataModel):
    """
    Base class for all ASDF serializable Roman data models.
        Provides all the interfaces necessary for CRDS and stpipe to use the model.
    """

    # crds_observatory is required for the stpipe DataModel protocol
    crds_observatory: ClassVar[str] = "roman"

    @abc.abstractproperty
    def tag_uri(cls) -> str:
        ...

    _shape: tuple[int, ...] | None = None
    _asdf: asdf.AsdfFile | None = None
    _asdf_external: bool = False

    @property
    def _has_model_type(self) -> bool:
        """Determines if the model has the model_type attribute."""
        return "meta" in self and "model_type" in self.meta

    def model_post_init(self, __context: Any):
        """
        Post initialization hook for the model.
            This is called after all the Pydantic related initialization is complete, as part
            of the initialization of a model instance.
        """
        # Set the model_type (if it has one), to match the class name
        if self._has_model_type:
            self.meta.model_type = self.__class__.__name__

    @property
    def _has_filename(self) -> bool:
        """Determines if the model has a filename attribute."""
        return "meta" in self and "filename" in self.meta

    @contextmanager
    def _temporary_filename_update(self, filename: str) -> None:
        """
        Context manager to temporally update the meta.filename attribute (if it exists), then
        restore it to its original value after the context exits.
            This is to facilitate writing the resulting model to a new ASDF file while enabling
            the filename in the newly written file to make sense, while retaining the original filename
            for the model in memory.
        """
        if self._has_filename:
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
        if not isinstance(file, str | Path):
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

    ###############################################################################################################
    #     Allow the data model to be used as a context manager to manage if it's asdf file is open or closed      #
    ###############################################################################################################
    def close(self):
        if not (self._asdf_external or self._asdf is None):
            self._asdf.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    ###############################################################################################################
    #                                          End context manager                                                #
    ###############################################################################################################

    def save(self, path: str | Path | Callable, dir_path: str | Path | None = None, *args, **kwargs) -> Path:
        """
        Save the model to a file.

            Note this is the interface used directly by stpipe when running STScI's pipeline to
            save a model to a file. The interface here is constrained to the interface defined by
            the stpipe DataModel protocol.

        Parameters
        ----------
        path: str, Path, or Callable
            The path to save the model to. If a Callable is provided, it should return a path or filename.
        dir_path: str or Path, optional
            The directory to save the model to. If None, the current working directory,
            typically this is where the code is run from, is used.
        *args :
            Additional positional arguments passed to self.to_asdf().
        **kwargs :
            Additional keyword arguments passed to self.to_asdf().

        Returns
        -------
        The path ultimately saved to
        """
        if not isinstance(path, str | Path | Callable):
            raise TypeError(f"Expected path to be a string, Path, or Callable; not {type(path).__name__}")

        # Invoke the callable if necessary
        if callable(path):
            if self._has_filename:
                path = path(self.meta.filename)
            else:
                raise ValueError("Cannot use a Callable path if the model does not have a filename attribute")

        # make sure we have a Path object
        path = Path(path)

        # If a directory is provided, join it to the path
        output_path = Path(dir_path) / path.name if dir_path is not None else path

        # Find the extension
        ext = path.suffix.decode(sys.getfilesystemencoding()) if isinstance(path.suffix, bytes) else path.suffix

        # TODO: Support gzip-compressed fits
        if ext == ".asdf":
            self.to_asdf(output_path, *args, **kwargs)
        else:
            raise ValueError(f"unknown filetype {ext}")

        return output_path

    def get_crds_parameters(self):
        """
        Get parameters used by CRDS to select references for this model.

            Note this is the interface used directly by stpipe when running STScI's pipeline to
            to pull reference files. The interface here is constrained to the interface defined by
            the stpipe DataModel protocol.

        Returns
        -------
        dict
        """
        return {
            key: val
            for key, val in self.to_flat_dict(include_arrays=False).items()
            if isinstance(val, (str, int, float, complex, bool))
        }

    @property
    def override_handle(self) -> str:
        """
        override_handle identifies in-memory models where a filepath would normally be used.
        """
        # Arbitrary choice to look something like crds://
        return f"override://{self.__class__.__name__}"

    def get_primary_array_name(self) -> str | None:
        """
        Returns the name "primary" array for this model, which
        controls the size of other arrays that are implicitly created.
        This is intended to be overridden in the subclasses if the
        primary array's name is not "data".
        """
        return "data" if "data" in self else None

    @property
    def shape(self) -> tuple[int, ...] | None:
        """Return the shape of the primary array if it has one"""
        if self._shape is None:
            primary_array_name = self.get_primary_array_name()
            if primary_array_name and primary_array_name in self:
                primary_array = self[primary_array_name]
                self._shape = primary_array.shape

        return self._shape


# TODO:
#  - Address copy/clone of the model
#  - Address asdf functionality pass through
#  - Write tests for extended models
#  - Migrate the init and rdm.open functionality
