from math import log10

import numpy as np
import pytest
from asdf import get_config
from asdf.schema import load_schema
from asdf.tags.core.ndarray import asdf_datatype_to_numpy_dtype

from roman_datamodels import datamodels as rdm
from roman_datamodels import dqflags
from roman_datamodels._stnode._utils import get_version

_RAMP_SCHEMA_PREFIX = "asdf://stsci.edu/datamodels/roman/schemas/ramp-"


@pytest.fixture(scope="module")
def ramp_schema():
    """The latest ramp schema"""
    ramp_uris = {get_version(uri): uri for uri in get_config().resource_manager if uri.startswith(_RAMP_SCHEMA_PREFIX)}

    # Latest one will be the first under a reverse sort
    return load_schema(ramp_uris[sorted(ramp_uris, reverse=True)[0]])


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


@pytest.mark.parametrize("flag", dqflags.pixel)
def test_pixel_flags(flag, ramp_schema):
    """Test that each pixel flag follows the defined rules"""
    pixel_dq_type = ramp_schema["properties"]["pixeldq"]["datatype"]

    # Test that the pixel flags are dqflags.pixel instances
    assert isinstance(flag, dqflags.pixel)

    # Test that the pixel flags are of the correct dtype
    assert flag.dtype == asdf_datatype_to_numpy_dtype(pixel_dq_type)

    # Test that the pixel flags are ints
    assert isinstance(flag, np.uint32)

    # Test that the pixel flags are dict accessible
    assert dqflags.pixel[flag.name] is flag

    # Test that the pixel flag is a power of 2
    if flag.name == "GOOD":
        # GOOD is the only non-power-of-two flag (it is 0)
        assert flag.value == 0
    else:
        assert _is_power_of_two(flag.value)


@pytest.mark.parametrize("flag", dqflags.pixel)
def test_write_pixel_flags(tmp_path, flag):
    filename = tmp_path / "test_dq.asdf"

    ramp = rdm.RampModel.create_fake_data(shape=(2, 8, 8))

    # Set all pixels to the flag value
    ramp.pixeldq[...] = flag

    # Check that we can write the model to disk (i.e. the flag validates)
    ramp.save(filename)

    # Check that we can read the model back in and the flag is preserved
    with rdm.open(filename) as dm:
        assert (dm.pixeldq == flag).all()


def test_group_uniqueness():
    """
    Test that there are no duplicate names in dqflags.group

        Note: The @unique decorator should ensure that no flag names have the
            same value as another in the enum raising an error at first import
            of this module. However, this test is just a sanity check on this.
    """
    assert len(dqflags.group) == len(dqflags.group.__members__)


@pytest.mark.parametrize("flag", dqflags.group)
def test_group_flags(flag, ramp_schema):
    """Test that each group flag follows the defined rules"""
    group_dq_type = ramp_schema["properties"]["groupdq"]["datatype"]

    # Test that the group flags are dqflags.group instances
    assert isinstance(flag, dqflags.group)

    # Test that the group flags are of the correct dtype
    assert flag.dtype == asdf_datatype_to_numpy_dtype(group_dq_type)

    # Test that the group flags are ints
    assert isinstance(flag, np.uint8)

    # Test that the group flags are dict accessible
    assert dqflags.group[flag.name] is flag

    # Test that each group flag matches a pixel flag of the same name
    # except for the WFI18_TRANSIENT flag
    if flag.name != "WFI18_TRANSIENT":
        assert dqflags.pixel[flag.name] == flag


@pytest.mark.parametrize("flag", dqflags.group)
def test_write_group_flags(tmp_path, flag):
    filename = tmp_path / "test_dq.asdf"

    ramp = rdm.RampModel.create_fake_data(shape=(2, 8, 8))

    # Set all pixels to the flag value
    ramp.groupdq[...] = flag

    # Check that we can write the model to disk (i.e. the flag validates)
    ramp.save(filename)

    # Check that we can read the model back in and the flag is preserved
    with rdm.open(filename) as dm:
        assert (dm.groupdq == flag).all()
