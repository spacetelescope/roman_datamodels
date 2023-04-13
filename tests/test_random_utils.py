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
@pytest.mark.parametrize("seed", [None, 42])
def test_generate_float(min, max, seed):
    t_min, t_max = _min_max(min, max)

    value = random_utils.generate_float(min=min, max=max, seed=seed)
    for _ in range(50 if seed is None else 1):
        assert isinstance(value, float)
        assert t_min <= value <= t_max


@pytest.mark.parametrize("max", [None, 1, 10, 100, 1000])
@pytest.mark.parametrize("seed", [None, 42])
def test_generate_positive_float(max, seed):
    t_min, t_max = _min_max(0, max)

    for _ in range(50 if seed is None else 1):
        value = random_utils.generate_positive_float(max=max, seed=seed)
        assert isinstance(value, float)
        assert t_min <= value <= t_max


@pytest.mark.parametrize("seed", [None, 42])
def test_generate_angle_radians(seed):
    for _ in range(50 if seed is None else 1):
        value = random_utils.generate_angle_radians(seed=seed)
        assert 0 <= value <= 2 * np.pi


@pytest.mark.parametrize("seed", [None, 42])
def test_generate_angle_degrees(seed):
    for _ in range(50 if seed is None else 1):
        value = random_utils.generate_angle_degrees(seed=seed)
        assert 0 <= value <= 360


@pytest.mark.parametrize("seed", [None, 42])
def test_generate_mjd_timestamp(seed):
    for _ in range(50 if seed is None else 1):
        value = random_utils.generate_mjd_timestamp(seed=seed)
        assert 58849 <= value <= 62502


@pytest.mark.parametrize("seed", [None, 42])
def test_generate_utc_timestamp(seed):
    for _ in range(50 if seed is None else 1):
        value = random_utils.generate_utc_timestamp(seed=seed)
        assert 1577836800.0 <= value <= 1893456000.0


@pytest.mark.parametrize("seed", [None, 42])
def test_genrate_string_timestamp(seed):
    for _ in range(50 if seed is None else 1):
        value = random_utils.generate_string_timestamp(seed=seed)
        assert isinstance(value, str)
        assert len(value) == 23
        pattern = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d{3}")
        assert pattern.match(value)


@pytest.mark.parametrize("seed", [None, 42])
def test_generate_string_date(seed):
    for _ in range(50 if seed is None else 1):
        value = random_utils.generate_string_date(seed=seed)
        assert isinstance(value, str)
        assert len(value) == 10
        pattern = re.compile(r"\d{4}-\d{2}-\d{2}")
        assert pattern.match(value)


@pytest.mark.parametrize("seed", [None, 42])
def test_generate_string_time(seed):
    for _ in range(50 if seed is None else 1):
        value = random_utils.generate_string_time(seed=seed)
        assert isinstance(value, str)
        assert len(value) == 12
        pattern = re.compile(r"\d{2}:\d{2}:\d{2}.\d{3}")
        assert pattern.match(value)


@pytest.mark.parametrize("time_format", ["unix", "isot"])
@pytest.mark.parametrize("seed", [None, 42])
def test_generate_astropy_time(time_format, seed):
    for _ in range(50 if seed is None else 1):
        value = random_utils.generate_astropy_time(time_format=time_format, seed=seed)
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
@pytest.mark.parametrize("seed", [None, 42])
def test_generate_int(min, max, seed):
    t_min, t_max = _int_min_max(min, max)

    for _ in range(50 if seed is None else 1):
        value = random_utils.generate_int(min=min, max=max, seed=seed)
        assert isinstance(value, int)
        assert t_min <= value <= t_max


@pytest.mark.parametrize("max", [None, 1, 10, 100, 1000])
@pytest.mark.parametrize("seed", [None, 42])
def test_generate_positive_int(max, seed):
    t_min, t_max = _int_min_max(0, max)

    for _ in range(50 if seed is None else 1):
        value = random_utils.generate_positive_int(max=max, seed=seed)
        assert isinstance(value, int)
        assert t_min <= value <= t_max


@pytest.mark.parametrize("choices", [[1, 2, 3], ["a", "b", "c"], [1, "a", 2, "b", 3, "c"]])
@pytest.mark.parametrize("unpack", [True, False])
@pytest.mark.parametrize("seed", [None, 42])
def test_generate_choice(choices, unpack, seed):
    for _ in range(50 if seed is None else 1):
        if unpack:
            value = random_utils.generate_choice(*choices, seed=seed)
        else:
            value = random_utils.generate_choice(choices, seed=seed)
        assert value in choices


@pytest.mark.parametrize("choices", [[1, 2, 3], ["a", "b", "c"], [1, "a", 2, "b", 3, "c"]])
@pytest.mark.parametrize("size", [2, 3, 4, 5])
@pytest.mark.parametrize("unpack", [True, False])
@pytest.mark.parametrize("seed", [None, 42])
def test_generate_choices(choices, size, unpack, seed):
    for _ in range(50 if seed is None else 1):
        if unpack:
            value = random_utils.generate_choices(*choices, k=size, seed=seed)
        else:
            value = random_utils.generate_choices(choices, k=size, seed=seed)

        assert isinstance(value, list)
        assert len(value) == size
        for v in value:
            assert v in choices


@pytest.mark.parametrize("prefix", ["", "this", "is", "a", "test"])
@pytest.mark.parametrize("max_length", [None, 4, 5, 6, 7, 8, 9, 10])
@pytest.mark.parametrize("seed", [None, 42])
def test_generate_string(prefix, max_length, seed):
    for _ in range(50 if seed is None else 1):
        value = random_utils.generate_string(prefix=prefix, max_length=max_length, seed=seed)
        assert isinstance(value, str)
        assert value.startswith(prefix)
        assert len(value) <= (2 * max_length if max_length is not None else 32) + len(prefix)


@pytest.mark.parametrize("seed", [None, 42])
def test_generate_bool(seed):
    for _ in range(50 if seed is None else 1):
        value = random_utils.generate_bool(seed=seed)
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
@pytest.mark.parametrize("seed", [None, 42])
def test_generate_array_float32(size, min, max, units, seed):
    t_min, t_max = _float32_min_max(min, max)

    value = random_utils.generate_array_float32(size=size, min=min, max=max, units=units, seed=seed)
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
@pytest.mark.parametrize("seed", [None, 42])
def test_generate_array_uint8(size, min, max, units, seed):
    t_min, t_max = _uint8_min_max(min, max)

    value = random_utils.generate_array_uint8(size=size, min=min, max=max, units=units, seed=seed)
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
@pytest.mark.parametrize("seed", [None, 42])
def test_generate_array_uint16(size, min, max, units, seed):
    t_min, t_max = _uint16_min_max(min, max)

    value = random_utils.generate_array_uint16(size=size, min=min, max=max, units=units, seed=seed)
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
@pytest.mark.parametrize("seed", [None, 42])
def test_generate_array_uint32(size, min, max, units, seed):
    t_min, t_max = _uint32_min_max(min, max)

    value = random_utils.generate_array_uint32(size=size, min=min, max=max, units=units, seed=seed)
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


@pytest.mark.parametrize("seed", [None, 42])
def test_generate_exposure_type(seed):
    t_values = [
        "WFI_DARK",
        "WFI_FLAT",
        "WFI_GRISM",
        "WFI_IMAGE",
        "WFI_PRISM",
        "WFI_WFSC",
    ]
    for _ in range(50 if seed is None else 1):
        value = random_utils.generate_exposure_type(seed=seed)
        assert isinstance(value, str)
        assert value in t_values


@pytest.mark.parametrize("seed", [None, 42])
def test_generate_detector(seed):
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
    for _ in range(50 if seed is None else 1):
        value = random_utils.generate_detector(seed=seed)
        assert isinstance(value, str)
        assert value in t_values


@pytest.mark.parametrize("seed", [None, 42])
def test_generate_optical_element(seed):
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
    for _ in range(50 if seed is None else 1):
        value = random_utils.generate_optical_element(seed=seed)
        assert isinstance(value, str)
        assert value in t_values


@pytest.mark.parametrize("seed", [None, 42])
def test_generate_software_version(seed):
    for _ in range(50 if seed is None else 1):
        value = random_utils.generate_software_version(seed=seed)
        assert isinstance(value, str)
        pattern = re.compile(r"([0-9]+)\.([0-9]+)\.([0-9]+)")
        assert pattern.match(value)

        ints = value.split(".")
        ints = np.array([int(i) for i in ints])
        assert (0 <= ints).all()
        assert (ints <= 100).all()
