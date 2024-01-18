import pytest
from gwcs.wcs import WCS
from pydantic import BaseModel, ValidationError

from roman_datamodels.core.adaptors import GwcsWcs, get_adaptor


def test_wcs_validate():
    """
    Test that a GWCS wcs validates and does not get copied
    """

    class TestModel(BaseModel):
        wcs: GwcsWcs[None]

    wcs = GwcsWcs.make_default()
    model = TestModel(wcs=wcs)
    assert isinstance(model.wcs, WCS)
    assert model.wcs is wcs


def test_non_wcs():
    """
    Test that a GWCS wcs annotation fails if the wcs is not a GWCS wcs
    """

    class TestModel(BaseModel):
        wcs: GwcsWcs[None]

    with pytest.raises(ValidationError):
        TestModel(wcs="foo")

    TestModel(wcs=GwcsWcs.make_default())  # Check no error


def test_json_schema_return():
    """
    Test the json schema return value
    """

    class TestModel(BaseModel):
        wcs: GwcsWcs[None]

    TestModel.model_json_schema()["properties"]["wcs"] == {
        "title": None,
        "tag": GwcsWcs._tags[0],
    }


def test_make_default():
    """Test make a default"""
    assert isinstance(get_adaptor(GwcsWcs[None]).make_default(), WCS)
