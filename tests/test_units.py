import asdf
import pytest

from astropy import units as u
from roman_datamodels import units


def test_RomanUnit_fail():
    with pytest.raises(ValueError):
        units.Unit('foo')


@pytest.mark.parametrize('unit', units.ROMAN_UNIT_SYMBOLS)
def test_roman_datamodels_unit(unit):
    roman_unit = getattr(units, unit)
    astropy_unit = getattr(u, unit)

    assert roman_unit == astropy_unit

    assert isinstance(roman_unit, units.Unit)
    assert isinstance(roman_unit, u.Unit)
    assert not isinstance(astropy_unit, units.Unit)

    roman_value = 10 * roman_unit
    astropy_value = 10 * astropy_unit

    assert roman_value == astropy_value


@pytest.mark.parametrize('unit', units.ROMAN_UNIT_SYMBOLS)
def test_string(unit):
    roman_unit = getattr(units, unit)
    astropy_unit = getattr(u, unit)

    assert roman_unit.to_string() == astropy_unit.to_string() == unit


@pytest.mark.parametrize('unit', units.ROMAN_UNIT_SYMBOLS)
def test_unit_serialization(unit, tmp_path):
    roman_unit = getattr(units, unit)

    file_path = tmp_path / "test.asdf"
    with asdf.AsdfFile() as af:
        af["unit"] = roman_unit
        af.write_to(file_path)

    with asdf.open(file_path) as af:
        assert af["unit"] == roman_unit


@pytest.mark.parametrize('unit', units.ROMAN_UNIT_SYMBOLS)
def test_quantity_serialization(unit, tmp_path):
    quantity = 3.14 * getattr(units, unit)

    file_path = tmp_path / "test.asdf"
    with asdf.AsdfFile() as af:
        af["quantity"] = quantity
        af.write_to(file_path)

    with asdf.open(file_path) as af:
        assert af["quantity"] == quantity
        assert isinstance(af["quantity"].unit, units.Unit)
