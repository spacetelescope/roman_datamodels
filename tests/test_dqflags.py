from importlib.resources import files
from math import log10

import numpy as np
import pytest
from asdf.tags.core.ndarray import asdf_datatype_to_numpy_dtype
from rad import resources
from semantic_version import Version
from yaml import safe_load

from roman_datamodels import datamodels as rdm
from roman_datamodels import dqflags


@pytest.fixture(scope="module")
def ramp_schema():
    """The latest ramp schema"""

    ramp_schema = None
    for schema in (files(resources) / "schemas").glob("ramp-*.yaml"):
        if ramp_schema is None:
            ramp_schema = schema
        else:
            current_version = Version(ramp_schema.name.rsplit("-", 1)[1].rsplit(".", 1)[0])
            next_version = Version(schema.name.rsplit("-", 1)[1].rsplit(".", 1)[0])
            if next_version > current_version:
                ramp_schema = schema

    return safe_load(ramp_schema.read_text())


def _is_power_of_two(x):
    return (log10(x) / log10(2)) % 1 == 0


def test_pixel_uniqueness():
    """
    Test that there are no duplicate names in dqflags.pixel

        Note: The @unique decorator should ensure that no flag names have the
            same value as another in the enum raising an error at first import
            of this module. However, this test is just a sanity check on this.
    """

    assert len(dqflags.pixel) == len(dqflags.pixel.__members__)


@pytest.fixture(scope="module", params=dqflags.pixel)
def pixel_flag(request) -> dqflags.pixel:
    """Fixture for providing all pixel flags for testing."""
    return request.param


def test_pixel_flags(pixel_flag: dqflags.pixel, ramp_schema):
    """Test that each pixel flag follows the defined rules"""
    pixel_dq_type = ramp_schema["properties"]["pixeldq"]["datatype"]

    # Test that the pixel flags are dqflags.pixel instances
    assert isinstance(pixel_flag, dqflags.pixel)

    # Test that the pixel flags are of the correct dtype
    assert pixel_flag.dtype == asdf_datatype_to_numpy_dtype(pixel_dq_type)

    # Test that the pixel flags are ints
    assert isinstance(pixel_flag, np.uint32)

    # Test that the pixel flags are dict accessible
    assert dqflags.pixel[pixel_flag.name] is pixel_flag

    # Test that the pixel flag is a power of 2
    if pixel_flag.name == "GOOD":
        # GOOD is the only non-power-of-two flag (it is 0)
        assert pixel_flag.value == 0
    else:
        assert _is_power_of_two(pixel_flag.value)


def test_write_pixel_flags(tmp_path, pixel_flag: dqflags.pixel):
    filename = tmp_path / "test_dq.asdf"

    ramp = rdm.RampModel.create_fake_data(shape=(2, 8, 8))

    # Set all pixels to the flag value
    ramp.pixeldq[...] = pixel_flag

    # Check that we can write the model to disk (i.e. the flag validates)
    ramp.save(filename)

    # Check that we can read the model back in and the flag is preserved
    with rdm.open(filename) as dm:
        assert (dm.pixeldq == pixel_flag).all()


def test_group_uniqueness():
    """
    Test that there are no duplicate names in dqflags.group

        Note: The @unique decorator should ensure that no flag names have the
            same value as another in the enum raising an error at first import
            of this module. However, this test is just a sanity check on this.
    """
    assert len(dqflags.group) == len(dqflags.group.__members__)


@pytest.fixture(scope="module", params=dqflags.group)
def group_flag(request) -> dqflags.group:
    """Fixture for providing all group flags for testing."""
    return request.param


def test_group_flags(group_flag: dqflags.group, ramp_schema):
    """Test that each group flag follows the defined rules"""
    group_dq_type = ramp_schema["properties"]["groupdq"]["datatype"]

    # Test that the group flags are dqflags.group instances
    assert isinstance(group_flag, dqflags.group)

    # Test that the group flags are of the correct dtype
    assert group_flag.dtype == asdf_datatype_to_numpy_dtype(group_dq_type)

    # Test that the group flags are ints
    assert isinstance(group_flag, np.uint8)

    # Test that the group flags are dict accessible
    assert dqflags.group[group_flag.name] is group_flag

    # Test that each group flag matches a pixel flag of the same name
    # except for the WFI18_TRANSIENT flag
    if group_flag.name != "WFI18_TRANSIENT":
        assert dqflags.pixel[group_flag.name] == group_flag


def test_write_group_flags(tmp_path, group_flag: dqflags.group):
    filename = tmp_path / "test_dq.asdf"

    ramp = rdm.RampModel.create_fake_data(shape=(2, 8, 8))

    # Set all pixels to the flag value
    ramp.groupdq[...] = group_flag

    # Check that we can write the model to disk (i.e. the flag validates)
    ramp.save(filename)

    # Check that we can read the model back in and the flag is preserved
    with rdm.open(filename) as dm:
        assert (dm.groupdq == group_flag).all()
