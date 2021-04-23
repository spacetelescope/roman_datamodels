"""
Various utility functions and data types
"""

import os
from platform import system as platform_system
import psutil
import traceback
from pydoc import locate

#from . import s3_utils
#from .basic_utils import bytes2human
from .extensions import DATAMODEL_EXTENSIONS

import logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


def bytes2human(n):
    """Convert bytes to human-readable format

    Taken from the `psutil` library which references
    http://code.activestate.com/recipes/578019

    Parameters
    ----------
    n : int
        Number to convert

    Returns
    -------
    readable : str
        A string with units attached.

    Examples
    --------
    >>> bytes2human(10000)
        '9.8K'

    >>> bytes2human(100001221)
        '95.4M'
    """
    symbols = ('K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
    prefix = {}
    for i, s in enumerate(symbols):
        prefix[s] = 1 << (i + 1) * 10
    for s in reversed(symbols):
        if n >= prefix[s]:
            value = float(n) / prefix[s]
            return '%.1f%s' % (value, s)
    return "%sB" % n


class NoTypeWarning(Warning):
    pass


def get_schema_uri_from_converter(converter_class):
    """
    Given a converter class, return the schema_uri corresponding to the tag.
    """
    # Obtain one of the possible objects the converter returns
    classname = converter_class.types[0]
    # Presume these are from the same directory tree
    rclass = locate(classname)
    tag = rclass._tag
    schema_uri = next(
        t for t in DATAMODEL_EXTENSIONS[0].tags if t._tag_uri == tag)._schema_uri
    return schema_uri

# def open(init=None, memmap=False, **kwargs):
#     """
#     Creates a DataModel from a number of different types

#     Parameters
#     ----------
#     init : shape tuple, file path, file object, astropy.io.fits.HDUList,
#            numpy array, dict, None

#         - None: A default data model with no shape

#         - shape tuple: Initialize with empty data of the given shape

#         - file path: Initialize from the given file (FITS , JSON or ASDF)

#         - readable file object: Initialize from the given file object

#         - astropy.io.fits.HDUList: Initialize from the given
#           `~astropy.io.fits.HDUList`

#         - A numpy array: A new model with the data array initialized
#           to what was passed in.

#         - dict: The object model tree for the data model

#     memmap : bool
#         Turn memmap of FITS file on or off.  (default: False).  Ignored for
#         ASDF files.

#     kwargs : dict
#         Additional keyword arguments passed to lower level functions. These arguments
#         are generally file format-specific. Arguments of note are:

#         - FITS

#            skip_fits_update - bool or None
#               `True` to skip updating the ASDF tree from the FITS headers, if possible.
#               If `None`, value will be taken from the environmental SKIP_FITS_UPDATE.
#               Otherwise, the default value is `True`.

#     Returns
#     -------
#     model : DataModel instance
#     """

#     from . import datamodels as dm
#     from . import filetype

#     # Initialize variables used to select model class

#     shape = ()
#     file_name = None
#     file_to_close = None

#     # Get special cases for opening a model out of the way
#     # all special cases return a model if they match

#     if init is None:
#         return dm.DataModel(None)

#     elif isinstance(init, dm.DataModel):
#         # Copy the object so it knows not to close here
#         return init.__class__(init)

#     elif isinstance(init, (str, bytes)) or hasattr(init, "read"):
#         # If given a string, presume its a file path.
#         # if it has a read method, assume a file descriptor

#         if isinstance(init, bytes):
#             init = init.decode(sys.getfilesystemencoding())

#         file_name = basename(init)
#         file_type = filetype.check(init)

#         elif file_type == "asn":
#             raise NotImplementedError("roman_datamodels does not yet support associations")
#             # Read the file as an association / model container
#             # from . import container
#             # return container.ModelContainer(init, **kwargs)

#         elif file_type == "asdf":
#             # Read the file as asdf, no need for a special class
#             return dm.DataModel(init, **kwargs)

#     elif isinstance(init, tuple):
#         for item in init:
#             if not isinstance(item, int):
#                 raise ValueError("shape must be a tuple of ints")
#         shape = init

#     elif isinstance(init, np.ndarray):
#         shape = init.shape

#     elif is_association(init) or isinstance(init, list):
#         raise NotImplementedError("stdatamodels does not yet support associations")
#         # from . import container
#         # return container.ModelContainer(init, **kwargs)

#     # Log a message about how the model was opened
#     if file_name:
#         log.debug(f'Opening {file_name} as {new_class}')
#     else:
#         log.debug(f'Opening as {new_class}')

#     # Actually open the model
#     model = new_class(init, **kwargs)

#     return model


def _class_from_model_type(hdulist):
    """
    Get the model type from the primary header, lookup to get class
    """
    raise NotImplementedError(
        "stdatamodels does not yet support automatic model class selection")
    # from . import _defined_models as defined_models

    # if hdulist:
    #     primary = hdulist[0]
    #     model_type = primary.header.get('DATAMODL')

    #     if model_type is None:
    #         new_class = None
    #     else:
    #         new_class = defined_models.get(model_type)
    # else:
    #     new_class = None

    # return new_class


def _class_from_ramp_type(hdulist, shape):
    """
    Special check to see if file is ramp file
    """
    raise NotImplementedError(
        "stdatamodels does not yet support automatic model class selection")
    # if not hdulist:
    #     new_class = None
    # else:
    #     if len(shape) == 4:
    #         try:
    #             hdulist['DQ']
    #         except KeyError:
    #             from . import ramp
    #             new_class = ramp.RampModel
    #         else:
    #             new_class = None
    #     else:
    #         new_class = None

    # return new_class


def _class_from_reftype(hdulist, shape):
    """
    Get the class name from the reftype and other header keywords
    """
    raise NotImplementedError(
        "stdatamodels does not yet support automatic model class selection")
    # if not hdulist:
    #     new_class = None

    # else:
    #     primary = hdulist[0]
    #     reftype = primary.header.get('REFTYPE')
    #     if reftype is None:
    #         new_class = None

    #     else:
    #         from . import reference
    #         if len(shape) == 0:
    #             new_class = reference.ReferenceFileModel
    #         elif len(shape) == 2:
    #             new_class = reference.ReferenceImageModel
    #         elif len(shape) == 3:
    #             new_class = reference.ReferenceCubeModel
    #         elif len(shape) == 4:
    #             new_class = reference.ReferenceQuadModel
    #         else:
    #             new_class = None

    # return new_class


def _class_from_shape(hdulist, shape):
    """
    Get the class name from the shape
    """
    raise NotImplementedError(
        "stdatamodels does not yet support automatic model class selection")
    # if len(shape) == 0:
    #     from . import model_base
    #     new_class = model_base.DataModel
    # elif len(shape) == 4:
    #     from . import quad
    #     new_class = quad.QuadModel
    # elif len(shape) == 3:
    #     from . import cube
    #     new_class = cube.CubeModel
    # elif len(shape) == 2:
    #     try:
    #         hdulist[('SCI', 2)]
    #     except (KeyError, NameError):
    #         # It's an ImageModel
    #         from . import image
    #         new_class = image.ImageModel
    #     else:
    #         # It's a MultiSlitModel
    #         from . import multislit
    #         new_class = multislit.MultiSlitModel
    # else:
    #     new_class = None

    # return new_class


def can_broadcast(a, b):
    """
    Given two shapes, returns True if they are broadcastable.
    """
    for i in range(1, min(len(a), len(b)) + 1):
        adim = a[-i]
        bdim = b[-i]

        if not (adim == 1 or bdim == 1 or adim == bdim):
            return False

    return True


def to_camelcase(token):
    return ''.join(x.capitalize() for x in token.split('_-'))


def is_association(asn_data):
    """
    Test if an object is an association by checking for required fields
    """
    if isinstance(asn_data, dict):
        if 'asn_id' in asn_data and 'asn_pool' in asn_data:
            return True
    return False


def get_short_doc(schema):
    title = schema.get('title', None)
    description = schema.get('description', None)
    if description is None:
        description = title or ''
    else:
        if title is not None:
            description = title + '\n\n' + description
    return description.partition('\n')[0]


def ensure_ascii(s):
    if isinstance(s, bytes):
        s = s.decode('ascii')
    return s


def create_history_entry(description, software=None):
    """
    Create a HistoryEntry object.

    Parameters
    ----------
    description : str
        Description of the change.
    software : dict or list of dict
        A description of the software used.  It should not include
        asdf itself, as that is automatically notated in the
        `asdf_library` entry.

        Each dict must have the following keys:

        ``name``: The name of the software
        ``author``: The author or institution that produced the software
        ``homepage``: A URI to the homepage of the software
        ``version``: The version of the software

    Examples
    --------
    >>> soft = {'name': 'jwreftools', 'author': 'STSCI', \
                'homepage': 'https://github.com/spacetelescope/jwreftools', 'version': "0.7"}
    >>> entry = create_history_entry(description="HISTORY of this file", software=soft)

    """
    from asdf.tags.core import Software, HistoryEntry
    import datetime

    if isinstance(software, list):
        software = [Software(x) for x in software]
    elif software is not None:
        software = Software(software)

    entry = HistoryEntry({
        'description': description,
        'time': datetime.datetime.utcnow()
    })

    if software is not None:
        entry['software'] = software
    return entry


def get_envar_as_boolean(name, default=False):
    """Interpret an environmental as a boolean flag

    Truth is any numeric value that is not 0 or
    any of the following case-insensitive strings:

    ('true', 't', 'yes', 'y')

    Parameters
    ----------
    name : str
        The name of the environmental variable to retrieve

    default : bool
        If the environmental variable cannot be accessed, use as the default.
    """
    truths = ('true', 't', 'yes', 'y')
    falses = ('false', 'f', 'no', 'n')
    if name in os.environ:
        value = os.environ[name]
        try:
            value = bool(int(value))
        except ValueError:
            value_lowcase = value.lower()
            if value_lowcase not in truths + falses:
                raise ValueError(
                    f'Cannot convert value "{value}" to boolean unambiguously.')
            return value_lowcase in truths
        return value

    log.debug(
        f'Environmental "{name}" cannot be found. Using default value of "{default}".')
    return default


def check_memory_allocation(shape, allowed=None, model_type=None, include_swap=True):
    """Check if a DataModel can be instantiated

    Parameters
    ----------
    shape : tuple
        The desired shape of the model.

    allowed : number or None
        Fraction of memory allowed to be allocated.
        If None, the environmental variable `DMODEL_ALLOWED_MEMORY`
        is retrieved. If undefined, then no check is performed.
        `1.0` would be all available memory. `0.5` would be half available memory.

    model_type : DataModel or None
        The desired model to instantiate.
        If None, `open` will be used to guess at a model type depending on shape.

    include_swap : bool
        Include available swap in the calculation.

    Returns
    -------
    can_instantiate, required_memory : bool, number
        True if the model can be instantiated and the predicted memory footprint.
    """
    # Determine desired allowed amount.
    if allowed is None:
        allowed = os.environ.get('DMODEL_ALLOWED_MEMORY', None)
        if allowed is not None:
            allowed = float(allowed)

    # Create the unit shape
    unit_shape = (1,) * len(shape)

    # Create the unit model.
    if model_type:
        unit_model = model_type(unit_shape)
    else:
        unit_model = open(unit_shape)

    # Size of the primary array.
    primary_array_name = unit_model.get_primary_array_name()
    primary_array = getattr(unit_model, primary_array_name)
    size = primary_array.nbytes
    for dimension in shape:
        size *= dimension

    # Get available memory
    available = get_available_memory(include_swap=include_swap)
    log.debug(
        f'Model size {bytes2human(size)} available system memory {bytes2human(available)}')

    if size > available:
        log.warning(
            f'Model {model_type} shape {shape} requires {bytes2human(size)} which is more than'
            f' system available {bytes2human(available)}'
        )

    if allowed and size > (allowed * available):
        log.debug(
            f'Model size greater than allowed memory {bytes2human(allowed * available)}'
        )
        return False, size

    return True, size


def get_available_memory(include_swap=True):
    """Retrieve available memory

    Parameters
    ----------
    include_swap : bool
        Include available swap in the calculation.

    Returns
    -------
    available : number
        The amount available.
    """
    system = platform_system()

    # Apple MacOS
    log.debug(f'Running OS is "{system}"')
    if system in ['Darwin']:
        return get_available_memory_darwin(include_swap=include_swap)

    # Default to Linux-like:
    return get_available_memory_linux(include_swap=include_swap)


def get_available_memory_linux(include_swap=True):
    """Get memory for a Linux system

    Presume that the swap space as reported is accurate at the time of
    the query and that any subsequent allocation will be held the value.

    Parameters
    ----------
    include_swap : bool
        Include available swap in the calculation.

    Returns
    -------
    available : number
        The amount available.
    """
    vm_stats = psutil.virtual_memory()
    available = vm_stats.available
    if include_swap:
        swap = psutil.swap_memory()
        available += swap.total
    return available


def get_available_memory_darwin(include_swap=True):
    """Get the available memory on an Apple MacOS-like system

    For Darwin, swap space is dynamic and will attempt to use the whole of the
    boot partition.

    If the system has been configured to use swap from other sources besides
    the boot partition, that available space will not be included.

    Parameters
    ----------
    include_swap : bool
        Include available swap in the calculation.

    Returns
    -------
    available : number
        The amount available.
    """
    vm_stats = psutil.virtual_memory()
    available = vm_stats.available
    if include_swap:

        # Attempt to determine amount of free disk space on the boot partition.
        try:
            swap = psutil.disk_usage('/private/var/vm').free
        except FileNotFoundError as exception:
            log.warn('Cannot determine available swap space.'
                     f'Reason:\n'
                     f'{"".join(traceback.format_exception(exception))}')
            swap = 0
        available += swap

    return available
