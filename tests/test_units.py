from numpy import isin
import pytest

from astropy import units as u
from roman_datamodels import units


def test_RomanUnit_fail():
    with pytest.raises(ValueError):
        units.Unit('foo')


@pytest.mark.parametrize('unit', units.ROMAN_UNIT_SYMBOLS)
def test_units(unit):
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