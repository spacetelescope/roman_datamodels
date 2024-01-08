import asdf
import astropy.units as u
import numpy as np
import pytest
from asdf.tags.core import NDArrayType
from astropy.modeling import Model
from astropy.time import Time

from roman_datamodels.core import BaseRomanDataModel, RomanDataModel
from roman_datamodels.datamodels import _generated

__all__ = ["BaseTest", "models", "roman_models"]

models = [getattr(_generated, name) for name in _generated.__all__ if issubclass(getattr(_generated, name), BaseRomanDataModel)]
roman_models = [mdl for mdl in models if issubclass(mdl, RomanDataModel)]


class BaseTest:
    """
    Base class to contain useful methods for testing the ASDF interface
    """

    def create_instance(self, model):
        """
        Instantiate the model using the make_default
        """
        return model.make_default(_shrink=True)

    def create_filename(self, tmp_path):
        """
        Create a file path to write to
        """
        return tmp_path / "test.asdf"

    def create_model(self, model, tmp_path):
        """
        Instantiate the model and create a file path to write it to
        """
        return self.create_instance(model), self.create_filename(tmp_path)

    def create_asdf(self, model, tmp_path):
        """Create an ASDF file with the model in it"""
        instance, filename = self.create_model(model, tmp_path)
        instance.to_asdf(filename)

        return filename

    def create_dict(self, model):
        """
        Return a dictionary representation of a model instance
        """

        # Use Pydantic model_dump method to get a dictionary representation
        return self.create_instance(model).model_dump()

    def create_dummy_asdf(self, model, tmp_path):
        """
        Create a dummy ASDF file (not containing a RomanDataModel)
        """
        instance, filename = self.create_model(model, tmp_path)

        # Create a file with a non-data model in it
        asdf.AsdfFile({"foo": "bar"}).write_to(filename)

        return instance, filename

    def create_callable_path(self, tmp_path):
        """
        Create a dummy that returns a callable path
        """

        def dummy(path: str):
            return tmp_path / f"{path.replace(' ', '_')}.asdf"

        return dummy

    def check_deep_copy(self, instance, instance_copy):
        """
        Check that the copy is a deep copy
        """
        # Check the types match
        if isinstance(instance, NDArrayType):
            # The copy will induce a regular numpy array when the NDArrayType is copied
            assert isinstance(instance_copy, np.ndarray)
        else:
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

        # Asdf wrapped ndarrays need to be checked with np.all() as == does not work on its own
        elif isinstance(instance, NDArrayType):
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

    def check_shallow_copy(self, instance, instance_copy):
        """
        Check if instance is a shallow copy of instance_copy
        """

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
