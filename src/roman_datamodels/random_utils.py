"""
Utility file containing random value generation routines.
"""

import math
import random
import secrets
import sys
import warnings
from datetime import datetime

import numpy as np
from astropy import units as u
from astropy.time import Time
from erfa.core import ErfaWarning


def generate_float(min=None, max=None):
    if min is None:
        min = sys.float_info.max * -1.0
    if max is None:
        max = sys.float_info.max
    value = random.random()
    return min + max * value - min * value


def generate_positive_float(max=None):
    return generate_float(min=0.0, max=max)


def generate_angle_radians():
    return generate_float(0.0, 2.0 * math.pi)


def generate_angle_degrees():
    return generate_float(0.0, 360.0)


def generate_mjd_timestamp():
    # Random timestamp between 2020-01-01 and 2030-01-01
    return generate_float(58849.0, 62502.0)


def generate_utc_timestamp():
    # Random timestamp between 2020-01-01 and 2030-01-01
    return generate_float(1577836800.0, 1893456000.0)


def generate_string_timestamp():
    return datetime.utcfromtimestamp(generate_utc_timestamp()).strftime("%Y-%m-%dT%H:%M:%S.%f")[0:23]


def generate_string_date():
    return datetime.utcfromtimestamp(generate_utc_timestamp()).strftime("%Y-%m-%d")


def generate_string_time():
    return datetime.utcfromtimestamp(generate_utc_timestamp()).strftime("%H:%M:%S.%f")[0:12]


def generate_astropy_time(time_format="unix", ignore_erfa_warnings=True):
    if ignore_erfa_warnings:
        # catch and ignore erfa warnings:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", ErfaWarning)
            timeobj = Time(generate_utc_timestamp(), format="unix")
    else:
        timeobj = Time(generate_utc_timestamp(), format="unix")

    if time_format == "unix":
        return timeobj
    else:
        time_str = timeobj.to_value(format=time_format)
        timeobj = Time(time_str, format=time_format)
        return timeobj


def generate_int(min=None, max=None):
    # Assume 32-bit signed integers for now
    if min is None:
        min = -1 * 2**31
    if max is None:
        max = 2**31 - 1
    return random.randint(min, max)


def generate_positive_int(max=None):
    return generate_int(0, max)


def generate_choice(*args):
    return random.choice(args)


def generate_choices(*args, **kwargs):
    return random.choices(args, **kwargs)


def generate_string(prefix="", max_length=None):
    if max_length is not None:
        random_length = min(16, max_length - len(prefix))
    else:
        random_length = 16

    return prefix + secrets.token_hex(random_length)


def generate_bool():
    return generate_choice(*[True, False])


def generate_array_float32(size=(4096, 4096), min=None, max=None, units=None):
    if min is None:
        min = np.finfo("float32").min
    if max is None:
        max = np.finfo("float32").max

    array = np.random.default_rng().random(size=size, dtype=np.float32)
    array = min + max * array - min * array
    if units:
        array = u.Quantity(array, units, dtype=np.float32)
    return array


def generate_array_uint8(size=(4096, 4096), min=None, max=None, units=None):
    if min is None:
        min = np.iinfo("uint8").min
    if max is None:
        max = np.iinfo("uint8").max
    array = np.random.randint(min, high=max, size=size, dtype=np.uint8)
    if units:
        array = u.Quantity(array, units, dtype=np.uint8)
    return array


def generate_array_uint16(size=(4096, 4096), min=None, max=None, units=None):
    if min is None:
        min = np.iinfo("uint16").min
    if max is None:
        max = np.iinfo("uint16").max
    array = np.random.randint(min, high=max, size=size, dtype=np.uint16)
    if units:
        array = u.Quantity(array, units, dtype=np.uint16)
    return array


def generate_array_uint32(size=(4096, 4096), min=None, max=None, units=None):
    if min is None:
        min = np.iinfo("uint32").min
    if max is None:
        max = np.iinfo("uint32").max
    array = np.random.randint(min, high=max, size=size, dtype=np.uint32)
    if units:
        array = u.Quantity(array, units, dtype=np.uint32)
    return array


def generate_exposure_type():
    return generate_choice(
        "WFI_DARK",
        "WFI_FLAT",
        "WFI_GRISM",
        "WFI_IMAGE",
        "WFI_PRISM",
        "WFI_WFSC",
    )


def generate_detector():
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
    )


def generate_optical_element():
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
    )


def generate_software_version():
    return "{}.{}.{}".format(
        generate_positive_int(100),
        generate_positive_int(100),
        generate_positive_int(100),
    )
