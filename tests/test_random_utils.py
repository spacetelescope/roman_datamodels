import re

import astropy.units as u
import numpy as np
import pytest
from astropy.time import Time

from roman_datamodels import random_utils


def _min_max(min, max):
    if min is None:
        min = np.finfo("float").min
    if max is None:
        max = np.finfo("float").max

    return min, max


@pytest.mark.parametrize("min, max", [(None, None), (-1, 1), (-30, 10), (-5, 100), (-100, 1000)])
def test_generate_float(min, max):
    t_min, t_max = _min_max(min, max)

    value = random_utils.generate_float(min=min, max=max)
    assert isinstance(value, float)
    assert t_min <= value <= t_max


@pytest.mark.parametrize("max", [None, 1, 10, 100, 1000])
def test_generate_positive_float(max):
    t_min, t_max = _min_max(0, max)

    value = random_utils.generate_positive_float(max=max)
    assert isinstance(value, float)
    assert t_min <= value <= t_max


def test_generate_angle_radians():
    value = random_utils.generate_angle_radians()
    assert 0 <= value <= 2 * np.pi


def test_generate_angle_degrees():
    value = random_utils.generate_angle_degrees()
    assert 0 <= value <= 360


def test_generate_mjd_timestamp():
    value = random_utils.generate_mjd_timestamp()
    assert 58849 <= value <= 62502


def test_generate_utc_timestamp():
    value = random_utils.generate_utc_timestamp()
    assert 1577836800.0 <= value <= 1893456000.0


def test_genrate_string_timestamp():
    value = random_utils.generate_string_timestamp()
    assert isinstance(value, str)
    assert len(value) == 23
    pattern = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d{3}")
    assert pattern.match(value)


def test_generate_string_date():
    value = random_utils.generate_string_date()
    assert isinstance(value, str)
    assert len(value) == 10
    pattern = re.compile(r"\d{4}-\d{2}-\d{2}")
    assert pattern.match(value)


def test_generate_string_time():
    value = random_utils.generate_string_time()
    assert isinstance(value, str)
    assert len(value) == 12
    pattern = re.compile(r"\d{2}:\d{2}:\d{2}.\d{3}")
    assert pattern.match(value)


@pytest.mark.parametrize("time_format", ["unix", "isot"])
def test_generate_astropy_time(time_format):
    value = random_utils.generate_astropy_time(time_format=time_format)
    assert isinstance(value, Time)
    assert 1577836800.0 <= value.unix <= 1893456000.0
    assert value.format == time_format


def _int_min_max(min, max):
    if min is None:
        min = -1 * 2**31
    if max is None:
        max = 2**31 - 1

    return min, max


@pytest.mark.parametrize("min, max", [(None, None), (-1, 1), (-30, 10), (-5, 100), (-100, 1000)])
def test_generate_int(min, max):
    t_min, t_max = _int_min_max(min, max)

    value = random_utils.generate_int(min=min, max=max)
    assert isinstance(value, int)
    assert t_min <= value <= t_max


@pytest.mark.parametrize("max", [None, 1, 10, 100, 1000])
def test_generate_positive_int(max):
    t_min, t_max = _int_min_max(0, max)

    value = random_utils.generate_positive_int(max=max)
    assert isinstance(value, int)
    assert t_min <= value <= t_max


@pytest.mark.parametrize("choices", [[1, 2, 3], ["a", "b", "c"], [1, "a", 2, "b", 3, "c"]])
@pytest.mark.parametrize("unpack", [True, False])
def test_generate_choice(choices, unpack):
    for _ in range(50):
        if unpack:
            value = random_utils.generate_choice(*choices)
        else:
            value = random_utils.generate_choice(choices)
        assert value in choices


@pytest.mark.parametrize("choices", [[1, 2, 3], ["a", "b", "c"], [1, "a", 2, "b", 3, "c"]])
@pytest.mark.parametrize("size", [2, 3, 4, 5])
@pytest.mark.parametrize("unpack", [True, False])
def test_generate_choices(choices, size, unpack):
    for _ in range(50):
        if unpack:
            value = random_utils.generate_choices(*choices, k=size)
        else:
            value = random_utils.generate_choices(choices, k=size)

        assert isinstance(value, list)
        assert len(value) == size
        for v in value:
            assert v in choices


@pytest.mark.parametrize("prefix", ["", "this", "is", "a", "test"])
@pytest.mark.parametrize("max_length", [None, 4, 5, 6, 7, 8, 9, 10])
def test_generate_string(prefix, max_length):
    value = random_utils.generate_string(prefix=prefix, max_length=max_length)
    assert isinstance(value, str)
    assert value.startswith(prefix)
    assert len(value) <= (2 * max_length if max_length is not None else 32) + len(prefix)


def test_generate_bool():
    for _ in range(100):
        value = random_utils.generate_bool()
        assert isinstance(value, bool)
        assert value in [True, False]


def _float32_min_max(min, max):
    if min is None:
        min = np.finfo("float32").min
    if max is None:
        max = np.finfo("float32").max

    return min, max


@pytest.mark.parametrize("size", [(4096, 4096), (2048, 2048), (1024, 1024), (512, 512), (256, 256)])
@pytest.mark.parametrize("min, max", [(None, None), (-1, 1), (-30, 10), (-5, 100), (-100, 1000)])
@pytest.mark.parametrize("units", [None, u.m, u.electron, u.DN])
def test_generate_array_float32(size, min, max, units):
    t_min, t_max = _float32_min_max(min, max)

    value = random_utils.generate_array_float32(size=size, min=min, max=max, units=units)
    assert isinstance(value, np.ndarray)
    assert value.dtype == np.float32
    assert value.shape == size

    if units is not None:
        assert isinstance(value, u.Quantity)
        assert value.unit == units
        val = value.value
    else:
        val = value
    assert (t_min <= val).all()
    assert (val <= t_max).all()


def _uint8_min_max(min, max):
    if min is None:
        min = np.iinfo("uint8").min
    if max is None:
        max = np.iinfo("uint8").max

    return min, max


@pytest.mark.parametrize("size", [(4096, 4096), (2048, 2048), (1024, 1024), (512, 512), (256, 256)])
@pytest.mark.parametrize("min, max", [(None, None), (0, 1), (5, 10), (10, 100), (100, 255)])
@pytest.mark.parametrize("units", [None, u.m, u.electron, u.DN])
def test_generate_array_uint8(size, min, max, units):
    t_min, t_max = _uint8_min_max(min, max)

    value = random_utils.generate_array_uint8(size=size, min=min, max=max, units=units)
    assert isinstance(value, np.ndarray)
    assert value.dtype == np.uint8
    assert value.shape == size

    if units is not None:
        assert isinstance(value, u.Quantity)
        assert value.unit == units
        val = value.value
    else:
        val = value
    assert (t_min <= val).all()
    assert (val <= t_max).all()


def _uint16_min_max(min, max):
    if min is None:
        min = np.iinfo("uint16").min
    if max is None:
        max = np.iinfo("uint16").max

    return min, max


@pytest.mark.parametrize("size", [(4096, 4096), (2048, 2048), (1024, 1024), (512, 512), (256, 256)])
@pytest.mark.parametrize("min, max", [(None, None), (0, 1), (5, 10), (10, 100), (100, 1000)])
@pytest.mark.parametrize("units", [None, u.m, u.electron, u.DN])
def test_generate_array_uint16(size, min, max, units):
    t_min, t_max = _uint16_min_max(min, max)

    value = random_utils.generate_array_uint16(size=size, min=min, max=max, units=units)
    assert isinstance(value, np.ndarray)
    assert value.dtype == np.uint16
    assert value.shape == size

    if units is not None:
        assert isinstance(value, u.Quantity)
        assert value.unit == units
        val = value.value
    else:
        val = value
    assert (t_min <= val).all()
    assert (val <= t_max).all()


def _uint32_min_max(min, max):
    if min is None:
        min = np.iinfo("uint32").min
    if max is None:
        max = np.iinfo("uint32").max

    return min, max


@pytest.mark.parametrize("size", [(4096, 4096), (2048, 2048), (1024, 1024), (512, 512), (256, 256)])
@pytest.mark.parametrize("min, max", [(None, None), (0, 1), (5, 10), (10, 100), (100, 1000)])
@pytest.mark.parametrize("units", [None, u.m, u.electron, u.DN])
def test_generate_array_uint32(size, min, max, units):
    t_min, t_max = _uint32_min_max(min, max)

    value = random_utils.generate_array_uint32(size=size, min=min, max=max, units=units)
    assert isinstance(value, np.ndarray)
    assert value.dtype == np.uint32
    assert value.shape == size

    if units is not None:
        assert isinstance(value, u.Quantity)
        assert value.unit == units
        val = value.value
    else:
        val = value
    assert (t_min <= val).all()
    assert (val <= t_max).all()


def test_generate_exposure_type():
    t_values = [
        "WFI_DARK",
        "WFI_FLAT",
        "WFI_GRISM",
        "WFI_IMAGE",
        "WFI_PRISM",
        "WFI_WFSC",
    ]
    for _ in range(100):
        value = random_utils.generate_exposure_type()
        assert isinstance(value, str)
        assert value in t_values


def test_generate_detector():
    t_values = [
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
    ]
    for _ in range(100):
        value = random_utils.generate_detector()
        assert isinstance(value, str)
        assert value in t_values


def test_generate_optical_element():
    t_values = [
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
    ]
    for _ in range(100):
        value = random_utils.generate_optical_element()
        assert isinstance(value, str)
        assert value in t_values


def test_generate_software_version():
    for _ in range(100):
        value = random_utils.generate_software_version()
        assert isinstance(value, str)
        pattern = re.compile(r"([0-9]+)\.([0-9]+)\.([0-9]+)")
        assert pattern.match(value)

        ints = value.split(".")
        ints = np.array([int(i) for i in ints])
        assert (0 <= ints).all()
        assert (ints <= 100).all()
