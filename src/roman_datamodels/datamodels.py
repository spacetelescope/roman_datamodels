"""
This module provides the same interface as the older, non-tag version of datamodels
for the whole asdf file. It will start very basic, initially only to support running
of the flat field step, but many other methods and capabilities will be added to
keep consistency with the JWST data model version.

It is to be subclassed by the various types of data model variants for products
"""

import contextlib
import copy
import datetime
import logging
import os
import os.path as op
import re
import sys
import warnings
from collections import OrderedDict
from collections.abc import Iterable
from pathlib import Path, PurePath

import asdf
import numpy as np
import packaging.version
from astropy.time import Time

from . import stnode, validate
from .extensions import DATAMODEL_EXTENSIONS
from .util import is_association

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
    "SuperbiasRefModel",
    "SaturationRefModel",
    "WfiImgPhotomRefModel",
    "ModelContainer",
    "open",
]

# prevent MRO issues when reading an
# ASN file in a "with open(filename)" block
_builtin_open = open

RECOGNIZED_MEMBER_FIELDS = ["tweakreg_catalog"]

# Configure logging
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


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
        return model_registry[topnode.__class__] == self.__class__

    @property
    def schema_uri(self):
        return next(t for t in DATAMODEL_EXTENSIONS[0].tags if t.tag_uri == self._instance._tag).schema_uri

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
        else:
            target._asdf = source._asdf
            target._instance = source._instance
        target._iscopy = True
        target._files_to_close = []
        target._shape = source._shape
        target._ctx = target

    def save(self, path, dir_path=None, *args, **kwargs):
        if callable(path):
            path_head, path_tail = op.split(path(self.meta.filename))
        else:
            path_head, path_tail = op.split(path)
        base, ext = op.splitext(path_tail)
        if isinstance(ext, bytes):
            ext = ext.decode(sys.getfilesystemencoding())

        if dir_path:
            path_head = dir_path
        output_path = op.join(path_head, path_tail)

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
            return {f"roman.{key}": convert_val(val) for (key, val) in self.items()}
        else:
            return {f"roman.{key}": convert_val(val) for (key, val) in self.items() if not isinstance(val, np.ndarray)}

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

    def info(self, *args, **kwargs):
        return self._asdf.info(*args, **kwargs)

    def search(self, *args, **kwargs):
        return self._asdf.search(*args, **kwargs)

    def schema_info(self, *args, **kwargs):
        return self._asdf.schema_info(*args, **kwargs)


class MosaicModel(DataModel):
    pass


class ImageModel(DataModel):
    pass


class ScienceRawModel(DataModel):
    pass


class RampModel(DataModel):
    pass


class RampFitOutputModel(DataModel):
    pass


class AssociationsModel(DataModel):
    # Need an init to allow instantiation from a JSON file
    pass


class GuidewindowModel(DataModel):
    pass


class ModelContainer(Iterable):
    """
    A container for holding DataModels.

    This functions like a list for holding DataModel objects.  It can be
    iterated through like a list and the datamodels within the container can be
    addressed by index. Additionally, the datamodels can be grouped by exposure.

    Parameters
    ----------
    init : path to an ASN file, list of either DataModels or path to ASDF files, or `None`
        If `None`, then an empty `ModelContainer` instance is initialized, to which
        DataModels can later be added via the ``append()`` method.

    iscopy : bool
        Presume this model is a copy. Members will not be closed
        when the model is closed/garbage-collected.

    memmap : bool
        Open ASDF file binary data using memmap (default: False)

    return_open : bool
        (optional) See notes below on usage.

    save_open : bool
        (optional) See notes below on usage.

    Examples
    --------
    To load a list of ASDF files into a `ModelContainer`:

        >>> container = ModelContainer(
                [
                    "/path/to/file1.asdf",
                    "/path/to/file2.asdf",
                    ...,
                    "/path/to/fileN.asdf"
                ]
            )

    To load a list of open Roman DataModels into a `ModelContainer`:

        >>> import roman_datamodels.datamodels as rdm
        >>> data_list = [
                    "/path/to/file1.asdf",
                    "/path/to/file2.asdf",
                    ...,
                    "/path/to/fileN.asdf"
                ]
        >>> datamodels_list = [rdm.open(x) for x in data_list]
        >>> container = ModelContainer(datamodels_list)

    To load an ASN file into a `ModelContainer`:

        >>> asn_file = "/path/to/asn_file.json"
        >>> container = ModelContainer(asn_file)

    In any of the cases above, the content of each file in a `ModelContainer` can
    be accessed by iterating over its elements. For example, to print out the filename
    of each file, we can run:
        >>> for model in container:
        ...     print(model.meta.filename)


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
        during processing.

        .. warning:: Input files will be updated in-place with new ``meta`` attribute
            values when ASN table's members contain additional attributes.

    """

    def __init__(
        self,
        init=None,
        asn_exptypes=None,
        asn_n_members=None,
        iscopy=False,
        memmap=False,
        return_open=True,
        save_open=True,
    ):
        self._models = []
        self._iscopy = iscopy
        self._memmap = memmap
        self._return_open = return_open
        self._save_open = save_open

        self.asn_exptypes = asn_exptypes
        self.asn_n_members = asn_n_members
        self.asn_table = {}
        self.asn_table_name = None
        self.asn_pool_name = None

        try:
            init = Path(init)
        except TypeError:
            if init is None:
                # don't populate container
                pass
            elif isinstance(init, Iterable):
                # only append list items to self._models if all items are either
                # strings (i.e. path to an ASDF file) or instances of DataModel
                is_all_string = all(isinstance(x, str) for x in init)
                is_all_roman_datamodels = all(isinstance(x, DataModel) for x in init)

                if is_all_string or is_all_roman_datamodels:
                    self._models.extend(init)
                else:
                    raise TypeError("Input must be a list of strings (full path to ASDF files) or Roman datamodels.")
        else:
            if is_association(init):
                self.from_asn(init)
            elif isinstance(init, Path):
                init_from_asn = self.read_asn(init)
                self.from_asn(init_from_asn, asn_file_path=init)
            else:
                raise TypeError("Input must be a list of either strings (full path to ASDF files) or Roman datamodels.")

    def __len__(self):
        return len(self._models)

    def __getitem__(self, index):
        m = self._models[index]
        if not isinstance(m, DataModel) and self._return_open:
            m = open(m, memmap=self._memmap)
        return m

    def __setitem__(self, index, model):
        self._models[index] = model

    def __iter__(self):
        for model in self._models:
            if not isinstance(model, DataModel) and self._return_open:
                model = open(model, memmap=self._memmap)
            yield model

    def close(self):
        if not self._iscopy:
            if self._asdf is not None:
                self._asdf.close()

    @staticmethod
    def read_asn(filepath):
        """
        Load fits files from a Roman association file.

        Parameters
        ----------
        filepath : str
            The path to an association file.
        """
        # Prevent circular import:
        from .associations import AssociationNotValidError, load_asn

        filepath = op.abspath(op.expanduser(op.expandvars(filepath)))
        try:
            with _builtin_open(filepath) as asn_file:
                asn_data = load_asn(asn_file)
        except AssociationNotValidError as e:
            raise OSError("Cannot read ASN file.") from e
        return asn_data

    def from_asn(self, asn_data, asn_file_path=None):
        """
        Load fits files from a Roman association file.

        Parameters
        ----------
        asn_data : ~roman_datamodels.associations.Association
            An association dictionary

        asn_file_path: str
            Filepath of the association, if known.
        """
        # match the asn_exptypes to the exptype in the association and retain
        # only those file that match, as a list, if asn_exptypes is set to none
        # grab all the files
        if self.asn_exptypes:
            infiles = []
            logger.debug(f"Filtering datasets based on allowed exptypes {self.asn_exptypes}:")
            for member in asn_data["products"][0]["members"]:
                if any(x for x in self.asn_exptypes if re.match(member["exptype"], x, re.IGNORECASE)):
                    infiles.append(member)
                    logger.debug(f'Files accepted for processing {member["expname"]}:')
        else:
            infiles = list(asn_data["products"][0]["members"])

        asn_dir = op.dirname(asn_file_path) if asn_file_path else ""
        # Only handle the specified number of members.
        sublist = infiles[: self.asn_n_members] if self.asn_n_members else infiles
        try:
            for member in sublist:
                filepath = op.join(asn_dir, member["expname"])
                update_model = any(attr in member for attr in RECOGNIZED_MEMBER_FIELDS)
                if update_model or self._save_open:
                    m = open(filepath, memmap=self._memmap)
                    m.meta["asn"] = {"exptype": member["exptype"]}
                    for attr, val in member.items():
                        if attr in RECOGNIZED_MEMBER_FIELDS:
                            if attr == "tweakreg_catalog":
                                val = op.join(asn_dir, val) if val.strip() else None
                            setattr(m.meta, attr, val)

                    if not self._save_open:
                        m.save(filepath, overwrite=True)
                        m.close()
                else:
                    m = filepath

                self._models.append(m)

        except OSError:
            self.close()
            raise

        # Pull the whole association table into asn_table
        self.merge_tree(self.asn_table, asn_data)

        if asn_file_path is not None:
            self.asn_table_name = op.basename(asn_file_path)
            self.asn_pool_name = asn_data["asn_pool"]
            for model in self:
                with contextlib.suppress(AttributeError):
                    model.meta.asn["table_name"] = self.asn_table_name
                    model.meta.asn["pool_name"] = self.asn_pool_name

    def save(self, dir_path=None, *args, **kwargs):
        # use current path if dir_path is not provided
        dir_path = dir_path if dir_path is not None else os.getcwd()
        # output filename suffix
        output_suffix = "cal_twkreg"
        for model in self._models:
            filename = model.meta.filename
            base, ext = op.splitext(filename)
            base = base.replace("cal", output_suffix)
            output_filename = "".join([base, ext])
            output_path = op.join(dir_path, output_filename)
            # TODO: Support gzip-compressed fits
            if ext == ".asdf":
                model.to_asdf(output_path, *args, **kwargs)
            else:
                raise ValueError(f"unknown filetype {ext}")

    @property
    def models_grouped(self):
        """
        Returns a list of a list of datamodels grouped by exposure.
        An ID is assigned to each group.

        Data from different detectors of the same exposure will have the
        same group ID, which allows grouping by exposure.  The following
        metadata is used for grouping:

            - `meta.observation.program`;
            - `meta.observation.observation`;
            - `meta.observation.visit`;
            - `meta.observation.visit_file_group`;
            - `meta.observation.visit_file_sequence`;
            - `meta.observation.visit_file_activity`;
            - `meta.observation.exposure`.
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
            model = model if isinstance(model, DataModel) else open(model)

            if not self._save_open:
                model = open(model, memmap=self._memmap)

            params = [str(getattr(model.meta.observation, param)) for param in unique_exposure_parameters]
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

    @property
    def to_association(self):
        pass

    def merge_tree(self, a, b):
        """
        Merge elements from tree `b` into tree `a`.
        """

        def recurse(a, b):
            if isinstance(b, dict):
                if not isinstance(a, dict):
                    return copy.deepcopy(b)
                for key, val in b.items():
                    a[key] = recurse(a.get(key), val)
                return a
            return copy.deepcopy(b)

        recurse(a, b)
        return a

    @property
    def crds_observatory(self):
        """
        Get the CRDS observatory for this container.  Used when selecting
        step/pipeline parameter files when the container is a pipeline input.

        Returns
        -------
        str
        """
        return DataModel().crds_observatory

    @property
    def get_crds_parameters(self):
        """
        Get parameters used by CRDS to select references for this model.

        Returns
        -------
        dict
        """
        return DataModel().get_crds_parameters()


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


class InverseLinearityRefModel(DataModel):
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
        if modeltype in model_registry:
            rmodel = model_registry[modeltype](asdffile, **kwargs)
            if target is not None:
                if not issubclass(rmodel.__class__, target):
                    if file_to_close is not None:
                        file_to_close.close()
                    raise ValueError("Referenced ASDF file model type is not subclass of target")
            else:
                return rmodel
        else:
            return DataModel(asdffile, **kwargs)


model_registry = {
    stnode.WfiMosaic: MosaicModel,
    stnode.WfiImage: ImageModel,
    stnode.WfiScienceRaw: ScienceRawModel,
    stnode.Ramp: RampModel,
    stnode.RampFitOutput: RampFitOutputModel,
    stnode.Associations: AssociationsModel,
    stnode.Guidewindow: GuidewindowModel,
    stnode.FlatRef: FlatRefModel,
    stnode.DarkRef: DarkRefModel,
    stnode.DistortionRef: DistortionRefModel,
    stnode.GainRef: GainRefModel,
    stnode.IpcRef: IpcRefModel,
    stnode.LinearityRef: LinearityRefModel,
    stnode.InverseLinearityRef: InverseLinearityRefModel,
    stnode.MaskRef: MaskRefModel,
    stnode.PixelareaRef: PixelareaRefModel,
    stnode.ReadnoiseRef: ReadnoiseRefModel,
    stnode.SaturationRef: SaturationRefModel,
    stnode.SuperbiasRef: SuperbiasRefModel,
    stnode.WfiImgPhotomRef: WfiImgPhotomRefModel,
}
