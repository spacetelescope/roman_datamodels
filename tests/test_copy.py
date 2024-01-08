"""
Test copying data models
"""

import astropy.units as u
import numpy as np
import pytest
from astropy.modeling import Model
from astropy.time import Time

from roman_datamodels.datamodels import _generated
from roman_datamodels.pydantic import BaseRomanDataModel

models = [getattr(_generated, name) for name in _generated.__all__ if issubclass(getattr(_generated, name), BaseRomanDataModel)]


@pytest.mark.parametrize("model", models)
class TestCopy:
    """
    Test the copy/clone methods for data models
    """

    def create_instance(self, model):
        """
        Create an instance of the model
        """
        return model.make_default(_shrink=True)

    def check_deep_copy(self, instance, instance_copy):
        """
        Check that the copy is a deep copy
        """
        # Check the types match
        assert isinstance(instance, type(instance_copy))

        # Loop over attributes if the instance is a data model
        if isinstance(instance, BaseRomanDataModel):
            assert instance is not instance_copy

            for name, value in instance:
                self.check_deep_copy(value, instance_copy[name])

        # Loop over attributes if the instance is a dict
        elif isinstance(instance, dict):
            assert instance is not instance_copy

            for name, value in instance.items():
                self.check_deep_copy(value, instance_copy[name])

        # Loop over attributes if the instance is a list
        elif isinstance(instance, list):
            assert instance is not instance_copy
            for value, value_copy in zip(instance, instance_copy):
                self.check_deep_copy(value, value_copy)

        # ndarrays need to be checked with np.all() as == does not work on its own
        elif isinstance(instance, np.ndarray):
            assert instance is not instance_copy
            assert (instance == instance_copy).all()

        # catch scalar quantities
        elif isinstance(instance, u.Quantity):
            assert instance is not instance_copy
            assert instance == instance_copy

        # catch times
        elif isinstance(instance, Time):
            assert instance is not instance_copy
            assert instance == instance_copy

        # catch astropy models
        elif isinstance(instance, Model):
            # models don't have an easy == method, so just check that are different objects
            assert instance is not instance_copy

        else:
            # Check everything else
            try:
                # Check the instances try:
                # Hashable objects cannot be copied as they are immutable.
                hash(instance)
            except TypeError:
                # mutable objects, so check that they are not the same object
                assert instance is not instance_copy
            else:
                # immutable objects, so check that they are the same object
                assert instance is instance_copy

            assert instance == instance_copy

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

    def test_shallow_copy(self, model):
        """
        Test creating a shallow copy of the model
        """
        instance = self.create_instance(model)

        instance_copy = instance.copy(deepcopy=False)

        assert instance == instance_copy

        # Check that the copy is a different object
        assert instance is not instance_copy

        # Check that the copy is a shallow copy
        #    Note that if the model does not have any sub-models, then the copy
        #    will be a deep copy.
        for _, value in instance:
            if isinstance(value, BaseRomanDataModel):
                with pytest.raises(AssertionError):
                    # Check that the copy is not a deep copy
                    self.check_deep_copy(instance, instance_copy)

                break
