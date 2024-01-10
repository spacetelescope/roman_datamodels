"""
This module contains the base class for all ASDF-serializable data models. These
models can be independently serialized and deserialized using the ASDF library.
"""
from __future__ import annotations

__all__ = ["DataModel"]

import abc
import sys
import warnings
from collections.abc import Callable
from contextlib import contextmanager
from pathlib import Path
from typing import Any, ClassVar

import asdf

from ._base import BaseDataModel

asdf_file = str | Path | asdf.AsdfFile | None


class DataModel(BaseDataModel):
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
    _asdf_external: bool = True

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
        file :
            The "file" to open, default is None.
            - If None, a new ASDF file is created.
            - If str or Path, the file is opened using asdf.open().
            - If asdf.AsdfFile, the object is still passed through to asdf.AsdfFile(), but that
            should just return the same object back.
        **kwargs :
            Additional keyword arguments passed to asdf.open() or asdf.AsdfFile().
        """
        if not isinstance(file, asdf_file):
            raise TypeError(f"Expected file to be a string, Path, asdf.AsdfFile, or None; not {type(file).__name__}")

        return asdf.open(file, **kwargs) if isinstance(file, (str, Path)) else asdf.AsdfFile(file, **kwargs)

    def to_asdf(self, file: str | Path, *args, **kwargs) -> asdf.AsdfFile:
        """
        Write the model to an ASDF file.

        Parameters
        ----------
        file :
            The file to write the model to.
        *args :
            Additional positional arguments passed to self.open_asdf().
        **kwargs :
            Additional keyword arguments passed to self.open_asdf().
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
    def from_asdf(cls, file: asdf_file = None, **kwargs) -> DataModel:
        """
        Read a RomanDataModel from an ASDF file.

        Parameters
        ----------
        file :
            The ASDF file to read from.
            - If None, a new model is created using the default values.
            - If str or Path, the file is opened using asdf.open(). Note the model
            will attempt to close the file when it is "closed".
            - If asdf.AsdfFile, that file is assumed to contain the model. Note
            that if a file is directly passed in, the resulting model will not
            attempt to close the file when it is closed.
        **kwargs :
            Additional keyword arguments passed to asdf.open().
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
                file = asdf.open(file, **kwargs)
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

    @classmethod
    def create_model(cls, init: dict[str, Any] | DataModel | asdf_file = None, **kwargs) -> DataModel:
        """
        Create a new model from a dictionary, another model, or an ASDF file.

        Parameters
        ----------
        init :
            The data to initialize the model with. Note that if init is a RomanDataModel
            matching the type of the model, it is returned as is (no copies). If init
            is asdf_file-like (str, Path, asdf.AsdfFile, or None), the model is read
            from the file. Otherwise it is assumed to be a dictionary, which is passed
            to the normal Pydantic initializer.
        **kwargs :
            Additional keyword arguments passed to asdf.open().
        """
        if isinstance(init, DataModel):
            if isinstance(init, cls):
                return init

            raise TypeError(f"Expected model of type {cls.__name__}, got {type(init).__name__}")

        if isinstance(init, asdf_file):
            return cls.from_asdf(init, **kwargs)

        return cls(**init)

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
        path:
            The path to save the model to. If a Callable is provided, it should return a path or filename.
        dir_path:
            The directory to save the model to. If None, the current working directory,
            typically this is where the code is run from, is used.
        *args :
            Additional positional arguments passed to self.to_asdf().
        **kwargs :
            Additional keyword arguments passed to self.to_asdf().
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

    def get_crds_parameters(self) -> dict[str, str | int | float | complex | bool]:
        """
        Get parameters used by CRDS to select references for this model.

            Note this is the interface used directly by stpipe when running STScI's pipeline to
            to pull reference files. The interface here is constrained to the interface defined by
            the stpipe DataModel protocol.
        """
        return {
            f"roman.{key}": val
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

    @property
    def _asdf_file(self) -> asdf.AsdfFile:
        """
        Get the asdf file associated with this model.
            Note that if no ASDF file object is associated with this model, a new one is created.

            This new AsdfFile object should be valid because Pydantic ensures that the model
            has valid data up to what is annotated in the model by the code generator. There are
            three known exceptions to this:
                1. __setitem__ is used to set the data in the model, this means Pydantic did not
                   validate that data.
                2. The model.pause_validation(revalidate_on_exit=False) context manager is used to
                   and modifications took place on the model. That is intended to be a feature of
                   the model to enable developers to modify model fields before schema's are updated.
                3. The model's schema uses a "patternProperties" to constrain the formulation of
                   keys for a dictionary. This is a limitation of the code generator at this time.
                   This currently is limited to `WfiImgPhotomRefModel.phot_table`.
            All cases 1 and 2 will be caught if model.model_validate(model) is called before the
            asdf file is accessed. Case 3 currently can only be caught by ASDF (use model.asdf_validate).
        """
        if self._asdf is None:
            self._asdf = asdf.AsdfFile({"roman": self})
            self._asdf_external = False

        return self._asdf

    def asdf_validate(self) -> None:
        """Run ASDF validation on the model"""
        self._asdf_file.validate()

    def info(self, *args, **kwargs) -> str:
        """
        Call down into the info method for ASDF.
            This allows one to leverage ASDF's info functionality to get information about the data
            in the model.

        Parameters
        ----------
        *args :
            Positional arguments passed to ASDF's info method.
        **kwargs :
            Keyword arguments passed to ASDF's info method.
        """

        return self._asdf_file.info(*args, **kwargs)

    def search(self, *args, **kwargs) -> str:
        """
        Call down into the search method for ASDF.
            This allows one to leverage ASDF's search functionality to get information about the data
            in the model.

        Parameters
        ----------
        *args :
            Positional arguments passed to ASDF's search method.
        **kwargs :
            Keyword arguments passed to ASDF's search schema method.
        """

        return self._asdf_file.search(*args, **kwargs)

    def schema_info(self, *args, **kwargs) -> str:
        """
        Call down into the schema_info method for ASDF.
            This allows one to leverage ASDF's schema_info functionality to get information about the data
            in the model.

        Parameters
        ----------
        *args :
            Positional arguments passed to ASDF's schema_info method.
        **kwargs :
            Keyword arguments passed to ASDF's search schema_info method.
        """

        return self._asdf_file.schema_info(*args, **kwargs)

    @classmethod
    def make_default(cls, *, data: dict[str, Any] | None = None, filepath: str | Path | None = None, **kwargs) -> BaseDataModel:
        """
        Create a new model with the default values.
            This extends the existing make_default functionality by allowing us to write the model
            to an asdf file in addition to returning the model.

        Parameters
        ----------
        data :
            The input data to initialize the model with, if any.
        filepath :
            Path to file to write the model to, if any.
        **kwargs :
            Additional keyword arguments passed to the default constructors.
        """
        new_model = super().make_default(data=data, **kwargs)

        # Write the new model to a file if a filepath is provided
        if filepath:
            new_model.to_asdf(filepath)

        return new_model

    @contextmanager
    def _temporary_asdf(self) -> bool:
        """
        Context manager to temporally remove the asdf file associated with the model (if it exists), then
        restore it,
        This returns if the asdf file was removed or not.
        """
        if self._asdf is None:
            yield False
        else:
            old_asdf = self._asdf
            self._asdf = None
            yield True
            self._asdf = old_asdf

        return

    def copy(self, deepcopy: bool = True) -> DataModel:
        """
        Copy the model.
            This extends the existing copy functionality by allowing us to copy the asdf file
            associated with the model.

        Parameters
        ----------
        deepcopy :
            If True, a deep copy is made. Otherwise a shallow copy is made.
        """

        with self._temporary_asdf() as asdf_removed:
            new_model = super().copy(deepcopy=deepcopy)

            if asdf_removed:
                new_model._asdf_external = True
                new_model._asdf = asdf.AsdfFile({"roman": new_model})

            return new_model
