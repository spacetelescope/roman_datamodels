"""
This module provides the same interface as the datamodels for JWST, so that they can be
    used in a common pipeline structure. Unlike the JWST datamodels, these models are
    backed by an ASDF file and the schema structure is defined by the ASDF schema.

This provides the abstract base class ``Datamodel`` for all the specific datamodels
    used for Roman. This dataclass is intended to be subclassed to form all of the actual
    working datamodels.
"""

import abc
import copy
import datetime
import functools
import sys
from contextlib import contextmanager
from pathlib import Path, PurePath

import asdf
import numpy as np
from asdf.exceptions import ValidationError
from astropy.time import Time

from roman_datamodels import stnode, validate

__all__ = ["DataModel", "MODEL_REGISTRY"]

MODEL_REGISTRY = {}


def _set_default_asdf(func):
    """
    Decorator which ensures that a DataModel has an asdf file available for use
    if required
    """

    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        if self._asdf is None:
            try:
                with validate.nuke_validation():
                    af = asdf.AsdfFile()
                    af["roman"] = self._instance
                    af.validate()
                    self._asdf = af
            except ValidationError as err:
                raise ValueError(f"DataModel needs to have all its data flushed out before calling {func.__name__}") from err

        return func(self, *args, **kwargs)

    return wrapper


@contextmanager
def _temporary_update_filename(datamodel, filename):
    """
    Context manager to temporarily update the filename of a datamodel so that it
    can be saved with that new file name without changing the current model's filename
    """
    from roman_datamodels.stnode import Filename

    if "meta" in datamodel._instance and "filename" in datamodel._instance.meta:
        old_filename = datamodel._instance.meta.filename
        datamodel._instance.meta.filename = Filename(filename)

        yield
        datamodel._instance.meta.filename = old_filename
        return

    yield
    return


class DataModel(abc.ABC):
    """Base class for all top level datamodels"""

    crds_observatory = "roman"

    @abc.abstractproperty
    def _node_type(self):
        """Define the top-level node type for this model"""
        pass

    def __init_subclass__(cls, **kwargs):
        """Register each subclass in the MODEL_REGISTRY"""
        super().__init_subclass__(**kwargs)

        # Allow for sub-registry classes to be defined
        if cls.__name__.startswith("_"):
            return

        # Check the node_type is a tagged object node
        if not issubclass(cls._node_type, stnode.TaggedObjectNode):
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

    def __init__(self, init=None, **kwargs):
        if isinstance(init, self.__class__):
            # Due to __new__ above, this is already initialized.
            return

        self._iscopy = False
        self._shape = None
        self._instance = None
        self._asdf = None

        if isinstance(init, stnode.TaggedObjectNode):
            if not isinstance(self, MODEL_REGISTRY.get(init.__class__)):
                expected = {mdl: node for node, mdl in MODEL_REGISTRY.items()}[self.__class__].__name__
                raise ValidationError(
                    f"TaggedObjectNode: {init.__class__.__name__} is not of the type expected. Expected {expected}"
                )
            with validate.nuke_validation():
                self._instance = init
                af = asdf.AsdfFile()
                af["roman"] = self._instance
                af.validate()
                self._asdf = af
                return

        if init is None:
            self._instance = self._node_type()

        elif isinstance(init, (str, bytes, PurePath)):
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
    def schema_uri(self):
        # Determine the schema corresponding to this model's tag
        return next(t for t in stnode.NODE_EXTENSIONS[0].tags if t.tag_uri == self._instance._tag).schema_uris[0]

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

    __copy__ = __deepcopy__ = copy

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
        target._ctx = target

    def save(self, path, dir_path=None, *args, **kwargs):
        path = Path(path(self.meta.filename) if callable(path) else path)
        output_path = Path(dir_path) / path.name if dir_path else path
        ext = path.suffix.decode(sys.getfilesystemencoding()) if isinstance(path.suffix, bytes) else path.suffix

        # TODO: Support gzip-compressed fits
        if ext == ".asdf":
            self.to_asdf(output_path, *args, **kwargs)
        else:
            raise ValueError(f"unknown filetype {ext}")

        return output_path

    def open_asdf(self, init=None, **kwargs):
        with validate.nuke_validation():
            return asdf.open(init, **kwargs) if isinstance(init, str) else asdf.AsdfFile(init, **kwargs)

    def to_asdf(self, init, *args, **kwargs):
        with validate.nuke_validation(), _temporary_update_filename(self, Path(init).name):
            asdf_file = self.open_asdf(**kwargs)
            asdf_file["roman"] = self._instance
            asdf_file.write_to(init, *args, **kwargs)

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
        if attr.startswith("_"):
            self.__dict__[attr] = value
        else:
            setattr(self._instance, attr, value)

    def __getattr__(self, attr):
        return getattr(self._instance, attr)

    def __setitem__(self, key, value):
        if key.startswith("_"):
            raise ValueError("May not specify attributes/keys that start with _")
        self._instance[key] = value

    def __getitem__(self, key):
        return self._instance[key]

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
            f"roman.{key}": convert_val(val) for (key, val) in self.items() if include_arrays or not isinstance(val, np.ndarray)
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

        def recurse(tree, path=[]):
            if isinstance(tree, (stnode.DNode, dict)):
                for key, val in tree.items():
                    yield from recurse(val, path + [key])
            elif isinstance(tree, (stnode.LNode, list, tuple)):
                for i, val in enumerate(tree):
                    yield from recurse(val, path + [i])
            elif tree is not None:
                yield (".".join(str(x) for x in path), tree)

        yield from recurse(self._instance)

    def get_crds_parameters(self):
        """
        Get parameters used by CRDS to select references for this model.

        Returns
        -------
        dict
        """
        return {
            key: val
            for key, val in self.to_flat_dict(include_arrays=False).items()
            if isinstance(val, (str, int, float, complex, bool))
        }

    def validate(self):
        """
        Re-validate the model instance against the tags
        """
        validate.value_change(self._instance, pass_invalid_values=False, strict_validation=True)

    @_set_default_asdf
    def info(self, *args, **kwargs):
        return self._asdf.info(*args, **kwargs)

    @_set_default_asdf
    def search(self, *args, **kwargs):
        return self._asdf.search(*args, **kwargs)

    @_set_default_asdf
    def schema_info(self, *args, **kwargs):
        return self._asdf.schema_info(*args, **kwargs)
