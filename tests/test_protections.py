import pytest

from roman_datamodels.core import BaseRomanDataModel, RomanDataModel, RomanExtendedDataModel

from ._helpers import models


def test_roman_data_model_abstract():
    """
    Test to make sure the RomanDataModel is an abstract class so that it cannot
    be directly instantiated.
    """

    with pytest.raises(TypeError, match=r"Can't instantiate abstract class.* with abstract method.*"):
        BaseRomanDataModel()


def test_tagged_data_model_abstract():
    """
    Test to make sure the TaggedDataModel is an abstract class so that it cannot
    be directly instantiated.
    """

    with pytest.raises(TypeError, match=r"Can't instantiate abstract class.* with abstract method.*"):
        RomanDataModel()


def test_extended_data_model_abstract():
    """
    Test to make sure the ExtendedDataModel is an abstract class so that it cannot
    be directly instantiated.
    """

    with pytest.raises(TypeError, match=r"Can't instantiate abstract class.* with abstract method.*"):
        RomanExtendedDataModel()


@pytest.mark.parametrize("model", RomanExtendedDataModel.__subclasses__())
def test_extension_models(model):
    """
    Test to make sure the extended models is an abstract class so that it cannot
    be directly instantiated.
    """

    with pytest.raises(TypeError, match=r"Can't instantiate abstract class.* with abstract method.*"):
        model()


@pytest.mark.parametrize("model", models)
def test_cannot_override_classvar(model):
    """
    Test that schema_uri and tag_uri cannot be overridden by subclasses
    """
    instance = model.make_default(_shrink=True)

    # Check that we cannot accidentally override the schema_uri on an instance
    with pytest.raises(AttributeError, match=r"'schema_uri' is a ClassVar of `.*` and cannot be set on an instance."):
        instance.schema_uri = "test"

    if issubclass(model, RomanDataModel):
        # Check that we cannot accidentally override the tag_uri on an instance
        with pytest.raises(AttributeError, match=r"'tag_uri' is a ClassVar of `.*` and cannot be set on an instance."):
            instance.tag_uri = "test"

        # Check that we cannot accidentally override the crds_observatory on an instance
        with pytest.raises(AttributeError, match=r"'crds_observatory' is a ClassVar of `.*` and cannot be set on an instance."):
            instance.crds_observatory = "test"
