"""
Run tests on writing the data models to ASDF
"""
import asdf
import pytest

from roman_datamodels.datamodels import _generated
from roman_datamodels.pydantic import RomanDataModel

models = [
    getattr(_generated, name)
    for name in _generated.__all__
    if issubclass(mdl := getattr(_generated, name), RomanDataModel) and mdl._tag_uri is not None
]


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
