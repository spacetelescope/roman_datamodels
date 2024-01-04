"""
Run tests on the data model validation
"""
import pytest
from pydantic import ValidationError

from roman_datamodels.datamodels import _generated
from roman_datamodels.pydantic import RomanDataModel

models = [getattr(_generated, name) for name in _generated.__all__ if issubclass(getattr(_generated, name), RomanDataModel)]


# Create a value that should not be valid for the majority of fields
#    The exception is any field that is unconstrained (e.g. Any). Currently,
#    this should only be the DistortionRefModel.coordinate_distortion_transform
class BadValue:
    """
    This should create a value that should not be valid for the majority of fields

    The exception is any field that is unconstrained (e.g. Any). Currently,
    this should only be the DistortionRefModel.coordinate_distortion_transform.
    """

    ...


@pytest.mark.parametrize("model", models)
def test_construct_with_invalid(model):
    """
    Test that if we construct a model with an invalid value, it fails to validate
    """
    input_dict = dict(model.make_default(_shrink=True))

    # Choose a field to modify
    field_name = list(model.model_fields.keys())[0]

    # Create input dict with bad value
    input_dict[field_name] = BadValue()

    # Attempt to construct the model
    with pytest.raises(ValidationError, match=r".* validation error for .*"):
        model(**input_dict)


@pytest.mark.parametrize("model", models)
def test_invalidate_field(model):
    """
    Test that if we change a field to an invalid value, the model fails to validate
    """

    instance = model.make_default(_shrink=True)

    # Choose a field to modify
    field_name = list(model.model_fields.keys())[0]

    # Modify the field to the bad value
    with pytest.raises(ValidationError, match=r".* validation error for .*"):
        setattr(instance, field_name, BadValue())


@pytest.mark.parametrize("model", models)
def test_model_pause_validation(model):
    """
    Test that the model's paused validation works.
        Note by default the model is revalidated after pause_validation context exits.
    """
    instance = model.make_default(_shrink=True)

    for field_name in model.model_fields:
        # Track if the field has been set as pytest.raises will not allow any code
        #   inside the context manager to run after the error is raised.
        # This check will occur outside the pytest.raises context, but the value
        #    will be adjusted inside the context.
        has_been_set = False

        # Check the validation configuration for the model
        assert instance.model_config["validate_assignment"] is True
        assert instance.model_config["revalidate_instances"] == "always"

        with pytest.raises(ValidationError):
            with instance.pause_validation():
                # Check the validation configuration for the model as been relaxed
                assert instance.model_config["validate_assignment"] is False
                assert instance.model_config["revalidate_instances"] == "never"

                # Set the value to a bad value
                setattr(instance, field_name, bad_value := BadValue())
                assert getattr(instance, field_name) is bad_value
                has_been_set = True

        # Check that the validation configuration for the model is restored
        assert instance.model_config["validate_assignment"] is True
        assert instance.model_config["revalidate_instances"] == "always"

        # Check that has_been_set is updated
        assert has_been_set


@pytest.mark.parametrize("model", models)
def test_model_pause_validation_no_revalidate(model):
    """
    Test that the model's paused validation works, and does not revalidate if that
        option is set.
    """
    instance = model.make_default(_shrink=True)

    for field_name in model.model_fields:
        # Check the validation configuration for the model
        assert instance.model_config["validate_assignment"] is True
        assert instance.model_config["revalidate_instances"] == "always"

        with instance.pause_validation(revalidate_on_exit=False):
            # Check the validation configuration for the model as been relaxed
            assert instance.model_config["validate_assignment"] is False
            assert instance.model_config["revalidate_instances"] == "never"

            # Set the value to a bad value
            setattr(instance, field_name, bad_value := BadValue())
            assert getattr(instance, field_name) is bad_value

        # Check that the validation configuration for the model is restored
        assert instance.model_config["validate_assignment"] is True
        assert instance.model_config["revalidate_instances"] == "always"

        # Check the value is still bad
        assert getattr(instance, field_name) is bad_value


@pytest.mark.parametrize("model", models)
def test_model_getitem(model):
    """
    Test that we can access model fields via the "dictionary-like" access interface.
    """
    instance = model.make_default(_shrink=True)

    for field_name in model.model_fields:
        assert instance[field_name] is getattr(instance, field_name)


@pytest.mark.parametrize("model", models)
def test_model_setitem(model):
    """
    Test that we can set model fields via the "dictionary-like" access interface.
    """
    for field_name in model.model_fields:
        if field_name == "coordinate_distortion_transform":
            continue

        instance = model.make_default(_shrink=True)
        bad_value = BadValue()

        with pytest.warns(RuntimeWarning, match=r".*RomanDataModel.__setitem__.*"):
            instance[field_name] = bad_value

        assert instance[field_name] is bad_value

        with pytest.raises(ValidationError):
            instance.model_validate(instance)
