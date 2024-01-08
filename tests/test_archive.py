"""
Run tests on the archive metadata retrieval for datamodels
"""
import pytest

from roman_datamodels.core import Archive, BaseRomanDataModel
from roman_datamodels.datamodels import _generated

models = [getattr(_generated, name) for name in _generated.__all__ if issubclass(getattr(_generated, name), BaseRomanDataModel)]


@pytest.mark.parametrize("model", models)
def test_get_archive_metadata(model):
    """
    Test that the archive metadata can be retrieved.
        This does not test if it is accurate or not.
    """

    assert isinstance(model.get_archive_metadata(), dict)


def test_check_archive_catalog():
    """
    This test arbitrarily checks the an archive_catalog entry
        Basic was chosen because telescope has only an archive_catalog entry
    """

    metadata = _generated.Basic.get_archive_metadata()

    assert isinstance(metadata, dict)
    assert "telescope" in metadata
    assert isinstance(metadata["telescope"], Archive)
    assert metadata["telescope"].sdf is None
    assert metadata["telescope"].archive_catalog is not None
    assert metadata["telescope"].archive_catalog.datatype == "nvarchar(5)"
    assert metadata["telescope"].archive_catalog.destination == ["ScienceCommon.telescope", "GuideWindow.telescope"]


def test_check_sdf():
    """
    This test arbitrarily checks the an archive_catalog entry
        Target was chosen because it has a partially complete sdf entry
    """

    metadata = _generated.Target.get_archive_metadata()

    assert isinstance(metadata, dict)
    assert "proposer_ra" in metadata
    assert isinstance(metadata["proposer_ra"], Archive)
    assert metadata["proposer_ra"].sdf is not None
    assert metadata["proposer_ra"].sdf.special_processing == "VALUE_REQUIRED"
    assert metadata["proposer_ra"].sdf.source.origin == "PSS:fixed_target.ra_literal"
    assert metadata["proposer_ra"].sdf.source.function == "hms_to_degrees"

    # It has this too
    assert metadata["proposer_ra"].archive_catalog is not None
