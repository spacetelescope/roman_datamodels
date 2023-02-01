"""
This module provides the same interface as the older, non-tag version of datamodels
for the whole asdf file. It will start very basic, initially only to support running
of the flat field step, but many other methods and capabilities will be added to
keep consistency with the JWST data model version.

It is to be subclassed by the various types of data model variants for products
"""
import builtins
import copy
import datetime
import json
import os
import os.path
import sys
from collections import OrderedDict
from collections.abc import Sequence
from pathlib import PurePath

import asdf
import numpy as np
from asdf import AsdfFile
from asdf.fits_embed import AsdfInFits
from astropy.time import Time

from . import stnode, validate
from .extensions import DATAMODEL_EXTENSIONS

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
    "SuperbiasRefModel",
    "SaturationRefModel",
    "WfiImgPhotomRefModel",
    "open",
]


class DataModel:
    """Base class for all top level datamodels"""

    crds_observatory = "roman"

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
        if model_registry[topnode.__class__] != self.__class__:
            return False
        return True

    @property
    def schema_uri(self):
        # Determine the schema corresponding to this model's tag
        schema_uri = next(t for t in DATAMODEL_EXTENSIONS[0].tags if t.tag_uri == self._instance._tag).schema_uri
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
        if isinstance(init, str):
            asdffile = asdf.open(init)
        else:
            asdffile = asdf.AsdfFile(init)
        return asdffile

    def to_asdf(self, init, *args, **kwargs):
        # self.on_save(init)

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


class ImageModel(DataModel):
    def __delattr__(self, attr):
        try:
            print("Deleting attribute: %s" % attr)
            del self._instance[attr]
        except KeyError:
            print("Already deleted this attribute!")

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


class ScienceRawModel(DataModel):
    pass


class RampModel(DataModel):
    pass


class RampFitOutputModel(DataModel):
    pass


class GuidewindowModel(DataModel):
    pass


class ModelContainer(Sequence):
    """
    A container for holding DataModels.

    This functions like a list for holding DataModel objects.  It can be
    iterated through like a list, DataModels within the container can be
    addressed by index, and the datamodels can be grouped into a list of
    lists for grouped looping, useful for NIRCam where grouping together
    all detectors of a given exposure is useful for some pipeline steps.

    Parameters
    ----------
    init : file path, list of DataModels, or None

        - file path: initialize from an association table

        - list: a list of DataModels of any type

        - None: initializes an empty `ModelContainer` instance, to which
          DataModels can be added via the ``append()`` method.

    asn_exptypes: str
        list of exposure types from the asn file to read
        into the ModelContainer, if None read all the given files.

    asn_n_members : int
        Open only the first N qualifying members.

    iscopy : bool
        Presume this model is a copy. Members will not be closed
        when the model is closed/garbage-collected.

    Examples
    --------
    >>> container = ModelContainer('example_asn.json')
    >>> for model in container:
    ...     print(model.meta.filename)

    Say the association was a NIRCam dithered dataset. The `models_grouped`
    attribute is a list of lists, the first index giving the list of exposure
    groups, with the second giving the individual datamodels representing
    each detector in the exposure (2 or 8 in the case of NIRCam).

    >>> total_exposure_time = 0.0
    >>> for group in container.models_grouped:
    ...     total_exposure_time += group[0].meta.exposure.exposure_time

    >>> c = ModelContainer()
    >>> m = datamodels.open('myfile.fits')
    >>> c.append(m)

    Notes
    -----
        The optional parameters ``save_open`` and ``return_open`` can be
        provided to control how the `DataModel` are used by the
        :py:class:`ModelContainer`. If ``save_open`` is set to `False`, each input
        `DataModel` instance in ``init`` will be written out to disk and
        closed, then only the filename for the `DataModel` will be used to
        initialize the :py:class:`ModelContainer` object.
        Subsequent access of each member will then open the `DataModel` file to
        work with it. If ``return_open`` is also `False`, then the `DataModel`
        will be closed when access to the `DataModel` is completed. The use of
        these parameters can minimize the amount of memory used by this object
        during processing, with these parameters being used
        by :py:class:`~jwst.outlier_detection.OutlierDetectionStep`.

        When ASN table's members contain attributes listed in
        :py:data:`RECOGNIZED_MEMBER_FIELDS`, :py:class:`ModelContainer` will
        read those attribute values and update the corresponding attributes
        in the ``meta`` of input models.

        .. code-block::
            :caption: Example of ASN table with additional model attributes \
to supply custom catalogs.

            "products": [
                {
                    "name": "resampled_image",
                    "members": [
                        {
                            "expname": "input_image1_cal.fits",
                            "exptype": "science",
                            "tweakreg_catalog": "custom_catalog1.ecsv"
                        },
                        {
                            "expname": "input_image2_cal.fits",
                            "exptype": "science",
                            "tweakreg_catalog": "custom_catalog2.ecsv"
                        }
                    ]
                }
            ]

        .. warning::
            Input files will be updated in-place with new ``meta`` attribute
            values when ASN table's members contain additional attributes.

    """

    def __init__(self, init=None, asn_schema=None, asn_file_path=None, model_file_path=None, iscopy=False, **kwargs):

        self._models = []
        self._iscopy = iscopy
        self._memmap = kwargs.get("memmap", False)
        self._return_open = kwargs.get("return_open", True)
        self._save_open = kwargs.get("save_open", True)

        if init is None:
            # don't populate container
            pass
        elif asn_file_path:
            with builtins.open(asn_file_path, "r") as asn_file:
                asn_schema = json.load(asn_file)

            for product in asn_schema["products"]:
                for member in product["members"]:
                    if self._iscopy:
                        member_model = open(model_file_path + member["expname"])
                    else:
                        member_model = "null"

                    self._models.append(member_model)
        elif isinstance(init, list):
            # only append list items to self._models if all items are either
            # strings (i.e. path to an ASDF file) or instances of DataModel
            is_all_string = all(isinstance(x, str) for x in init)
            is_all_roman_datamodels = all(isinstance(x, DataModel) for x in init)

            if is_all_string or is_all_roman_datamodels:
                self._models.extend(init)
            else:
                raise TypeError("Input must be a list of strings (full path to ASDF files) or Roman datamodels.")
        elif isinstance(init, self.__class__):
            instance = copy.deepcopy(init._instance)
            self._schema = init._schema
            self._shape = init._shape
            self._asdf = AsdfFile(instance)
            self._instance = instance
            self._ctx = self
            self._models = init._models
            self._iscopy = True
        else:
            raise TypeError(
                "Input must be an ASN filepath or list of either strings (full path to ASDF files) or Roman datamodels."
            )

    def __len__(self):
        return len(self._models)

    def __getitem__(self, index):
        m = self._models[index]
        if not isinstance(m, DataModel) and self._return_open:
            m = open(m, memmap=self._memmap)
        return m

    def __setitem__(self, index, model):
        self._models[index] = model

    def __delitem__(self, index):
        del self._models[index]

    def __iter__(self):
        for model in self._models:
            if not isinstance(model, DataModel) and self._return_open:
                model = open(model, memmap=self._memmap)
            yield model

    def insert(self, index, model):
        self._models.insert(index, model)

    def append(self, model):
        self._models.append(model)

    def extend(self, model):
        self._models.extend(model)

    @property
    def models_grouped(self):
        """
        Returns a list of a list of datamodels grouped by exposure.
        Assign an ID grouping by exposure.

        Data from different detectors of the same exposure will have the
        same group id, which allows grouping by exposure.  The following
        metadata is used for grouping:

        meta.observation.program
        meta.observation.observation
        meta.observation.visit
        meta.observation.visit_file_group
        meta.observation.visit_file_sequence
        meta.observation.visit_file_activity
        meta.observation.exposure
        """
        unique_exposure_parameters = [
            "program",
            "observation",
            "visit",
            "visit_file_group",
            "visit_file_sequence",
            "visit_file_activity",
            "exposure",
        ]

        group_dict = OrderedDict()
        for i, model in enumerate(self._models):
            params = []

            model = model if isinstance(model, DataModel) else open(model)

            if not self._save_open:
                model = open(model, memmap=self._memmap)

            for param in unique_exposure_parameters:
                params.append(str(getattr(model.meta.observation, param)))
            try:
                group_id = "roman" + "_".join(["".join(params[:3]), "".join(params[3:6]), params[6]])
                model.meta["group_id"] = group_id
            except TypeError:
                model.meta["group_id"] = f"exposure{i + 1:04d}"

            group_id = model.meta.group_id
            if not self._save_open and not self._return_open:
                model.close()
                model = self._models[i]

            if group_id in group_dict:
                group_dict[group_id].append(model)
            else:
                group_dict[group_id] = [model]

        return group_dict.values()


class FlatRefModel(DataModel):
    pass


class DarkRefModel(DataModel):
    pass


class DistortionRefModel(DataModel):
    pass


class GainRefModel(DataModel):
    pass


class IpcRefModel(DataModel):
    pass


class LinearityRefModel(DataModel):
    def get_primary_array_name(self):
        """
        Returns the name "primary" array for this model, which
        controls the size of other arrays that are implicitly created.
        This is intended to be overridden in the subclasses if the
        primary array's name is not "data".
        """
        return "coeffs"


class MaskRefModel(DataModel):
    def get_primary_array_name(self):
        """
        Returns the name "primary" array for this model, which
        controls the size of other arrays that are implicitly created.
        This is intended to be overridden in the subclasses if the
        primary array's name is not "data".
        """
        return "dq"


class PixelareaRefModel(DataModel):
    pass


class ReadnoiseRefModel(DataModel):
    pass


class SuperbiasRefModel(DataModel):
    pass


class SaturationRefModel(DataModel):
    pass


class WfiImgPhotomRefModel(DataModel):
    pass


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
        except ValueError:
            raise TypeError("Open requires a filepath, file-like object, or Roman datamodel")
        if isinstance(asdffile, AsdfInFits):
            raise TypeError("Roman datamodels does not accept FITS files or objects")
    modeltype = type(asdffile.tree["roman"])
    if modeltype in model_registry:
        rmodel = model_registry[modeltype](asdffile, **kwargs)
        if target is not None:
            if not issubclass(rmodel.__class__, target):
                raise ValueError("Referenced ASDF file model type is not subclass of target")
        else:
            return rmodel
    else:
        return DataModel(asdffile, **kwargs)


model_registry = {
    stnode.WfiImage: ImageModel,
    stnode.WfiScienceRaw: ScienceRawModel,
    stnode.Ramp: RampModel,
    stnode.RampFitOutput: RampFitOutputModel,
    stnode.Guidewindow: GuidewindowModel,
    stnode.FlatRef: FlatRefModel,
    stnode.DarkRef: DarkRefModel,
    stnode.DistortionRef: DistortionRefModel,
    stnode.GainRef: GainRefModel,
    stnode.IpcRef: IpcRefModel,
    stnode.LinearityRef: LinearityRefModel,
    stnode.MaskRef: MaskRefModel,
    stnode.PixelareaRef: PixelareaRefModel,
    stnode.ReadnoiseRef: ReadnoiseRefModel,
    stnode.SaturationRef: SaturationRefModel,
    stnode.SuperbiasRef: SuperbiasRefModel,
    stnode.WfiImgPhotomRef: WfiImgPhotomRefModel,
}
