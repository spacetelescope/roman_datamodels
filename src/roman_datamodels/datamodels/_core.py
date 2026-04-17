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
from typing import TYPE_CHECKING

import asdf
import numpy as np
from asdf.exceptions import ValidationError
from asdf.tags.core.ndarray import NDArrayType
from astropy.time import Time

from roman_datamodels._stnode import NODE_EXTENSIONS, DNode, TaggedObjectNode

if TYPE_CHECKING:
    from collections.abc import Mapping
    from typing import Any, Self

__all__ = ["MODEL_REGISTRY", "DataModel"]

MODEL_REGISTRY: dict[str, type[DataModel]] = {}


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


class DataModel(abc.ABC):
    """Base class for all top level datamodels"""

    crds_observatory = "roman"

    _node_type: type[TaggedObjectNode]

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

        # Add to registry
        MODEL_REGISTRY[cls._node_type] = cls

    def __new__(cls, init=None, **kwargs):
        """
        Handle the case where one passes in an already instantiated version
        of the model. In this case the constructor should just directly return
        the model.
        """
        if init.__class__.__name__ == cls.__name__:
            return init

        return super().__new__(cls)

    @classmethod
    def create_minimal(cls, defaults: Mapping[str, Any] | None = None, *, tag: str | None = None) -> Self:
        """
        Class method that constructs an "minimal" model.

        The "minimal" model will contain schema-required attributes
        where a default value can be determined:

            * node class defining a default value
            * defined in the schema (for example single item enums)
            * empty container classes (for example a "meta" dict)
            * required items with a corresponding provided default

        Parameters
        ----------
        defaults : None or dict
            If provided, defaults will be used in place of schema
            defined values for required attributes.

        tag: str or None
            If provided, specifically create a model using this tag not the
            default one.

        Returns
        -------
        DataModel
            "Empty" model with optional defaults. This will often
            be incomplete (invalid) as not all required attributes
            can be guessed.
        """
        return cls(cls._node_type.create_minimal(defaults, tag=tag))

    @classmethod
    def create_fake_data(
        cls, defaults: Mapping[str, Any] | None = None, shape: tuple[int, ...] | None = None, *, tag: str | None = None
    ) -> Self:
        """
        Class method that constructs a model filled with fake data.

        Similar to `DataModel.create_minimal` this only creates
        required attributes.

        Fake arrays will have a number of dimensions matching
        the schema requirements. If shape is provided only the
        dimensions matching the schema requirements will be used.
        For example if a 3 dimensional shape is provided but a fake
        array only requires 2 dimensions only the first 2 values
        from shape will be used.

        Parameters
        ----------
        defaults : None or dict
            If provided, defaults will be used in place of schema
            defined or fake values for required attributes.

        shape : None or tuple of int
            When provided use this shape to determine the
            shape used to construct fake arrays.

        tag: str or None
            If provided, specifically create a model using this tag not the
            default one.

        Returns
        -------
        DataModel
            A valid model with fake data.
        """
        return cls(cls._node_type.create_fake_data(defaults, shape, tag=tag))

    __slots__ = ("_asdf", "_files_to_close", "_instance", "_iscopy", "_shape")

    @classmethod
    def create_from_model(cls, model: DataModel | DNode) -> Self:
        """
        Create a new DataModel from an existing model.
        """
        if isinstance(model, DataModel):
            node = model._instance
        else:
            node = model
        return cls(cls._node_type.create_from_node(node))

    def __init__(self, init=None, **kwargs):
        if isinstance(init, self.__class__):
            # Due to __new__ above, this is already initialized.
            return

        self._iscopy = False
        self._shape = None
        self._instance = None
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

    def check_type(self, asdf_file):
        """
        Subclass is expected to check for proper type of node
        """
        if "roman" not in asdf_file.tree:
            raise ValueError('ASDF file does not have expected "roman" attribute')

        return MODEL_REGISTRY[asdf_file.tree["roman"].__class__] == self.__class__

    @property
    def _latest_manifest_uri(self):
        return self._node_type._latest_manifest

    @property
    def schema_uri(self):
        # Determine the schema corresponding to this model's tag
        return next(t for t in NODE_EXTENSIONS[self._latest_manifest_uri].tags if t.tag_uri == self._instance._tag).schema_uris[0]

    def close(self):
        if not (self._iscopy or self._asdf is None):
            self._asdf.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __del__(self):
        """Ensure closure of resources when deleted."""
        self.close()

    def copy(self, deepcopy=True, memo=None):
        result = self.__class__(init=None)
        self.clone(result, self, deepcopy=deepcopy, memo=memo)
        return result

    __copy__ = copy

    def __deepcopy__(self, memo=None):
        return self.copy(deepcopy=True, memo=memo)

    @staticmethod
    def clone(target, source, deepcopy=False, memo=None):
        if deepcopy:
            target._asdf = source._asdf.copy()
            target._instance = copy.deepcopy(source._instance, memo=memo)
        else:
            target._asdf = source._asdf
            target._instance = source._instance

        target._iscopy = True
        target._files_to_close = []
        target._shape = source._shape

    def save(self, path, dir_path=None, *args, all_array_compression="lz4", all_array_storage="internal", **kwargs):
        path = Path(path(self.meta.filename) if callable(path) else path)
        output_path = Path(dir_path) / path.name if dir_path else path
        ext = path.suffix.decode(sys.getfilesystemencoding()) if isinstance(path.suffix, bytes) else path.suffix

        # TODO: Support gzip-compressed fits
        if ext == ".asdf":
            self.to_asdf(
                output_path, *args, all_array_compression=all_array_compression, all_array_storage=all_array_storage, **kwargs
            )
        elif ext == ".parquet" and hasattr(self, "to_parquet"):
            to_parquet_kwargs = {}
            if "ivoa_compliant" in kwargs:
                to_parquet_kwargs["ivoa_compliant"] = kwargs["ivoa_compliant"]
            self.to_parquet(output_path, **to_parquet_kwargs)
        else:
            raise ValueError(f"unknown filetype {ext}")

        return output_path

    def open_asdf(self, init=None, **kwargs):
        from ._utils import _open_asdf

        if isinstance(init, str):
            return _open_asdf(init, **kwargs)

        return asdf.AsdfFile(init, **kwargs)

    def to_asdf(self, init, *args, all_array_compression="lz4", all_array_storage="internal", **kwargs):
        from ._utils import temporary_update_filedate, temporary_update_filename

        with (
            temporary_update_filename(self, Path(init).name),
            temporary_update_filedate(self, Time.now()),
        ):
            asdf_file = self.open_asdf(**kwargs)
            asdf_file["roman"] = self._instance
            asdf_file.write_to(
                init, *args, all_array_compression=all_array_compression, all_array_storage=all_array_storage, **kwargs
            )

    def get_primary_array_name(self):
        """
        Returns the name "primary" array for this model, which
        controls the size of other arrays that are implicitly created.
        This is intended to be overridden in the subclasses if the
        primary array's name is not "data".
        """
        return "data" if hasattr(self, "data") else ""

    @property
    def override_handle(self):
        """override_handle identifies in-memory models where a filepath
        would normally be used.
        """
        # Arbitrary choice to look something like crds://
        return f"override://{self.__class__.__name__}"

    @property
    def shape(self):
        if self._shape is None:
            primary_array_name = self.get_primary_array_name()
            if primary_array_name and hasattr(self, primary_array_name):
                primary_array = getattr(self, primary_array_name)
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

    def to_flat_dict(self, include_arrays=True):
        """
        Returns a dictionary of all of the model items as a flat dictionary.

        Each dictionary key is a dot-separated name.  For example, the
        model element ``meta.observation.date`` will end up in the
        dictionary as::

            { "meta.observation.date": "2012-04-22T03:22:05.432" }

        This differs from the JWST data model in that the schema is not
        directly used
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

    def items(self):
        """
        Iterates over all of the model items in a flat way.

        Each element is a pair (``key``, ``value``).  Each ``key`` is a
        dot-separated name.  For example, the schema element
        ``meta.observation.date`` will end up in the result as::

            ("meta.observation.date": "2012-04-22T03:22:05.432")

        Unlike the JWST DataModel implementation, this does not use
        schemas directly.
        """

        yield from self._instance._recursive_items()

    def get_crds_parameters(self):
        """
        Get parameters used by CRDS to select references for this model.

        This will only return items under ``roman.meta``.

        Returns
        -------
        dict
        """
        return {
            f"roman.meta.{key}": val
            for key, val in self.meta.to_flat_dict(include_arrays=False, recursive=True).items()
            if isinstance(val, str | int | float | complex | bool)
        }

    @_set_default_asdf
    def validate(self):
        """
        Re-validate the model instance against the tags
        """
        self._asdf.validate()

    @_set_default_asdf
    def info(self, *args, **kwargs):
        return self._asdf.info(*args, **kwargs)

    @_set_default_asdf
    def search(self, *args, **kwargs):
        return self._asdf.search(*args, **kwargs)

    @_set_default_asdf
    def schema_info(self, *args, **kwargs):
        return self._asdf.schema_info(*args, **kwargs)
