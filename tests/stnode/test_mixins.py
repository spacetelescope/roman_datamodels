import pytest
from astropy.time import Time

from roman_datamodels import stnode

NOW_MJD = int(Time.now().to_value("mjd"))
TEST_TIME = Time("2000-01-01T00:00:00.0", format="isot", scale="utc")
TEST_MJD = TEST_TIME.to_value("mjd")

FILE_DATE_TYPES = (stnode.FileDate, stnode.FpsFileDate, stnode.TvacFileDate)

DEFAULT_STR_TYPES = [
    (stnode.CalibrationSoftwareName, "RomanCAL"),
    (stnode.Origin, "STSCI/SOC"),
    (stnode.Telescope, "ROMAN"),
]


@pytest.mark.parametrize("type_", FILE_DATE_TYPES)
@pytest.mark.parametrize(
    "method, defaults, expected",
    (
        ("from_schema", None, NOW_MJD),
        ("fake_data", None, 58849),  # the mjd of the fake value
        ("from_schema", TEST_TIME, TEST_MJD),
        ("fake_data", TEST_TIME, TEST_MJD),
    ),
)
def test_file_date(type_, method, defaults, expected):
    obj = getattr(type_, method)(defaults)
    assert isinstance(obj, type_)
    assert abs(obj.to_value("mjd") - expected) < 1


@pytest.mark.parametrize("type_, expected", DEFAULT_STR_TYPES)
@pytest.mark.parametrize("method", ("from_schema", "fake_data"))
@pytest.mark.parametrize("defaults", (None, "test"))
def test_default_str_mixin(type_, expected, method, defaults):
    obj = getattr(type_, method)(defaults)
    assert isinstance(obj, type_)
    if defaults:
        assert obj == defaults
    else:
        assert obj == expected


@pytest.mark.parametrize(
    "type_, method, expected",
    (
        (stnode.PrdVersion, "fake_data", "8.8.8"),
        (stnode.SdfSoftwareVersion, "fake_data", "7.7.7"),
    ),
)
@pytest.mark.parametrize("defaults", (None, "test"))
def test_special_fake_str_mixin(type_, expected, method, defaults):
    obj = getattr(type_, method)(defaults)
    assert isinstance(obj, type_)
    if defaults:
        assert obj == defaults
    else:
        assert obj == expected


def test_ref_file_mixin():
    defaults = {"flat": "foo.asdf"}
    obj = stnode.RefFile.from_schema(defaults)
    assert obj["dark"] == "N/A"
    assert obj["flat"] == defaults["flat"]


@pytest.mark.parametrize("type_", (stnode.L2CalStep, stnode.L3CalStep))
def test_cal_step_mixin(type_):
    defaults = {"outlier_detection": "COMPLETE"}
    obj = type_.from_schema(defaults)
    assert obj["skymatch"] == "INCOMPLETE"
    assert obj["outlier_detection"] == defaults["outlier_detection"]


def test_wfi_img_photom_ref_mixin():
    obj = stnode.WfiImgPhotomRef.from_schema()
    assert "phot_table" in obj
