"""
Utility file containing random value generation routines.
"""

import string
import warnings
from datetime import datetime

import numpy as np
from astropy import units as u
from astropy.time import Time
from erfa.core import ErfaWarning

_HEX_ALPHABET = np.array(list(string.hexdigits))


def generate_float(min=None, max=None, seed=None):
    # Assume 32-bit range for now, 64-bit range tends to overflow
    if min is None:
        min = -1e38
    if max is None:
        max = 1e38

    return np.random.default_rng(seed).uniform(low=min, high=max)


def generate_positive_float(max=None, seed=None):
    return generate_float(min=0.0, max=max, seed=seed)


def generate_angle_radians(seed=None):
    return generate_float(0.0, 2.0 * np.pi, seed=seed)


def generate_angle_degrees(seed=None):
    return generate_float(0.0, 360.0, seed=seed)


def generate_mjd_timestamp(seed=None):
    # Random timestamp between 2020-01-01 and 2030-01-01
    return generate_float(58849.0, 62502.0, seed=seed)


def generate_utc_timestamp(seed=None):
    # Random timestamp between 2020-01-01 and 2030-01-01
    return generate_float(1577836800.0, 1893456000.0, seed=seed)


def generate_string_timestamp(seed=None):
    return datetime.utcfromtimestamp(generate_utc_timestamp(seed=seed)).strftime("%Y-%m-%dT%H:%M:%S.%f")[0:23]


def generate_string_date(seed=None):
    return datetime.utcfromtimestamp(generate_utc_timestamp(seed=seed)).strftime("%Y-%m-%d")


def generate_string_time(seed=None):
    return datetime.utcfromtimestamp(generate_utc_timestamp(seed=seed)).strftime("%H:%M:%S.%f")[0:12]


def generate_astropy_time(time_format="unix", ignore_erfa_warnings=True, seed=None):
    def _gen_time():
        timeobj = Time(generate_utc_timestamp(seed=seed), format="unix")

        if time_format == "unix":
            return timeobj
        else:
            time_str = timeobj.to_value(format=time_format)
            timeobj = Time(time_str, format=time_format)
            return timeobj

    if ignore_erfa_warnings:
        # catch and ignore erfa warnings:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", ErfaWarning)
            return _gen_time()
    else:
        return _gen_time()


def generate_int(min=None, max=None, size=None, seed=None):
    # Assume 32-bit signed integers for now
    if min is None:
        min = -1 * 2**31
    if max is None:
        max = 2**31 - 1

    return np.random.default_rng(seed).integers(low=min, high=max, size=size, dtype=int)


def generate_positive_int(max=None, size=None, seed=None):
    return generate_int(0, max, size=size, seed=seed)


def generate_choice(*args, seed=None):
    if len(args) == 1:
        args = args[0]

    index = generate_positive_int(max=len(args) - 1, seed=seed)
    return args[index]


def generate_choices(*args, seed=None, k=1, **kwargs):
    if len(args) == 1:
        args = args[0]

    indices = generate_positive_int(max=len(args) - 1, size=k, seed=seed).tolist()
    return [args[i] for i in indices]


def generate_string(prefix="", max_length=None, seed=None):
    if max_length is not None:
        size = 2 * min(16, max_length - len(prefix))
    else:
        size = 2 * 16

    if size > 0:
        suffix = str(np.random.default_rng(seed).choice(_HEX_ALPHABET, size=size).view(f"U{size}")[0])
    else:
        suffix = ""

    return prefix + suffix


def generate_bool(seed=None):
    return bool(generate_choice(*[True, False], seed=seed))


def generate_array_float32(size=(4096, 4096), min=None, max=None, units=None, seed=None):
    if min is None:
        min = np.finfo("float32").min
    if max is None:
        max = np.finfo("float32").max

    array = np.random.default_rng(seed).uniform(low=min, high=max, size=size).astype(np.float32)
    if units:
        array = u.Quantity(array, units, dtype=np.float32)
    return array


def generate_array_float64(size=(4096, 4096), min=None, max=None, units=None, seed=None):
    if min is None:
        min = np.finfo("float32").min
    if max is None:
        max = np.finfo("float32").max

    array = np.random.default_rng(seed).uniform(low=min, high=max, size=size).astype(np.float64)
    if units:
        array = u.Quantity(array, units, dtype=np.float64)
    return array


def generate_array_complex128(size=(32, 286721), min=None, max=None, shape=None, seed=None):
    """
    Uniformly at random generate a complex array of the specified size.

    Parameters
    ----------
    size: tuple
        The size of the array to generate.

    min: tuple (or None)
        Min value for the sample axis.
            - If None and shape is "square", then (-1.0, -1.0).
            - If None and shape is "disk", then (0.0, -pi).

    max: tuple (or None)
        Max value for the sample axis.
            - If None and shape is "square", then (1.0, 1.0).
            - If None and shape is "disk", then (1.0, pi).

    shape: str
        The type of sampling to use.  Options are:
            - "square": Sample uniformly from a square.
            - "disk": Sample uniformly from a disk.
    """
    shape = "square" if shape is None else shape

    if shape not in ["square", "disk"]:
        raise ValueError(f"Invalid shape: {shape}")

    if min is None:
        if shape == "square":
            min = (-1.0, -1.0)
        elif shape == "disk":
            min = (0.0, -np.pi)

    if max is None:
        if shape == "square":
            max = (1.0, 1.0)
        elif shape == "disk":
            max = (1.0, np.pi)

    if len(min) != 2:
        raise ValueError(f"Invalid min: {min}")

    if len(max) != 2:
        raise ValueError(f"Invalid max: {max}")

    rng = np.random.default_rng(seed)
    if shape == "square":
        # Generate two arrays of random numbers, one for the real part and one for the imaginary part.
        x = rng.uniform(min[0], max[0], size=size)
        y = rng.uniform(min[1], max[1], size=size)

        return (x + 1.0j * y).astype(np.complex128)

    elif shape == "disk":
        # Generate two arrays of random numbers, one for the radius and one for the angle.
        r = rng.uniform(min[0], max[0], size=size)
        theta = rng.uniform(min[1], max[1], size=size)

        return (r * np.exp(1.0j * theta)).astype(np.complex128)


def generate_array_uint8(size=(4096, 4096), min=None, max=None, units=None, seed=None):
    if min is None:
        min = np.iinfo("uint8").min
    if max is None:
        max = np.iinfo("uint8").max
    array = np.random.default_rng(seed).integers(low=min, high=max, size=size, dtype=np.uint8)
    if units:
        array = u.Quantity(array, units, dtype=np.uint8)
    return array


def generate_array_uint16(size=(4096, 4096), min=None, max=None, units=None, seed=None):
    if min is None:
        min = np.iinfo("uint16").min
    if max is None:
        max = np.iinfo("uint16").max
    array = np.random.default_rng(seed).integers(min, high=max, size=size, dtype=np.uint16)
    if units:
        array = u.Quantity(array, units, dtype=np.uint16)
    return array


def generate_array_uint32(size=(4096, 4096), min=None, max=None, units=None, seed=None):
    if min is None:
        min = np.iinfo("uint32").min
    if max is None:
        max = np.iinfo("uint32").max
    array = np.random.default_rng(seed).integers(min, high=max, size=size, dtype=np.uint32)
    if units:
        array = u.Quantity(array, units, dtype=np.uint32)
    return array


def generate_exposure_type(seed=None):
    return generate_choice(
        "WFI_DARK",
        "WFI_FLAT",
        "WFI_GRISM",
        "WFI_IMAGE",
        "WFI_PRISM",
        "WFI_WFSC",
        seed=seed,
    )


def generate_detector(seed=None):
    return generate_choice(
        "WFI01",
        "WFI02",
        "WFI03",
        "WFI04",
        "WFI05",
        "WFI06",
        "WFI07",
        "WFI08",
        "WFI09",
        "WFI10",
        "WFI11",
        "WFI12",
        "WFI13",
        "WFI14",
        "WFI15",
        "WFI16",
        "WFI17",
        "WFI18",
        seed=seed,
    )


def generate_optical_element(seed=None):
    return generate_choice(
        "F062",
        "F087",
        "F106",
        "F129",
        "F146",
        "F158",
        "F184",
        "F213",
        "GRISM",
        "PRISM",
        "DARK",
        seed=seed,
    )


def generate_software_version(seed=None):
    vals = generate_positive_int(100, size=3, seed=seed)
    return f"{vals[0]}.{vals[1]}.{vals[2]}"
