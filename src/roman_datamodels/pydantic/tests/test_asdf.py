"""
Run tests on writing the data models to ASDF
"""
import asdf
import pytest

from roman_datamodels.datamodels import _generated
from roman_datamodels.datamodels.datamodel import RomanDataModel

models = [
    getattr(_generated, name)
    for name in _generated.__all__
    if issubclass(mdl := getattr(_generated, name), RomanDataModel) and mdl.tag_uri is not None
]


# TODO: change to using .to_asdf() later
@pytest.mark.parametrize("model", models)
def test_write_asdf(model, tmp_path):
    """
    Test that reading and writing the model to ASDF doesn't raise an error.
        This is only a face value check, not an exactness check.
    """

    filename = tmp_path / "test.asdf"

    # _shrink=True is used to limit testing memory use
    af = asdf.AsdfFile({"roman_datamodel": model.make_default(_shrink=True)})
    af.write_to(filename)

    with asdf.open(filename) as af:
        assert isinstance(af["roman_datamodel"], model)


def test_observation(tmp_path):
    """
    Test that the aliased field "pass" in Observation is written as "pass" not its
    python field name (python syntax reasons) "pass_".
    """

    filename = tmp_path / "test.asdf"

    # _shrink=True is used to limit testing memory use
    af = asdf.AsdfFile({"roman_datamodel": _generated.Observation.make_default(_shrink=True)})
    af.write_to(filename)

    # Force raw types so we can look at the ASDF tree itself
    with asdf.open(filename, _force_raw_types=True) as af:
        assert "pass" in af.tree["roman_datamodel"]
        assert "pass_" not in af.tree["roman_datamodel"]

        assert af.tree["roman_datamodel"]["pass"] == -999999


@pytest.mark.parametrize("model", models)
def test_extras(model, tmp_path):
    """
    Test that we can add, write, and read-back extra data to a model.
    """

    filename = tmp_path / "test.asdf"

    # _shrink=True is used to limit testing memory use
    instance = model.make_default(_shrink=True)

    # Add extra field and check that it is there
    instance.foo = "bar"
    assert instance.foo == "bar"

    # Write to ASDF
    af = asdf.AsdfFile({"roman_datamodel": instance})
    af.write_to(filename)

    # Read back from ASDF contains the extra field
    with asdf.open(filename) as af:
        assert isinstance(af["roman_datamodel"], model)
        new_instance = af["roman_datamodel"]
        assert new_instance.foo == "bar"


@pytest.mark.parametrize("model", models)
class TestFromAsdf:
    """
    Test the from_asdf class method
    """

    def create_asdf(self, model, tmp_path):
        """Create an ASDF file with the model in it"""
        filename = tmp_path / "test.asdf"

        # Write to ASDF
        af = asdf.AsdfFile({"roman": model.make_default(_shrink=True)})  # TODO: change to using .to_asdf() later
        af.write_to(filename)
        af.close()

        return filename

    def test_file_name_str(self, model, tmp_path):
        """
        Test that we can read a model from a file name
        """
        filename = self.create_asdf(model, tmp_path)

        # Read back using RomanDataModel.from_asdf
        with RomanDataModel.from_asdf(str(filename)) as instance:
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

    def test_file_name_path(self, model, tmp_path):
        """
        Test that we can read a model from a file name
        """
        filename = self.create_asdf(model, tmp_path)

        # Read back using RomanDataModel.from_asdf
        with RomanDataModel.from_asdf(filename) as instance:
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
        Test that we can read a model from an ASDF file
        """
        filename = self.create_asdf(model, tmp_path)

        # Get the ASDF file
        with asdf.open(filename) as af:
            # Read back using from_asdf (asdf.AsdfFile)
            with RomanDataModel.from_asdf(af) as instance:
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
        with pytest.raises(TypeError, match=r"Can't instantiate abstract class.* with abstract method.*"):
            RomanDataModel.from_asdf()

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
        with pytest.raises(TypeError, match=r"Expected file to be a string, Path, asdf.AsdfFile, or None"):
            RomanDataModel.from_asdf(42)

        # Using model.from_asdf
        with pytest.raises(TypeError, match=r"Expected file to be a string, Path, asdf.AsdfFile, or None"):
            model.from_asdf(42)

    def test_wrong_model_type(self, model, tmp_path):
        """
        Test that we raise an error if the model is not of the correct type (when opening with a specific model class)
        """
        filename = self.create_asdf(model, tmp_path)

        # Get a different model class
        other_model = models[models.index(model) - 1]
        assert other_model is not model  # Sanity check

        # Try to open the file with the wrong model class
        with pytest.raises(TypeError, match=r"Expected file containing model of type.*, got.*"):
            other_model.from_asdf(filename)
