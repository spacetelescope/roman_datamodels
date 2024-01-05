"""
Test general aspects of the RomanDataModel class.
"""
import pytest

from roman_datamodels.datamodels import RomanDataModel, RomanExtendedDataModel, _generated

models = [
    getattr(_generated, name) for name in _generated.__all__ if issubclass(mdl := getattr(_generated, name), RomanDataModel)
]


@pytest.mark.parametrize("model", models)
def test_override_handle(model):
    """
    Test the override_handle method
    """

    assert model.make_default(_shrink=True).override_handle == f"override://{model.__name__}"


@pytest.mark.parametrize("model", models)
def test_get_primary_array_name(model):
    """
    Test the primary_array_name method
    """

    # Check that the the primary array name has not been overridden.
    #    This is explicitly done for some of the extended models, these are explicitly tested in test_extended_models.py
    if not (
        issubclass(model, RomanExtendedDataModel) and model.get_primary_array_name is not RomanDataModel.get_primary_array_name
    ):
        instance = model.make_default(_shrink=True)

        if "data" in instance:
            assert instance.get_primary_array_name() == "data"
        else:
            assert instance.get_primary_array_name() is None


@pytest.mark.parametrize("model", models)
def test_shape(model):
    """
    Test the shape property
    """
    instance = model.make_default(_shrink=True)

    # Check that _shape is not initialized until it is accessed
    assert instance._shape is None

    if instance.get_primary_array_name() is None:
        # Nothing happens if there is no primary array
        assert instance.shape is None
        assert instance._shape is None
    else:
        # Shape is the same as the primary array
        assert instance.shape == instance[instance.get_primary_array_name()].shape
        # Shape is now remembered
        assert instance._shape == instance[instance.get_primary_array_name()].shape
