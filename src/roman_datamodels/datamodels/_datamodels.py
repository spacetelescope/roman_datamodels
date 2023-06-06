"""
This module provides the same interface as the older, non-tag version of datamodels
for the whole asdf file. It will start very basic, initially only to support running
of the flat field step, but many other methods and capabilities will be added to
keep consistency with the JWST data model version.

It is to be subclassed by the various types of data model variants for products
"""

import abc
import copy
import datetime
import os
import os.path
import sys
import warnings
from pathlib import PurePath

import asdf
import numpy as np
import packaging.version
from astropy.time import Time
from jsonschema import ValidationError

from roman_datamodels import stnode, validate
from roman_datamodels.extensions import DATAMODEL_EXTENSIONS

# .dev is included in the version comparison to allow for correct version
# comparisons with development versions of asdf 3.0
if packaging.version.Version(asdf.__version__) < packaging.version.Version("3.dev"):
    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            category=asdf.exceptions.AsdfDeprecationWarning,
            message=r"AsdfInFits has been deprecated.*",
        )
        from asdf.fits_embed import AsdfInFits
else:
    AsdfInFits = None

__all__ = [
    "DataModel",
    "ImageModel",
    "ScienceRawModel",
    "RampModel",
    "RampFitOutputModel",
    "GuidewindowModel",
    "FlatRefModel",
    "DarkRefModel",
    "DistortionRefModel",
    "GainRefModel",
    "LinearityRefModel",
    "MaskRefModel",
    "PixelareaRefModel",
    "ReadnoiseRefModel",
    "RefpixRefModel",
    "SuperbiasRefModel",
    "SaturationRefModel",
    "WfiImgPhotomRefModel",
    "AssociationsModel",
    "IpcRefModel",
    "InverseLinearityRefModel",
    "MosaicModel",
    "open",
    "MODEL_REGISTRY",
]

MODEL_REGISTRY = {}


class DataModel(abc.ABC):
    """Base class for all top level datamodels"""

    crds_observatory = "roman"

    @abc.abstractproperty
    def _node_type(self):
        pass

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        if not issubclass(cls._node_type, stnode.TaggedObjectNode):
            raise ValueError("Subclass must be a TaggedObjectNode subclass")

        if cls._node_type in MODEL_REGISTRY:
            raise ValueError(f"Duplicate model type {cls._node_type}")

        MODEL_REGISTRY[cls._node_type] = cls

    def __init__(self, init=None, **kwargs):
        self._iscopy = False
        self._shape = None
        self._instance = None
        self._asdf = None
        if init is None:
            asdffile = self.open_asdf(init=None, **kwargs)
        elif isinstance(init, (str, bytes, PurePath)):
            if isinstance(init, PurePath):
                init = str(init)
            if isinstance(init, bytes):
                init = init.decode(sys.getfilesystemencoding())
            asdffile = self.open_asdf(init, **kwargs)
            if not self.check_type(asdffile):
                raise ValueError(f"ASDF file is not of the type expected. Expected {self.__class__.__name__}")
            self._instance = asdffile.tree["roman"]
        elif isinstance(init, asdf.AsdfFile):
            asdffile = init
            self._asdf = asdffile
            self._instance = asdffile.tree["roman"]
        elif isinstance(init, stnode.TaggedObjectNode):
            if not isinstance(self, MODEL_REGISTRY.get(init.__class__)):
                expected = {mdl: node for node, mdl in MODEL_REGISTRY.items()}[self.__class__].__name__
                raise ValidationError(
                    f"TaggedObjectNode: {init.__class__.__name__} is not of the type expected. Expected {expected}"
                )
            with validate.nuke_validation():
                self._instance = init
                asdffile = asdf.AsdfFile()
                asdffile.tree = {"roman": init}
        else:
            raise OSError("Argument does not appear to be an ASDF file or TaggedObjectNode.")
        self._asdf = asdffile

    def check_type(self, asdffile_instance):
        """
        Subclass is expected to check for proper type of node
        """
        if "roman" not in asdffile_instance.tree:
            raise ValueError('ASDF file does not have expected "roman" attribute')
        topnode = asdffile_instance.tree["roman"]
        if MODEL_REGISTRY[topnode.__class__] != self.__class__:
            return False
        return True

    @property
    def schema_uri(self):
        # Determine the schema corresponding to this model's tag
        schema_uri = next(t for t in DATAMODEL_EXTENSIONS[0].tags if t.tag_uri == self._instance._tag).schema_uris[0]
        return schema_uri

    def close(self):
        if not self._iscopy:
            if self._asdf is not None:
                self._asdf.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __del__(self):
        """Ensure closure of resources when deleted."""
        self.close()

    def copy(self, memo=None):
        result = self.__class__(init=None)
        self.clone(result, self, deepcopy=True, memo=memo)
        return result

    __copy__ = __deepcopy__ = copy

    @staticmethod
    def clone(target, source, deepcopy=False, memo=None):
        if deepcopy:
            instance = copy.deepcopy(source._instance, memo=memo)
            target._asdf = source._asdf.copy()
            target._instance = instance
            target._iscopy = True
        else:
            target._asdf = source._asdf
            target._instance = source._instance
            target._iscopy = True

        target._files_to_close = []
        target._shape = source._shape
        target._ctx = target

    def save(self, path, dir_path=None, *args, **kwargs):
        if callable(path):
            path_head, path_tail = os.path.split(path(self.meta.filename))
        else:
            path_head, path_tail = os.path.split(path)
        base, ext = os.path.splitext(path_tail)
        if isinstance(ext, bytes):
            ext = ext.decode(sys.getfilesystemencoding())

        if dir_path:
            path_head = dir_path
        output_path = os.path.join(path_head, path_tail)

        # TODO: Support gzip-compressed fits
        if ext == ".asdf":
            self.to_asdf(output_path, *args, **kwargs)
        else:
            raise ValueError(f"unknown filetype {ext}")

        return output_path

    def open_asdf(self, init=None, **kwargs):
        with validate.nuke_validation():
            if isinstance(init, str):
                asdffile = asdf.open(init)
            else:
                asdffile = asdf.AsdfFile(init)
            return asdffile

    def to_asdf(self, init, *args, **kwargs):
        with validate.nuke_validation():
            asdffile = self.open_asdf(**kwargs)
            asdffile.tree = {"roman": self._instance}
            asdffile.write_to(init, *args, **kwargs)

    def get_primary_array_name(self):
        """
        Returns the name "primary" array for this model, which
        controls the size of other arrays that are implicitly created.
        This is intended to be overridden in the subclasses if the
        primary array's name is not "data".
        """
        if hasattr(self, "data"):
            primary_array_name = "data"
        else:
            primary_array_name = ""
        return primary_array_name

    @property
    def override_handle(self):
        """override_handle identifies in-memory models where a filepath
        would normally be used.
        """
        # Arbitrary choice to look something like crds://
        return "override://" + self.__class__.__name__

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
        if hasattr(self._instance, key):
            setattr(self._instance, key, value)
        else:
            self._instance._data[key] = value

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

        if include_arrays:
            return {"roman." + key: convert_val(val) for (key, val) in self.items()}
        else:
            return {"roman." + key: convert_val(val) for (key, val) in self.items() if not isinstance(val, np.ndarray)}

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
        crds_header = {
            key: val
            for key, val in self.to_flat_dict(include_arrays=False).items()
            if isinstance(val, (str, int, float, complex, bool))
        }
        return crds_header

    def validate(self):
        """
        Re-validate the model instance against the tags
        """
        validate.value_change(self._instance, pass_invalid_values=False, strict_validation=True)

    def info(self, *args, **kwargs):
        return self._asdf.info(*args, **kwargs)

    def search(self, *args, **kwargs):
        return self._asdf.search(*args, **kwargs)

    def schema_info(self, *args, **kwargs):
        return self._asdf.schema_info(*args, **kwargs)


class MosaicModel(DataModel):
    _node_type = stnode.WfiMosaic


class ImageModel(DataModel):
    _node_type = stnode.WfiImage


class ScienceRawModel(DataModel):
    _node_type = stnode.WfiScienceRaw


class RampModel(DataModel):
    _node_type = stnode.Ramp

    @classmethod
    def from_science_raw(cls, model):
        """
        Construct a RampModel from a ScienceRawModel

        Parameters
        ----------
        model : ScienceRawModel or RampModel
            The input science raw model (a RampModel will also work)
        """

        if isinstance(model, cls):
            return model

        if isinstance(model, ScienceRawModel):
            from roman_datamodels.maker_utils import mk_ramp

            instance = mk_ramp(shape=model.shape)

            # Copy input_model contents into RampModel
            for key in model:
                # If a dictionary (like meta), overwrite entries (but keep
                # required dummy entries that may not be in input_model)
                if isinstance(instance[key], dict):
                    instance[key].update(getattr(model, key))
                elif isinstance(instance[key], np.ndarray):
                    # Cast input ndarray as RampModel dtype
                    instance[key] = getattr(model, key).astype(instance[key].dtype)
                else:
                    instance[key] = getattr(model, key)

            return cls(instance)

        raise ValueError("Input model must be a ScienceRawModel or RampModel")


class RampFitOutputModel(DataModel):
    _node_type = stnode.RampFitOutput


class AssociationsModel(DataModel):
    # Need an init to allow instantiation from a JSON file
    _node_type = stnode.Associations

    @classmethod
    def is_association(cls, asn_data):
        """
        Test if an object is an association by checking for required fields
        """
        if isinstance(asn_data, dict):
            if "asn_id" in asn_data and "asn_pool" in asn_data:
                return True
        return False


class GuidewindowModel(DataModel):
    _node_type = stnode.Guidewindow


class FlatRefModel(DataModel):
    _node_type = stnode.FlatRef


class DarkRefModel(DataModel):
    _node_type = stnode.DarkRef


class DistortionRefModel(DataModel):
    _node_type = stnode.DistortionRef


class GainRefModel(DataModel):
    _node_type = stnode.GainRef


class IpcRefModel(DataModel):
    _node_type = stnode.IpcRef


class LinearityRefModel(DataModel):
    _node_type = stnode.LinearityRef

    def get_primary_array_name(self):
        """
        Returns the name "primary" array for this model, which
        controls the size of other arrays that are implicitly created.
        This is intended to be overridden in the subclasses if the
        primary array's name is not "data".
        """
        return "coeffs"


class InverseLinearityRefModel(DataModel):
    _node_type = stnode.InverseLinearityRef

    def get_primary_array_name(self):
        """
        Returns the name "primary" array for this model, which
        controls the size of other arrays that are implicitly created.
        This is intended to be overridden in the subclasses if the
        primary array's name is not "data".
        """
        return "coeffs"


class MaskRefModel(DataModel):
    _node_type = stnode.MaskRef

    def get_primary_array_name(self):
        """
        Returns the name "primary" array for this model, which
        controls the size of other arrays that are implicitly created.
        This is intended to be overridden in the subclasses if the
        primary array's name is not "data".
        """
        return "dq"


class PixelareaRefModel(DataModel):
    _node_type = stnode.PixelareaRef


class ReadnoiseRefModel(DataModel):
    _node_type = stnode.ReadnoiseRef


class SuperbiasRefModel(DataModel):
    _node_type = stnode.SuperbiasRef


class SaturationRefModel(DataModel):
    _node_type = stnode.SaturationRef


class WfiImgPhotomRefModel(DataModel):
    _node_type = stnode.WfiImgPhotomRef


class RefpixRefModel(DataModel):
    _node_type = stnode.RefpixRef


def open(init, memmap=False, target=None, **kwargs):
    """
    Data model factory function

    Parameters
    ----------
    init : str, `DataModel`, `asdf.AsdfFile`
        May be any one of the following types:
            - `asdf.AsdfFile` instance
            - string indicating the path to an ASDF file
            - `DataModel` Roman data model instance
    memmap : bool
        Open ASDF file binary data using memmap (default: False)
    target : `DataModel`
        If not None value, the `DataModel` implied by the init argument
        must be an instance of the target class. If the init value
        is already a data model, and matches the target, the init
        value is returned, not copied, as opposed to the case where
        the init value is a data model, and target is not supplied,
        and the returned value is a copy of the init value.

    Returns
    -------
    `DataModel`
    """
    with validate.nuke_validation():
        file_to_close = None
        if target is not None:
            if not issubclass(target, DataModel):
                raise ValueError("Target must be a subclass of DataModel")
        # Temp fix to catch JWST args before being passed to asdf open
        if "asn_n_members" in kwargs:
            del kwargs["asn_n_members"]
        if isinstance(init, asdf.AsdfFile):
            asdffile = init
        elif isinstance(init, DataModel):
            if target is not None:
                if not isinstance(init, target):
                    raise ValueError("First argument is not an instance of target")
                else:
                    return init
            # Copy the object so it knows not to close here
            return init.copy()
        else:
            try:
                kwargs["copy_arrays"] = not memmap
                asdffile = asdf.open(init, **kwargs)
                file_to_close = asdffile
            except ValueError:
                raise TypeError("Open requires a filepath, file-like object, or Roman datamodel")
            if AsdfInFits is not None and isinstance(asdffile, AsdfInFits):
                if file_to_close is not None:
                    file_to_close.close()
                raise TypeError("Roman datamodels does not accept FITS files or objects")
        modeltype = type(asdffile.tree["roman"])
        if modeltype in MODEL_REGISTRY:
            rmodel = MODEL_REGISTRY[modeltype](asdffile, **kwargs)
            if target is not None:
                if not issubclass(rmodel.__class__, target):
                    if file_to_close is not None:
                        file_to_close.close()
                    raise ValueError("Referenced ASDF file model type is not subclass of target")
            else:
                return rmodel
        else:
            return DataModel(asdffile, **kwargs)