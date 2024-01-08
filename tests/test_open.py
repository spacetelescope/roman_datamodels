from pathlib import Path

import asdf
import astropy.units as u
import pytest
from astropy.io import fits
from pydantic import ValidationError

from roman_datamodels import datamodels as rdm

from ._helpers import BaseTest, roman_models


@pytest.mark.parametrize("model", roman_models)
class TestOpen(BaseTest):
    """
    Test the RDM open function
    """

    def test_file_path(self, model, tmp_path):
        """
        Test opening model from ASDF file path
        """
        filename = self.create_asdf(model, tmp_path)

        with rdm.open(filename) as instance:
            assert isinstance(instance, model)
            assert instance._asdf_external is False
            assert instance._asdf is not None

    def test_asdf_file(self, model, tmp_path):
        """
        Test opening model from asdf file object
        """
        filename = self.create_asdf(model, tmp_path)

        with asdf.open(filename) as af:
            with rdm.open(af) as instance:
                assert isinstance(instance, model)
                assert instance._asdf_external is True
                assert instance._asdf is af

    def test_existing(self, model):
        """
        Test opening model from existing model
        """
        existing = self.create_instance(model)

        with rdm.open(existing) as instance:
            assert isinstance(instance, model)

            self.check_shallow_copy(existing, instance)

    def test_memmap(self, model, tmp_path):
        """
        Test opening with memmap
        """
        existing, filename = self.create_model(model, tmp_path)
        existing.to_asdf(filename)

        # Only effects models with a primary array
        if (name := existing.get_primary_array_name()) is not None:
            # Manufacture some new data
            new_data = existing[name].copy()
            item = tuple(0 for _ in new_data.shape)
            unit = new_data.unit if isinstance(new_data, u.Quantity) else 1
            new_data[item] = 42 * unit

            # Sanity check
            assert (new_data != existing[name]).any()

            # Since quantities (some model arrays are quantities some are ndarrays) don't inherit
            # from np.memmap we have to test they are effectively memmaped.
            # rw mode needed because we have to test the memmap by manipulating the data on disk.

            # Open the file and update the data using a memmap
            with rdm.open(filename, memmap=True, mode="rw") as instance:
                # Check that the read data is the same
                assert (instance[name] == existing[name]).all()

                # Sanity check
                assert instance[name][item] != new_data[item]

                # Update the value (full assignment to avoid segfaults)
                instance[name][item] = new_data[item]

                # Check the assignment
                assert (instance[name] == new_data).all()
                assert (instance[name] != existing[name]).any()

                # Note that there has been no attempt to save the data back to the file

            # Reopen the file and check the memmap updated the file
            with rdm.open(filename) as instance:
                assert (instance[name] == new_data).all()
                assert (instance[name] != existing[name]).any()

    @pytest.mark.parametrize("kwargs", [{}, {"memmap": False}])
    def test_no_memmap(self, model, tmp_path, kwargs):
        """
        Test opening with memmap off
            memmap is off by default
        """

        existing, filename = self.create_model(model, tmp_path)
        existing.to_asdf(filename)

        # Only effects models with a primary array
        if (name := existing.get_primary_array_name()) is not None:
            # Manufacture some new data
            new_data = existing[name].copy()
            item = tuple(0 for _ in new_data.shape)
            unit = new_data.unit if isinstance(new_data, u.Quantity) else 1
            new_data[item] = 42 * unit

            # Sanity check
            assert (new_data != existing[name]).any()

            # Since quantities (some model arrays are quantities some are ndarrays) don't inherit
            # from np.memmap we have to test they are effectively memmaped.
            # rw mode needed because we have to test for a memmap by manipulating the data on disk.

            # Open the file and update the data using a memmap
            with rdm.open(filename, mode="rw", **kwargs) as instance:
                # Check that the read data is the same
                assert (instance[name] == existing[name]).all()

                # Sanity check
                assert instance[name][item] != new_data[item]

                # Update the value (full assignment to avoid segfaults)
                instance[name][item] = new_data[item]

                # Check the assignment
                assert (instance[name] == new_data).all()
                assert (instance[name] != existing[name]).any()

                # Note that there has been no attempt to save the data back to the file

            # Reopen the file and check the memmap updated the file
            with rdm.open(filename) as instance:
                assert (instance[name] != new_data).any()
                assert (instance[name] == existing[name]).all()


def test_open_json(tmp_path):
    """
    Test opening a json file, assuming its an ASN
    """
    init = tmp_path / "init.json"

    assert init == rdm.open(init)


def test_open_path(tmp_path):
    """
    Test opening a path
    """
    with pytest.raises(ValueError, match=r"Input file path does not have an extension: .*"):
        rdm.open(tmp_path)


# Turn off warnings for this test (deprecation warnings are raised by the converter for the file used)
@pytest.mark.filterwarnings("ignore:")
def test_read_pattern_properties():
    """
    Regression test for reading pattern properties
    """

    # This file has been modified by hand to break the `photmjsr` value
    with pytest.raises(ValidationError):
        rdm.open(Path(__file__).parent / "data" / "photmjsm.asdf")


def test_rdm_open_non_datamodel():
    """
    Test that opening a non-roman data model raises an error
    """
    # This is not a roman datamodel
    with pytest.raises(TypeError, match=r"Expected file containing model of type .*, got .*"):
        rdm.open(Path(__file__).parent / "data" / "not_a_datamodel.asdf")


def test_invalid_input():
    with pytest.raises(TypeError):
        rdm.open(fits.HDUList())
