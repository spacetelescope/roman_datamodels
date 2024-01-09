"""
Tests related to the ASDF interface for RomanDataModel
"""
from pathlib import Path
from unittest import mock

import asdf
import pytest

from roman_datamodels.core import DataModel
from roman_datamodels.datamodels import _generated

from ._helpers import BaseTest, roman_models


@pytest.mark.parametrize("model", roman_models)
class TestOpenAsdf(BaseTest):
    """
    Test the open_asdf method
    """

    def test_str(self, model, tmp_path):
        """
        Test that we can open an ASDF file represented by a str
        """
        instance, filename = self.create_dummy_asdf(model, tmp_path)

        # Open the ASDF file
        af = instance.open_asdf(str(filename))
        assert isinstance(af, asdf.AsdfFile)
        assert af.tree["foo"] == "bar"

        # Have to close this because open_asdf doesn't close it on purpose
        af.close()

    def test_path(self, model, tmp_path):
        """
        Test that we can open an ASDF file represented by a path
        """
        instance, filename = self.create_dummy_asdf(model, tmp_path)
        assert isinstance(filename, Path)

        # Open the ASDF file
        af = instance.open_asdf(filename)
        assert isinstance(af, asdf.AsdfFile)
        assert af.tree["foo"] == "bar"

        # Have to close this because open_asdf doesn't close it on purpose
        af.close()

    def test_asdf_file(self, model, tmp_path):
        """
        Test that we can open an existing ASDF file
        """
        instance, filename = self.create_dummy_asdf(model, tmp_path)

        # Open the ASDF file with asdf
        with asdf.open(filename) as af:
            # Now open with open_asdf
            new_af = instance.open_asdf(af)

            assert isinstance(new_af, asdf.AsdfFile)
            assert new_af.tree["foo"] == "bar"

    def test_none(self, model, tmp_path):
        """
        Test that we can open nothing
        """
        instance, _ = self.create_dummy_asdf(model, tmp_path)

        # Open nothing
        af = instance.open_asdf()
        assert isinstance(af, asdf.AsdfFile)
        assert af.tree == {}


@pytest.mark.parametrize("model", roman_models)
class TestToAsdf(BaseTest):
    """
    Test the to_asdf method
    """

    def test_str(self, model, tmp_path):
        """
        Test writing a model to a file represented by a str
        """
        instance, filename = self.create_model(model, tmp_path)

        # Write to ASDF
        #     This is also testing the asdf converter can serialize the model
        af = instance.to_asdf(str(filename))

        # Check that the asdf file created contains the model
        assert isinstance(af, asdf.AsdfFile)
        assert af.tree["roman"] is instance

        # Check that the written file is then readable
        #    Note .from_asdf is not used so that issues with .to_asdf can be debugged
        #    independently using the tests.
        # This also check the asdf converter can deserialize to the model
        #    This is only a face value check, not a round trip check.
        with asdf.open(filename) as af:
            assert isinstance(af["roman"], model)

    def test_path(self, model, tmp_path):
        """
        Test writing a model to a file represented by a str
        """
        instance, filename = self.create_model(model, tmp_path)
        assert isinstance(filename, Path)

        # Write to ASDF
        #     This is also testing the asdf converter can serialize the model
        af = instance.to_asdf(filename)

        # Check that the asdf file created contains the model
        assert isinstance(af, asdf.AsdfFile)
        assert af.tree["roman"] is instance

        # Check that the written file is then readable
        #    Note .from_asdf is not used so that issues with .to_asdf can be debugged
        #    independently using the tests.
        # This also check the asdf converter can deserialize to the model
        #    This is only a face value check, not a round trip check.
        with asdf.open(filename) as af:
            assert isinstance(af["roman"], model)

    def test_other_input(self, model):
        """
        Test that we raise an error if the input is not a string, Path, or asdf.AsdfFile
        """
        with pytest.raises(TypeError, match=r"Expected file to be a string or Path; not.*"):
            model.make_default(_shrink=True).to_asdf(mock.MagicMock())

    def test_includes_extras(self, model, tmp_path):
        """
        Test that we can add, write, and read-back extra data to a model.
        """
        instance, filename = self.create_model(model, tmp_path)

        # Add extra field and check that it is there
        #    Note this shows the `extra="allow"` configuration option is enabled
        instance.foo = "bar"
        assert instance.foo == "bar"

        # Write to ASDF
        instance.to_asdf(filename)

        # Read back from ASDF contains the extra field
        #    Note this is a partial round trip check, as it shows that at least one
        #    field (the extra one) is round tripped.
        with asdf.open(filename) as af:
            assert isinstance(af["roman"], model)
            assert af["roman"].foo == "bar"

    def test_proper_filename(self, model, tmp_path):
        """
        Test that the filename in the meta is updated when writing to a file
        """
        instance, filename = self.create_model(model, tmp_path)

        # Note only models with meta.filename will have this behavior
        if instance._has_filename:
            assert instance.meta.filename != filename

            current_filename = instance.meta.filename

            # Write to ASDF
            instance.to_asdf(filename)

            # Check that the filename in the meta is not updated
            assert instance.meta.filename == current_filename

            # Read back from ASDF and check that the filename in the meta is updated
            #    to reflect the name of the file that it was written to
            with asdf.open(filename) as af:
                assert isinstance(af["roman"], model)
                assert af["roman"].meta.filename == filename.name

    def test_make_default(self, model, tmp_path):
        """
        Test saving the model to an asdf file as part of model generation
            Basically this method is an extension of previously tested functionality
            byt the tests in test_default.py. The extension is just calling to_asdf
            on the resulting default model.
        """
        filename = self.create_filename(tmp_path)

        # Create the model and save it to an ASDF file
        instance = model.make_default(_shrink=True, filepath=filename)
        assert isinstance(instance, model)

        # Read back from ASDF and check that the filename in the meta is updated
        #    to reflect the name of the file that it was written to
        with asdf.open(filename) as af:
            assert isinstance(af["roman"], model)


def test_observation(tmp_path):
    """
    Test that the aliased field "pass" in Observation is written as "pass" not its
    python field name (python syntax reasons) "pass_".
    """

    filename = tmp_path / "test.asdf"
    model = _generated.Observation.make_default(_shrink=True)
    model.to_asdf(filename)

    # Force raw types so we can look at the ASDF tree itself
    with asdf.open(filename, _force_raw_types=True) as af:
        # Check that the data is correctly written under pass not pass
        assert "pass" in af.tree["roman"]
        assert "pass_" not in af.tree["roman"]
        assert af.tree["roman"]["pass"] == -999999 == model.pass_


@pytest.mark.parametrize("model", roman_models)
class TestFromAsdf(BaseTest):
    """
    Test the from_asdf class method
    """

    def test_str(self, model, tmp_path):
        """
        Test that we can read a model from a file represented by a str
        """
        filename = self.create_asdf(model, tmp_path)

        # Read back using RomanDataModel.from_asdf
        with DataModel.from_asdf(str(filename)) as instance:
            assert isinstance(instance, model)
            assert instance._asdf_external is False
            assert instance._asdf is not None
            assert isinstance(instance._asdf, asdf.AsdfFile)

        # Read back using model.from_asdf
        with model.from_asdf(str(filename)) as instance:
            assert isinstance(instance, model)
            assert instance._asdf_external is False
            assert instance._asdf is not None
            assert isinstance(instance._asdf, asdf.AsdfFile)

    def test_path(self, model, tmp_path):
        """
        Test that we can read a model from a file represented by a path
        """
        filename = self.create_asdf(model, tmp_path)
        assert isinstance(filename, Path)

        # Read back using RomanDataModel.from_asdf
        with DataModel.from_asdf(filename) as instance:
            assert isinstance(instance, model)
            assert instance._asdf_external is False
            assert instance._asdf is not None
            assert isinstance(instance._asdf, asdf.AsdfFile)

        # Read back using model.from_asdf
        with model.from_asdf(filename) as instance:
            assert isinstance(instance, model)
            assert instance._asdf_external is False
            assert instance._asdf is not None
            assert isinstance(instance._asdf, asdf.AsdfFile)

    def test_asdf_file(self, model, tmp_path):
        """
        Test that we can read a model from an existing ASDF file
        """
        filename = self.create_asdf(model, tmp_path)

        # Get the ASDF file
        with asdf.open(filename) as af:
            # Read back using from_asdf (asdf.AsdfFile)
            with DataModel.from_asdf(af) as instance:
                assert isinstance(instance, model)
                assert instance._asdf_external is True
                assert instance._asdf is af

            # Read back using model.from_asdf
            with model.from_asdf(af) as instance:
                assert isinstance(instance, model)
                assert instance._asdf_external is True
                assert instance._asdf is af

    def test_none(self, model):
        """
        Test that we can create a default model if no file is provided
        """

        # RomanDataModel can't actually create a default instance, so this should fail
        with pytest.raises(TypeError, match=r"Can't instantiate abstract class.*"):
            DataModel.from_asdf()

        # Open using the model class directly (this will raise a warning).
        with pytest.warns(UserWarning, match=r"No file provided, creating default model"), model.from_asdf() as instance:
            assert isinstance(instance, model)
            assert instance._asdf_external is True
            assert instance._asdf is None

    def test_other_input(self, model):
        """
        Test that we raise an error if the input is not a string, Path, or asdf.AsdfFile
        """

        # Using RomanDataModel.from_asdf
        with pytest.raises(TypeError, match=r"Expected file to be a string, Path, asdf.AsdfFile, or None; not.*"):
            DataModel.from_asdf(mock.MagicMock())

        # Using model.from_asdf
        with pytest.raises(TypeError, match=r"Expected file to be a string, Path, asdf.AsdfFile, or None; not.*"):
            model.from_asdf(mock.MagicMock())

    def test_wrong_model_type(self, model, tmp_path):
        """
        Test that we raise an error if the model is not of the correct type (when opening with a specific model class)
        """
        filename = self.create_asdf(model, tmp_path)

        # Get a different model class
        other_model = roman_models[roman_models.index(model) - 1]
        assert other_model is not model  # Sanity check

        # Try to open the file with the wrong model class
        with pytest.raises(TypeError, match=r"Expected file containing model of type.*, got.*"):
            other_model.from_asdf(filename)

    def test_open_non_data_model_file(self, model, tmp_path):
        """
        Test that we catch if the file doesn't contain a data model and close the model.
            This test assumes we pass a str/Path to RomanDataModel.from_asdf (not an open asdf.AsdfFile)
            pytest will raise a file not closed error if we don't close the file.
        """
        _, filename = self.create_dummy_asdf(model, tmp_path)

        # Try to open the file with RomanDataModel.from_asdf
        with pytest.raises(KeyError, match=r".*from_asdf expects a file with a 'roman' key"):
            DataModel.from_asdf(filename)

        # Try to open the file with model.from_asdf
        with pytest.raises(KeyError, match=r".*from_asdf expects a file with a 'roman' key"):
            model.from_asdf(filename)

    def test_open_non_data_model_asdf_file(self, model, tmp_path):
        """
        Test that we catch if the file doesn't contain a data model and close the model.
            This test assumes we pass an open asdf.AsdfFile to RomanDataModel.from_asdf.
        """
        _, filename = self.create_dummy_asdf(model, tmp_path)

        with asdf.open(filename) as af:
            # Try to open the file with RomanDataModel.from_asdf
            with pytest.raises(KeyError, match=r".*from_asdf expects a file with a 'roman' key"):
                DataModel.from_asdf(af)

            # Try to open the file with model.from_asdf
            with pytest.raises(KeyError, match=r".*from_asdf expects a file with a 'roman' key"):
                model.from_asdf(af)

            # Check if ASDF believes the file is closed (it shouldn't be)
            #    Note that it has been requested that this be made public in asdf
            assert af._closed is False


@pytest.mark.parametrize("model", roman_models)
class TestCreateModel(BaseTest):
    """
    Test the create_model class method
    """

    def test_data_model(self, model):
        """
        Test that if we pass an existing model, we get the same model back
        """
        existing = self.create_instance(model)

        # Call create model from RomanDataModel
        with DataModel.create_model(existing) as instance:
            assert instance is existing

        # Call create model from model
        with model.create_model(existing) as instance:
            assert instance is existing

    def test_wrong_model_type(self, model):
        """
        Test that we raise an error if the model is not of the correct type (when opening with a specific model class)
        """
        existing = self.create_instance(model)

        # Get a different model class
        other_model = roman_models[roman_models.index(model) - 1]
        assert other_model is not model  # Sanity check

        # Try to open the file with the wrong model class
        with pytest.raises(TypeError, match=r"Expected model of type.*, got.*"):
            other_model.create_model(existing)

    def test_asdf_file_like(self, model, tmp_path):
        """
        Test that if we pass a str/Path/asdf-file/None, we get the correct model back
            This is a pass down to the from_asdf class method.
        """
        filename = self.create_asdf(model, tmp_path)

        # str/Path
        with DataModel.create_model(str(filename)) as instance:
            assert isinstance(instance, model)
            assert instance._asdf_external is False
            assert instance._asdf is not None
            assert isinstance(instance._asdf, asdf.AsdfFile)

        with model.create_model(str(filename)) as instance:
            assert isinstance(instance, model)
            assert instance._asdf_external is False
            assert instance._asdf is not None
            assert isinstance(instance._asdf, asdf.AsdfFile)

        # asdf.AsdfFile
        with asdf.open(filename) as af:
            with DataModel.create_model(af) as instance:
                assert isinstance(instance, model)
                assert instance._asdf_external is True
                assert instance._asdf is af

            with model.create_model(af) as instance:
                assert isinstance(instance, model)
                assert instance._asdf_external is True
                assert instance._asdf is af

        # None
        with pytest.warns(UserWarning, match=r"No file provided, creating default model"), model.create_model(None) as instance:
            assert isinstance(instance, model)
            assert instance._asdf_external is True
            assert instance._asdf is None

    def test_dict(self, model):
        """
        Test that if we pass a dictionary, we get the correct model back
        """
        dict = self.create_dict(model)

        with model.create_model(dict) as instance:
            assert isinstance(instance, model)
            assert instance._asdf_external is True
            assert instance._asdf is None


@pytest.mark.parametrize("model", roman_models)
class TestSave(BaseTest):
    """
    Test the save interface for stpipe
    """

    def test_str(self, model, tmp_path):
        """
        Test with string path
        """
        instance, filename = self.create_model(model, tmp_path)

        # Test saving the model and check that the output filename is correct
        assert instance.save(str(filename)) == filename

        # Check that the written file is then readable
        with DataModel.from_asdf(filename) as instance:
            assert isinstance(instance, model)

    def test_str_dir_path(self, model, tmp_path):
        """
        Test with string path and directory path
        """
        instance, filename = self.create_model(model, tmp_path)

        # Create a directory path
        dir_path = tmp_path / "test"
        dir_path.mkdir(exist_ok=True)

        # Test saving the model and check that the output filename is correct
        assert (output_path := instance.save(str(filename), dir_path=dir_path)) == dir_path / filename.name

        # Check that the written file is then readable
        with DataModel.from_asdf(output_path) as instance:
            assert isinstance(instance, model)

    def test_path(self, model, tmp_path):
        """
        Test with path
        """
        instance, filename = self.create_model(model, tmp_path)

        # Test saving the model and check that the output filename is correct
        assert instance.save(filename) == filename

        # Check that the written file is then readable
        with DataModel.from_asdf(filename) as instance:
            assert isinstance(instance, model)

    def test_path_dir_path(self, model, tmp_path):
        """
        Test with path and directory path
        """
        instance, filename = self.create_model(model, tmp_path)

        # Create a directory path
        dir_path = tmp_path / "test"
        dir_path.mkdir(exist_ok=True)

        # Test saving the model and check that the output filename is correct
        assert (output_path := instance.save(filename, dir_path=dir_path)) == dir_path / filename.name

        # Check that the written file is then readable
        with DataModel.from_asdf(output_path) as instance:
            assert isinstance(instance, model)

    def test_callable(self, model, tmp_path):
        """
        Test with callable
        """
        instance, _ = self.create_model(model, tmp_path)
        path = self.create_callable_path(tmp_path)

        if instance._has_filename:
            # Test saving the model and check that the output filename is correct
            #    This can only happen if the model has a filename attribute
            assert (output_path := instance.save(path)) == tmp_path / "dummy_value.asdf"

            # Check that the written file is then readable
            with DataModel.from_asdf(output_path) as instance:
                assert isinstance(instance, model)
        else:
            # Test that we raise an error if the model doesn't have a filename attribute
            with pytest.raises(ValueError, match=r"Cannot use a Callable path if the model does not have a filename attribute"):
                instance.save(path)

    def test_callable_dir_path(self, model, tmp_path):
        """
        Test with callable and directory path
        """
        instance, filename = self.create_model(model, tmp_path)
        path = self.create_callable_path(tmp_path)

        # Create a directory path
        dir_path = tmp_path / "test"
        dir_path.mkdir(exist_ok=True)

        if instance._has_filename:
            # Test saving the model and check that the output filename is correct
            #    This can only happen if the model has a filename attribute
            assert (output_path := instance.save(path, dir_path=dir_path)) == dir_path / "dummy_value.asdf"

            # Check that the written file is then readable
            with DataModel.from_asdf(output_path) as instance:
                assert isinstance(instance, model)
        else:
            # Test that we raise an error if the model doesn't have a filename attribute
            with pytest.raises(ValueError, match=r"Cannot use a Callable path if the model does not have a filename attribute"):
                instance.save(path, dir_path=dir_path)


@pytest.mark.parametrize("model", roman_models)
class TestAsdfPassThrough(BaseTest):
    """
    Test all the passthrough methods to ASDF
    """

    def test_asdf_validate(self, model):
        """
        Test that we can run validate on the model via ASDF
        """
        instance = self.create_instance(model)

        # The default models should not have an associated ASDF file
        assert instance._asdf is None
        assert instance._asdf_external is True

        # Run validate via ASDF
        instance.asdf_validate()

        # There should now be an associated ASDF file
        assert instance._asdf is not None
        assert instance._asdf_external is False
        assert isinstance(instance._asdf, asdf.AsdfFile)
        assert instance._asdf.tree["roman"] is instance

    def test_do_not_override_asdf_file(self, model, tmp_path):
        """
        Test that we do not override an existing ASDF file
        """
        filename = self.create_asdf(model, tmp_path)

        # Read the model via ASDF
        with DataModel.from_asdf(filename) as instance:
            # Check the state of the AsdfFile object
            assert instance._asdf is not None
            assert instance._asdf_external is False

            # Grab the asdf file object
            asdf_file = instance._asdf

            # Call the pass down property (._asdf_file) used to access the ASDF file
            assert instance._asdf_file is instance._asdf
            assert instance._asdf is asdf_file

    def test_info(self, model, capsys):
        """
        Test that we can call down into the ASDF info method
        """
        instance = self.create_instance(model)

        # info displays to standard out/err so we need to capture it
        instance.info()
        captured = capsys.readouterr()
        stdout = captured.out
        stderr = captured.err

        # Ensure we captured something (sanity check), stderr should be nothing as
        #    info should have succeeded
        assert stdout
        assert stderr == ""

        # Info should be the same as if we ran it directly on the AsdfFile object
        instance._asdf.info()
        captured = capsys.readouterr()
        assert captured.out == stdout
        assert captured.err == stderr

    def test_search(self, model):
        """
        Test that we can call down into the ASDF search method
        """
        instance = self.create_instance(model)

        # search returns an AsdfSearchResult object which has no __eq__ method;
        #    however, it is intended to be printed for human consumption so we can
        #    compare the string representations.
        assert repr(instance.search("roman")) == repr(instance._asdf.search("roman"))

    def test_schema_info(self, model):
        """
        Test that we can call down to the ASDF search schema method
        """
        instance = self.create_instance(model)

        # schema_info returns a nested dictionary of strings, so we can directly compare the results
        assert instance.schema_info("archive_catalog") == instance._asdf.schema_info("archive_catalog")
