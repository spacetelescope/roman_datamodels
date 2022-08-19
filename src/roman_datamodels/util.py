"""
Various utility functions and data types
"""

import logging
import os
import traceback
from platform import system as platform_system
from pydoc import locate

import psutil

# from . import s3_utils
# from .basic_utils import bytes2human
from .extensions import DATAMODEL_EXTENSIONS

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
    symbols = ("K", "M", "G", "T", "P", "E", "Z", "Y")
    prefix = {}
    for i, s in enumerate(symbols):
        prefix[s] = 1 << (i + 1) * 10
    for s in reversed(symbols):
        if n >= prefix[s]:
            value = float(n) / prefix[s]
            return f"{value:.1f}{s}"
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
        t for t in DATAMODEL_EXTENSIONS[0].tags if t.tag_uri == tag
    ).schema_uris[0]
    return schema_uri


def _class_from_model_type(hdulist):
    """
    Get the model type from the primary header, lookup to get class
    """
    raise NotImplementedError(
        "stdatamodels does not yet support automatic model class selection"
    )


def _class_from_ramp_type(hdulist, shape):
    """
    Special check to see if file is ramp file
    """
    raise NotImplementedError(
        "stdatamodels does not yet support automatic model class selection"
    )


def _class_from_reftype(hdulist, shape):
    """
    Get the class name from the reftype and other header keywords
    """
    raise NotImplementedError(
        "stdatamodels does not yet support automatic model class selection"
    )


def _class_from_shape(hdulist, shape):
    """
    Get the class name from the shape
    """
    raise NotImplementedError(
        "stdatamodels does not yet support automatic model class selection"
    )


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
    return "".join(x.capitalize() for x in token.split("_-"))


def is_association(asn_data):
    """
    Test if an object is an association by checking for required fields
    """
    if isinstance(asn_data, dict):
        if "asn_id" in asn_data and "asn_pool" in asn_data:
            return True
    return False


def get_short_doc(schema):
    title = schema.get("title", None)
    description = schema.get("description", None)
    if description is None:
        description = title or ""
    else:
        if title is not None:
            description = title + "\n\n" + description
    return description.partition("\n")[0]


def ensure_ascii(s):
    if isinstance(s, bytes):
        s = s.decode("ascii")
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
                'homepage': 'https://github.com/spacetelescope/jwreftools',
                'version': "0.7"}
    >>> entry = create_history_entry(description="HISTORY of this file", software=soft)

    """
    import datetime

    from asdf.tags.core import HistoryEntry, Software

    if isinstance(software, list):
        software = [Software(x) for x in software]
    elif software is not None:
        software = Software(software)

    entry = HistoryEntry(
        {"description": description, "time": datetime.datetime.utcnow()}
    )

    if software is not None:
        entry["software"] = software
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
    truths = ("true", "t", "yes", "y")
    falses = ("false", "f", "no", "n")
    if name in os.environ:
        value = os.environ[name]
        try:
            value = bool(int(value))
        except ValueError:
            value_lowcase = value.lower()
            if value_lowcase not in truths + falses:
                raise ValueError(
                    f'Cannot convert value "{value}" to boolean unambiguously.'
                )
            return value_lowcase in truths
        return value

    log.debug(
        f'Environmental "{name}" cannot be found. Using default value of "{default}".'
    )
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
        allowed = os.environ.get("DMODEL_ALLOWED_MEMORY", None)
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
        f"Model size {bytes2human(size)} available system memory"
        f"{bytes2human(available)}"
    )

    if size > available:
        log.warning(
            f"Model {model_type} shape {shape} requires {bytes2human(size)}"
            f" which is more than system available {bytes2human(available)}"
        )

    if allowed and size > (allowed * available):
        log.debug(
            f"Model size greater than allowed memory {bytes2human(allowed * available)}"
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
    if system in ["Darwin"]:
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
            swap = psutil.disk_usage("/private/var/vm").free
        except FileNotFoundError as exception:
            log.warn(
                "Cannot determine available swap space."
                f"Reason:\n"
                f'{"".join(traceback.format_exception(exception))}'
            )
            swap = 0
        available += swap

    return available
