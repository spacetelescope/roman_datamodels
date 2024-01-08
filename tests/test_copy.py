"""
Test copying data models
"""

import pytest

from roman_datamodels.core import DataModel

from ._helpers import BaseTest, models, roman_models


@pytest.mark.parametrize("model", models)
class TestCopy(BaseTest):
    """
    Test the copy/clone methods for data models
    """

    def test_copy(self, model):
        """
        Test creating a copy of the model
        """
        instance = self.create_instance(model)

        instance_copy = instance.copy()

        # Check that the copy is a different object
        assert instance is not instance_copy

        # Check that the copy is a deep copy
        self.check_deep_copy(instance, instance_copy)

        # Check additional features of RomanDataModel
        if issubclass(model, DataModel):
            instance_copy._asdf_external = True
            instance_copy._asdf is None

    def test_shallow_copy(self, model):
        """
        Test creating a shallow copy of the model
        """
        instance = self.create_instance(model)

        instance_copy = instance.copy(deepcopy=False)

        self.check_shallow_copy(instance, instance_copy)

        # Check additional features of RomanDataModel
        if issubclass(model, DataModel):
            instance_copy._asdf_external = True
            instance_copy._asdf is None


@pytest.mark.parametrize("model", roman_models)
class TestRomanCopy(BaseTest):
    """
    Test copy for specific roman data models
        Most of this is already tested in TestCopy, but the RomanDataModels have extended functionality
    """

    def test_copy_asdf_base(self, model, tmp_path):
        """
        Test copy model built from ASDF file
        """

        filename = self.create_asdf(model, tmp_path)

        with model.from_asdf(filename) as instance:
            # Sanity checks
            assert isinstance(instance, model)
            assert instance._asdf is not None
            assert instance._asdf_external is False
            assert instance._asdf.tree["roman"] is instance

            # make copy
            instance_copy = instance.copy()
            assert isinstance(instance_copy, model)

            assert instance_copy is not instance

            assert instance_copy._asdf is not None
            assert instance_copy._asdf is not instance._asdf
            assert instance_copy._asdf_external is True
            assert instance_copy._asdf.tree["roman"] is instance_copy

            self.check_deep_copy(instance, instance_copy)
