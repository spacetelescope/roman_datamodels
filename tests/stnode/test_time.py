import pytest
from astropy.time import Time

from roman_datamodels import _stnode as stnode

NOW_MJD = int(Time.now().to_value("mjd"))
TEST_TIME = Time("2000-01-01T00:00:00.0", format="isot", scale="utc")
TEST_MJD = TEST_TIME.to_value("mjd")

FILE_DATE_TYPES = (stnode.FileDate, stnode.FpsFileDate, stnode.TvacFileDate)


@pytest.mark.parametrize("type_", FILE_DATE_TYPES)
@pytest.mark.parametrize(
    "method, defaults, expected",
    (
        ("create_minimal", None, NOW_MJD),
        ("create_fake_data", None, 58849),  # the mjd of the fake value
        ("create_minimal", TEST_TIME, TEST_MJD),
        ("create_fake_data", TEST_TIME, TEST_MJD),
    ),
)
def test_file_date(type_, method, defaults, expected):
    obj = getattr(type_, method)(defaults)
    assert isinstance(obj, type_)
    assert abs(obj.to_value("mjd") - expected) < 1
