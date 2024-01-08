"""
Tests of the extended models functionality
"""
import pytest

from roman_datamodels.core import RomanExtendedDataModel
from roman_datamodels.datamodels import _generated

models = [
    getattr(_generated, name)
    for name in _generated.__all__
    if issubclass(mdl := getattr(_generated, name), RomanExtendedDataModel)
]


@pytest.mark.parametrize("model", models)
def test_extended_model_base_class_name(model):
    """
    Check the name of the base class won't cause issues, this enforces the naming convention.
    """

    assert (base_cls := model.__bases__[0]) is RomanExtendedDataModel.model_from_schema_uri(model.schema_uri)
    assert base_cls.__name__.startswith("_")
    assert base_cls.__name__[1:] == model.__name__


class TestWfiMode:
    """
    Test the _WfiMode model
    """

    def test_filter(self):
        """
        Test the filter property
        """
        instance = _generated.WfiMode.make_default(_shrink=True)

        # By default we get the first filter "F062" set
        assert instance.filter == "F062"

        # Set the optical element to be a grating
        instance.optical_element = "GRISM"
        assert instance.filter is None

    def test_grating(self):
        """
        Test the grating property
        """
        instance = _generated.WfiMode.make_default(_shrink=True)

        # By default we get the first filter "F062" set
        assert instance.grating is None

        # Set the optical element to be a grating
        instance.optical_element = "GRISM"
        assert instance.grating == "GRISM"


class TestRampModel:
    """
    Test the _RampModel model
    """

    def test_from_science_raw(self):
        """
        Test the from_science_raw method, using the WfiScienceRawModel
        """
        science = _generated.WfiScienceRawModel.make_default(_shrink=True)
        instance = _generated.RampModel.from_science_raw(science, _shrink=True)

        assert isinstance(instance, _generated.RampModel)
        assert instance.amp33 is science.amp33

    def test_from_science_raw_from_ramp_model(self):
        """
        Test the from_science_raw method, using the RampModel
        """
        ramp = _generated.RampModel.make_default(_shrink=True)
        instance = _generated.RampModel.from_science_raw(ramp, _shrink=True)

        # Check that we just pass the input through
        assert instance is ramp


class TestAssociationsModel:
    """
    Test the _AssociationsModel model
    """

    def test_is_association(self):
        """
        Test the is_association method
        """

        # Create "valid" association data
        asn_data = {
            "asn_id": "foo",
            "asn_pool": "bar",
        }
        assert _generated.AssociationsModel.is_association(asn_data)

        # Remove the "asn_pool" field
        asn_data.pop("asn_pool")
        assert not _generated.AssociationsModel.is_association(asn_data)

        # Remove the "asn_id" field
        asn_data.pop("asn_id")
        assert not _generated.AssociationsModel.is_association(asn_data)

        # Pass a non_dict
        assert not _generated.AssociationsModel.is_association("foo")


class TestLinearityRefModel:
    """
    Test the _LinearityRefModel model
    """

    def test_get_primary_array_name(self):
        """
        Test the get_primary_array_name method
        """
        instance = _generated.LinearityRefModel.make_default(_shrink=True)

        assert instance.get_primary_array_name() == "coeffs"


class TestInverselinearityRefModel:
    """
    Test the _InverselinearityRefModel model
    """

    def test_get_primary_array_name(self):
        """
        Test the get_primary_array_name method
        """
        instance = _generated.InverselinearityRefModel.make_default(_shrink=True)

        assert instance.get_primary_array_name() == "coeffs"


class TestMaskRefModel:
    """
    Test the _MaskRefModel model
    """

    def test_get_primary_array_name(self):
        """
        Test the get_primary_array_name method
        """
        instance = _generated.MaskRefModel.make_default(_shrink=True)

        assert instance.get_primary_array_name() == "dq"
