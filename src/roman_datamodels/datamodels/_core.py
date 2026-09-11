"""
This module provides the same interface as the datamodels for JWST, so that they can be
    used in a common pipeline structure. Unlike the JWST datamodels, these models are
    backed by an ASDF file and the schema structure is defined by the ASDF schema.

This provides the abstract base class ``Datamodel`` for all the specific datamodels
    used for Roman. This dataclass is intended to be subclassed to form all of the actual
    working datamodels.
"""

from __future__ import annotations

import abc
import copy
import datetime
import functools
import sys
from pathlib import Path, PurePath
from typing import TYPE_CHECKING, ClassVar

import asdf
import numpy as np
from asdf.exceptions import ValidationError
from asdf.tags.core.ndarray import NDArrayType
from asdf.util import NotSet
from astropy.time import Time

from roman_datamodels._stnode import NODE_EXTENSIONS, DNode, TaggedObjectNode

if TYPE_CHECKING:
    from collections.abc import Callable, Generator
    from os import PathLike
    from typing import Any, Self

__all__ = ["MODEL_REGISTRY", "DataModel"]

MODEL_REGISTRY: dict[type[TaggedObjectNode], type[DataModel]] = {}

DEFAULT_ARRAY_INLINE_THRESHOLD = 512


def _set_default_asdf(func):
    """
    Decorator which ensures that a DataModel has an asdf file available for use
    if required
    """

    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        if self._asdf is None:
            af = asdf.AsdfFile()
            af["roman"] = self._instance
            self._asdf = af

        return func(self, *args, **kwargs)

    return wrapper


def _schema_link_from_tag(tag_uri: str) -> str:
    """
    generate an intersphinx link docstring for the given tag uri to the rad documentation.
    """
    page = tag_uri.replace("asdf://stsci.edu/datamodels/roman/tags", "generated/schemas")
    text = tag_uri.replace("/tags/", "/schemas/")

    return f"The schema for this DataModel is :external+rad:doc:`{text} <{page}>`"


class DataModel(abc.ABC):
    """
    Base class for all top level data models

    This includes both:
    - The Science Product Data Models
    - The Reference File Data Models
    """

    crds_observatory: ClassVar[str] = "roman"
    """
    Name of the observatory for CRDS purposes
    """

    _node_type: ClassVar[type[TaggedObjectNode]]
    """
    The STNode type associated with this DataModel.
    """

    _is_copy: bool
    """
    Indicates whether this instance is a copy of another instance.
    """

    _shape: tuple[int, ...] | None
    """
    The shape of the data contained in this DataModel instance.
    """

    _instance: TaggedObjectNode
    """
    The underlying STNode instance associated with this DataModel.
    """

    _asdf: asdf.AsdfFile | None
    """
    The ASDF file associated with this DataModel instance, if any.
    """

    def __init_subclass__(cls, **kwargs):
        """Register each subclass in the MODEL_REGISTRY"""
        super().__init_subclass__(**kwargs)

        # Allow for sub-registry classes to be defined
        if cls.__name__.startswith("_"):
            return

        # Check the node_type is a tagged object node
        if not issubclass(cls._node_type, TaggedObjectNode):
            raise ValueError("Subclass must be a TaggedObjectNode subclass")

        # Check for duplicates
        if cls._node_type in MODEL_REGISTRY:
            raise ValueError(f"Duplicate model type {cls._node_type}")

        cls.__doc__ = f"DataModel for node type :class:`~roman_datamodels._stnode.{cls._node_type.__name__}`\n\n{_schema_link_from_tag(cls._node_type._default_tag)}"

        # Add to registry
        MODEL_REGISTRY[cls._node_type] = cls

    # Handle the case where one passes in an already instantiated version
    # of the model. In this case the constructor should just directly return
    # the model.
    def __new__(cls, init=None, **kwargs):
        if init.__class__.__name__ == cls.__name__:
            return init

        return super().__new__(cls)

    # The mypy ignore is due to a limitation of mypy where it is only looking at the direct
    #   object and its main base class. Since this is originates in the _TaggedNodeMixin, mypy
    #   cannot see the create_minimal enough to examine exactly what it is.
    @classmethod
    @functools.wraps(TaggedObjectNode.create_minimal.__func__)  # type: ignore[attr-defined]
    def create_minimal(cls, defaults=None, *, tag=None):
        return cls(cls._node_type.create_minimal(defaults, tag=tag))

    @classmethod
    @functools.wraps(TaggedObjectNode.create_fake_data.__func__)  # type: ignore[attr-defined]
    def create_fake_data(cls, defaults=None, shape=None, *, tag=None):
        return cls(cls._node_type.create_fake_data(defaults, shape, tag=tag))

    __slots__ = ("_asdf", "_files_to_close", "_instance", "_iscopy", "_shape")

    @classmethod
    def create_from_model(cls, model: DataModel | DNode) -> Self:
        """
        Create an instance of this model from an existing model

        Parameters
        ----------
        model :
            Model or DNode to convert from. The values in this will be used
            to fill the new model instance

        Returns
        -------
            A new instance of the model created from the provided model or DNode.
        """
        if isinstance(model, DataModel):
            node: DNode = model._instance
        else:
            node = model
        return cls(cls._node_type.create_from_node(node))

    def __init__(self, init=None, **kwargs):
        if isinstance(init, self.__class__):
            # Due to __new__ above, this is already initialized.
            return

        self._iscopy = False
        self._shape = None
        self._asdf = None
        self._files_to_close = None

        if isinstance(init, TaggedObjectNode):
            if not isinstance(self, MODEL_REGISTRY.get(init.__class__)):
                expected = {mdl: node for node, mdl in MODEL_REGISTRY.items()}[self.__class__].__name__
                raise ValidationError(
                    f"TaggedObjectNode: {init.__class__.__name__} is not of the type expected. Expected {expected}"
                )

            self._instance = init
            af = asdf.AsdfFile()
            af["roman"] = self._instance
            self._asdf = af
            return

        if init is None:
            self._instance = self._node_type()

        elif isinstance(init, str | bytes | PurePath):
            if isinstance(init, PurePath):
                init = str(init)
            if isinstance(init, bytes):
                init = init.decode(sys.getfilesystemencoding())

            self._asdf = self.open_asdf(init, **kwargs)
            if not self.check_type(self._asdf):
                raise ValueError(f"ASDF file is not of the type expected. Expected {self.__class__.__name__}")

            self._instance = self._asdf.tree["roman"]
        elif isinstance(init, asdf.AsdfFile):
            self._asdf = init

            self._instance = self._asdf.tree["roman"]
        else:
            raise OSError("Argument does not appear to be an ASDF file or TaggedObjectNode.")

    def check_type(self, asdf_file: asdf.AsdfFile) -> bool:
        """
        Check that an ASDF file is for the expected node type

        Parameters
        ----------
        asdf_file :
            The ASDF file to check the type of.

        Returns
        -------
            True if the ASDF file contains the expected node type, False otherwise.
        """
        if "roman" not in asdf_file.tree:
            raise ValueError('ASDF file does not have expected "roman" attribute')

        return MODEL_REGISTRY[asdf_file.tree["roman"].__class__] == self.__class__

    @property
    def _latest_manifest_uri(self):
        return self._node_type._latest_manifest

    @property
    def schema_uri(self) -> str:
        """
        The URI of the schema in RAD for this data model
        """
        # Determine the schema corresponding to this model's tag
        return next(t for t in NODE_EXTENSIONS[self._latest_manifest_uri].tags if t.tag_uri == self._instance._tag).schema_uris[0]  # type: ignore[no-any-return]

    def close(self) -> None:
        """Close the associated ASDF file"""
        if not (self._iscopy or self._asdf is None):
            self._asdf.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __del__(self):
        """Ensure closure of resources when deleted"""
        self.close()

    def copy(self, deepcopy: bool = True, memo: dict[int, Any] | None = None) -> Self:
        """
        Create a copy of the current instance

        Parameters
        ----------
        deepcopy :
            If True, perform a deep copy. Otherwise, perform a shallow copy.
        memo :
            Memoization dictionary for deep copy.

        Returns
        -------
            The copied instance.
        """
        result = self.__class__(init=None)
        self.clone(result, self, deepcopy=deepcopy, memo=memo)
        return result

    __copy__ = copy

    def __deepcopy__(self, memo: dict[int, Any] | None = None) -> Self:
        return self.copy(deepcopy=True, memo=memo)

    @staticmethod
    def clone(target: DataModel, source: DataModel, deepcopy: bool = False, memo: dict[int, Any] | None = None) -> None:
        """
        Clone the source contents into the target

        Parameters
        ----------
        target :
            The target DataModel instance to clone into.
        source :
            The source DataModel instance to clone from.
        deepcopy :
            If True, perform a deep copy. Otherwise, perform a shallow copy.
        memo :
            Memoization dictionary for deep copy.
        """
        if deepcopy:
            target._asdf = source._asdf.copy() if source._asdf is not None else None
            target._instance = copy.deepcopy(source._instance, memo=memo)
        else:
            target._asdf = source._asdf
            target._instance = source._instance

        target._iscopy = True
        target._files_to_close = []
        target._shape = source._shape

    def save(
        self,
        path: PathLike | (Callable[[PathLike], str]),
        dir_path: PathLike | None = None,
        *args: Any,
        all_array_compression: str = "lz4",
        all_array_storage: Any = NotSet,
        **kwargs: Any,
    ) -> Path:
        """
        Save the model to a file

        Parameters
        ----------
        path :
            The path or a callable that returns the path to save the file to.
        dir_path :
            Optional directory path to prepend to the output file.
        *args :
            Additional positional arguments to pass to the underlying save method.
        all_array_compression :
            Compression method for all arrays.
        all_array_storage :
            Storage method for all arrays.
        **kwargs :
            Additional keyword arguments to pass to the underlying save method.

        Returns
        -------
            The path to the saved file.
        """
        path = Path(path(self.meta.filename) if callable(path) else path)
        output_path = Path(dir_path) / path.name if dir_path else path
        ext = path.suffix.decode(sys.getfilesystemencoding()) if isinstance(path.suffix, bytes) else path.suffix

        if ext == ".asdf":
            self.to_asdf(
                output_path, *args, all_array_compression=all_array_compression, all_array_storage=all_array_storage, **kwargs
            )
        elif ext == ".parquet" and hasattr(self, "to_parquet"):
            self.to_parquet(output_path)
        else:
            raise ValueError(f"unknown filetype {ext}")

        return output_path

    @staticmethod
    def open_asdf(init: PathLike | asdf.AsdfFile | None = None, **kwargs: Any) -> asdf.AsdfFile:
        """
        Open an ASDF file

        Parameters
        ----------
        init :
            An object that can be opened by `asdf.open`
        **kwargs :
            Additional arguments to pass to `asdf.open`

        Returns
        -------
            The opened ASDF file
        """
        from ._utils import _open_asdf

        if isinstance(init, str):
            return _open_asdf(init, **kwargs)

        return asdf.AsdfFile(init, **kwargs)

    def to_asdf(
        self,
        init: PathLike,
        *args: Any,
        all_array_compression: str = "lz4",
        all_array_storage: Any = NotSet,
        **kwargs: Any,
    ) -> None:
        """
        Save the model to an ASDF file.

        Parameters
        ----------
        init :
            The path to save the ASDF file to.
        *args :
            Additional positional arguments to pass to `asdf.AsdfFile.write_to`.
        all_array_compression :
            Compression method for all arrays.
        all_array_storage :
            Storage method for all arrays.
        **kwargs :
            Additional keyword arguments to pass to `asdf.AsdfFile.write_to`.
        """
        from ._utils import _temporary_update_filedate, _temporary_update_filename

        with (
            _temporary_update_filename(self, Path(init).name),
            _temporary_update_filedate(self, Time.now()),
        ):
            asdf_file = self.open_asdf(**kwargs)
            asdf_file["roman"] = self._instance
            with asdf.config_context() as cfg:
                # only set array inline threshold if not already set by the user
                if cfg.array_inline_threshold is None and all_array_storage is NotSet:
                    cfg.array_inline_threshold = DEFAULT_ARRAY_INLINE_THRESHOLD

                asdf_file.write_to(
                    init, *args, all_array_compression=all_array_compression, all_array_storage=all_array_storage, **kwargs
                )

    def get_primary_array_name(self) -> str:
        """
        Returns the name "primary" array for this model

        This array controls the size of other arrays that are implicitly created.

        This is intended to be overridden in the subclasses if the primary
        array's name is not "data".

        Returns
        -------
            The name of the primary data array.
        """
        return "data" if hasattr(self, "data") else ""

    @property
    def override_handle(self) -> str:
        """
        The file path used for in-memory models
        """
        # Arbitrary choice to look something like crds://
        return f"override://{self.__class__.__name__}"

    @property
    def shape(self) -> tuple[int, ...] | None:
        """
        The shape of the primary data array
        """
        if self._shape is None:
            if (primary_array_name := self.get_primary_array_name()) and hasattr(self, primary_array_name):
                primary_array: np.ndarray = getattr(self, primary_array_name)
                self._shape = primary_array.shape
        return self._shape

    def __setattr__(self, attr, value):
        if attr.startswith("_") and attr in DataModel.__slots__:
            DataModel.__dict__[attr].__set__(self, value)
        else:
            setattr(self._instance, attr, value)

    def __getattr__(self, attr):
        return getattr(self._instance, attr)

    def __delattr__(self, attr):
        if attr.startswith("_") and attr in DataModel.__slots__:
            super().__delattr__(attr)
        else:
            delattr(self._instance, attr)

    def __setitem__(self, key, value):
        if key.startswith("_"):
            raise ValueError("May not specify attributes/keys that start with _")
        self._instance[key] = value

    def __getitem__(self, key):
        return self._instance[key]

    def __dir__(self):
        return set(super().__dir__()) | set(dir(self._instance))

    def __iter__(self):
        return iter(self._instance)

    def to_flat_dict(self, include_arrays: bool = True) -> dict[str, Any]:
        """
        Flattened Dictionary Representation of the Model

        Each dictionary key is a dot-separated name.  For example, the
        model element ``meta.observation.date`` will end up in the
        dictionary as::

            { "meta.observation.date": "2012-04-22T03:22:05.432" }

        This differs from the JWST data model in that the schema is not
        directly used

        Parameters
        ----------
        include_arrays :
            Whether to include array-type items in the flat dictionary. Defaults to True.

        Returns
        -------
            A flat dictionary representation of the model.
        """

        def convert_val(val):
            if isinstance(val, datetime.datetime):
                return val.isoformat()
            elif isinstance(val, Time):
                return str(val)
            return val

        return {
            f"roman.{key}": convert_val(val)
            for (key, val) in self.items()
            if include_arrays or not isinstance(val, np.ndarray | NDArrayType)
        }

    def items(self) -> Generator[tuple[str, Any], None, None]:
        """
        Iterates over all of the model items in a flat way

        Each element is a pair (``key``, ``value``).  Each ``key`` is a
        dot-separated name.  For example, the schema element
        ``meta.observation.date`` will end up in the result as::

            ("meta.observation.date": "2012-04-22T03:22:05.432")

        Unlike the JWST DataModel implementation, this does not use
        schemas directly.

        Returns
        -------
            A generator of key-value pairs representing the flat dictionary of the model.
        """

        yield from self._instance._recursive_items()

    def get_crds_parameters(self) -> dict[str, Any]:
        """
        Get parameters used by CRDS

        This is used to select references for this model.

        This will only return items under ``roman.meta``.

        Returns
        -------
            The CRDS parameters as a flat dictionary.
        """
        return {
            f"roman.meta.{key}": val
            for key, val in self.meta.to_flat_dict(include_arrays=False, recursive=True).items()
            if isinstance(val, str | int | float | complex | bool)
        }

    @_set_default_asdf
    @functools.wraps(asdf.AsdfFile.validate)
    def validate(self):
        self._asdf.validate()

    @_set_default_asdf
    @functools.wraps(asdf.AsdfFile.info)
    def info(self, *args, **kwargs):
        return self._asdf.info(*args, **kwargs)

    @_set_default_asdf
    @functools.wraps(asdf.AsdfFile.search)
    def search(self, *args, **kwargs):
        return self._asdf.search(*args, **kwargs)

    @_set_default_asdf
    @functools.wraps(asdf.AsdfFile.schema_info)
    def schema_info(self, *args, **kwargs):
        return self._asdf.schema_info(*args, **kwargs)
