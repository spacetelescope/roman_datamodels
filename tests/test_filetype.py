from pathlib import Path

import asdf
import pytest

from roman_datamodels import filetype

DATA_DIRECTORY = Path(__file__).parent / "data"


@pytest.mark.filterwarnings("ignore:ERFA function.*")
def test_filetype():
    assert filetype.check(DATA_DIRECTORY / "empty.json") == "asn"
    assert filetype.check(DATA_DIRECTORY / "example_schema.json") == "asn"
    with open(DATA_DIRECTORY / "fake.json") as file:
        assert filetype.check(file) == "asn"

    assert filetype.check(DATA_DIRECTORY / "empty.asdf") == "asdf"
    assert filetype.check(DATA_DIRECTORY / "pluto.asdf") == "asdf"
    with open(DATA_DIRECTORY / "pluto.asdf", "rb") as file:
        assert filetype.check(file) == "asdf"

    assert filetype.check(DATA_DIRECTORY / "fake.asdf") == "asdf"
    with open(DATA_DIRECTORY / "fake.asdf") as file:
        assert filetype.check(file) == "asn"

    assert filetype.check(str(DATA_DIRECTORY / "pluto.asdf")) == "asdf"

    with pytest.raises(ValueError):
        filetype.check(DATA_DIRECTORY / "empty.txt")

    with pytest.raises(ValueError):
        filetype.check(2)

    with pytest.raises(ValueError):
        filetype.check("test")


def test_read_pattern_properties():
    """
    Regression test for reading pattern properties
    """

    from roman_datamodels.datamodels import open as rdm_open

    # This file has been modified by hand to break the `photmjsr` value
    with pytest.raises(asdf.ValidationError):
        rdm_open(DATA_DIRECTORY / "photmjsm.asdf")
