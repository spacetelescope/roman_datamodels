"""
Run tests on the archive metadata retrieval for datamodels
"""
import pytest

from roman_datamodels.datamodels import _generated
from roman_datamodels.pydantic import RomanDataModel

models = [getattr(_generated, name) for name in _generated.__all__ if issubclass(getattr(_generated, name), RomanDataModel)]


@pytest.mark.parametrize("model", models)
def test_get_archive_metadata(model):
    """
    Test that the archive metadata can be retrieved.
        This does not test if it is accurate or not.
    """

    assert isinstance(model.get_archive_metadata(), dict)
