"""
Test general aspects of the RomanDataModel class.
"""
import pytest

from roman_datamodels.datamodels import RomanDataModel, RomanExtendedDataModel, _generated
from roman_datamodels.pydantic import BaseRomanDataModel

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


@pytest.mark.parametrize("model", models)
def test_to_flat_dict(model):
    """
    Partially test the to_flat_dict method
    """
    instance = model.make_default(_shrink=True)

    flat_dict = instance.to_flat_dict()

    # Check first and second levels for data models
    for field_name, field in instance.model_fields.items():
        # We only check required fields
        if field.is_required():
            for key in flat_dict:
                if key.startswith(field_name):
                    break
            else:
                assert False, f"Field {field_name} not found in flat_dict"

            # Do the same for sub-models
            if isinstance(sub_instance := instance[field_name], BaseRomanDataModel):
                for sub_field_name, sub_field in sub_instance.model_fields.items():
                    if sub_field.is_required():
                        for key in flat_dict:
                            if key.startswith(f"{field_name}.{sub_field_name}"):
                                break
                        else:
                            assert False, f"Field {field_name}.{sub_field_name} not found in flat_dict"


@pytest.mark.parametrize("model", models)
def test_get_crds_parameters(model):
    """
    Test that the get_crds_parameters method works
    """
    instance = model.make_default(_shrink=True)

    for key, value in instance.get_crds_parameters().items():
        assert isinstance(key, str)
        assert isinstance(value, (str, int, float, bool, complex))
