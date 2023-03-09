import asdf
import astropy.units as u
import pytest
from asdf.testing.helpers import yaml_to_asdf

with pytest.warns(DeprecationWarning, match=r"The roman_datamodels.units module is deprecated. Use astropy.units instead"):
    from roman_datamodels import units


@pytest.mark.parametrize("unit", units.__all__)
def test_units(unit):
    assert getattr(units, unit) == getattr(u, unit)


@pytest.mark.parametrize("unit", units.__all__)
def test_base_roman_unit(unit):
    """Test deserialization of a base legacy Roman units"""
    yaml = f"""
unit: !<asdf://stsci.edu/datamodels/roman/tags/unit-1.0.0> {unit}
    """

    buff = yaml_to_asdf(yaml)
    with asdf.open(buff) as af:
        assert af["unit"] == getattr(u, unit)


@pytest.mark.parametrize("unit", ["electron / s", "electron2 / s2", "electron / DN"])
def test_compound_roman_unit(unit):
    """Test deserialization of a compound Roman units"""
    yaml = f"""
unit: !<asdf://stsci.edu/datamodels/roman/tags/unit-1.0.0> {unit}
    """

    buff = yaml_to_asdf(yaml)
    with asdf.open(buff) as af:
        assert af["unit"] == u.Unit(unit, parse_strict="silent")


@pytest.mark.parametrize("unit", [u.electron, u.DN, u.electron / u.s, u.electron**2 / u.s**2, u.electron / u.DN])
def test_non_vounit(unit, tmp_path):
    """Test deserialization of a non-VOUnits used by Roman"""

    file_path = tmp_path / "test.asdf"
    with asdf.AsdfFile() as af:
        af["unit"] = unit
        af.write_to(file_path)

    with asdf.open(file_path) as af:
        assert af["unit"] == unit

    with asdf.open(file_path, _force_raw_types=True) as af:
        assert isinstance(af["unit"], asdf.tagged.TaggedString)
        assert af["unit"]._tag.startswith("tag:astropy.org:astropy/units/unit-")
