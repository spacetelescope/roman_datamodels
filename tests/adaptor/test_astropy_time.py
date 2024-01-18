from datetime import datetime

import pytest
from astropy.time import Time
from pydantic import BaseModel, ValidationError

from roman_datamodels.core.adaptors import AstropyTime, get_adaptor


def test_time_validate():
    """
    Test that an astropy time validates and does not get copied
    """

    class TestModel(BaseModel):
        time: AstropyTime[None]

    time = Time("2020-01-01T00:00:00.000")
    model = TestModel(time=time)
    assert isinstance(model.time, Time)
    assert model.time is time


def test_non_time():
    """
    Test that an astropy time annotation fails if the time is not an astropy time
    """

    class TestModel(BaseModel):
        time: AstropyTime[None]

    with pytest.raises(ValidationError):
        TestModel(time="2020-01-01T00:00:00.000")

    # TODO: Should this be allowed?
    with pytest.raises(ValidationError):
        TestModel(time=datetime(2020, 1, 1, 0, 0, 0, 0))

    TestModel(time=Time("2020-01-01T00:00:00.000"))  # Check no error


def test_json_schema_return():
    """
    Test the json schema return value
    """

    class TestModel(BaseModel):
        time: AstropyTime[None]

    TestModel.model_json_schema()["properties"]["time"] == {
        "title": None,
        "tag": AstropyTime._tags[0],
    }


def test_make_default():
    """Test make a default"""
    assert get_adaptor(AstropyTime[None]).make_default() == Time("2020-01-01T00:00:00.000", format="isot", scale="utc")
