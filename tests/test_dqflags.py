from math import log10

import pytest

from roman_datamodels import datamodels as rdm
from roman_datamodels import dqflags
from roman_datamodels.maker_utils import mk_datamodel


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
def test_pixel_flags(flag):
    """Test that each pixel flag follows the defined rules"""
    # Test that the pixel flags are dqflags.pixel instances
    assert isinstance(flag, dqflags.pixel)

    # Test that the pixel flags are ints
    assert isinstance(flag, int)

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

    ramp = mk_datamodel(rdm.RampModel, shape=(2, 8, 8))

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
def test_group_flags(flag):
    """Test that each group flag follows the defined rules"""
    # Test that the group flags are dqflags.group instances
    assert isinstance(flag, dqflags.group)

    # Test that the group flags are ints
    assert isinstance(flag, int)

    # Test that the group flags are dict accessible
    assert dqflags.group[flag.name] is flag

    # Test that each group flag matches a pixel flag of the same name
    assert dqflags.pixel[flag.name] == flag


@pytest.mark.parametrize("flag", dqflags.group)
def test_write_group_flags(tmp_path, flag):
    filename = tmp_path / "test_dq.asdf"

    ramp = mk_datamodel(rdm.RampModel, shape=(2, 8, 8))

    # Set all pixels to the flag value
    ramp.groupdq[...] = flag

    # Check that we can write the model to disk (i.e. the flag validates)
    ramp.save(filename)

    # Check that we can read the model back in and the flag is preserved
    with rdm.open(filename) as dm:
        assert (dm.groupdq == flag).all()
