import asdf
import pytest
from astropy import units as u

from roman_datamodels import units


def test_RomanUnit_fail():
    with pytest.raises(ValueError):
        units.Unit("foo")


@pytest.mark.parametrize("unit", units.ROMAN_UNIT_SYMBOLS)
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


@pytest.mark.parametrize("unit", units.ROMAN_UNIT_SYMBOLS)
def test_string(unit):
    roman_unit = getattr(units, unit)
    astropy_unit = getattr(u, unit)

    assert roman_unit.to_string() == astropy_unit.to_string() == unit


@pytest.mark.parametrize("unit", units.ROMAN_UNIT_SYMBOLS)
def test_unit_serialization(unit, tmp_path):
    roman_unit = getattr(units, unit)

    file_path = tmp_path / "test.asdf"
    with asdf.AsdfFile() as af:
        af["unit"] = roman_unit
        af.write_to(file_path)

    with asdf.open(file_path) as af:
        assert isinstance(af["unit"], units.Unit)
        assert af["unit"] == roman_unit


@pytest.mark.parametrize("unit", units.ROMAN_UNIT_SYMBOLS)
def test_quantity_serialization(unit, tmp_path):
    quantity = 3.14 * getattr(units, unit)

    file_path = tmp_path / "test.asdf"
    with asdf.AsdfFile() as af:
        af["quantity"] = quantity
        af.write_to(file_path)

    with asdf.open(file_path) as af:
        assert af["quantity"] == quantity
        assert isinstance(af["quantity"].unit, units.Unit)


@pytest.mark.parametrize("unit", units.ROMAN_UNIT_SYMBOLS)
@pytest.mark.parametrize("pwr", [-2, -1, 2])
def test_roman_unit_pow(unit, pwr, tmp_path):
    roman_unit = getattr(units, unit)

    power = roman_unit**pwr
    assert isinstance(power, units.CompositeUnit)

    file_path = tmp_path / "test.asdf"
    with asdf.AsdfFile() as af:
        af["power"] = power
        af.write_to(file_path)

    with asdf.open(file_path) as af:
        assert isinstance(af["power"], units.CompositeUnit)
        assert af["power"] == power

        ru = af["power"].bases[0]
        assert isinstance(ru, units.Unit)
        assert ru == roman_unit

        assert af["power"].powers[0] == pwr


@pytest.mark.parametrize("unit", units.ROMAN_UNIT_SYMBOLS)
def test_roman_unit_div_astropy_unit(unit, tmp_path):
    roman_unit = getattr(units, unit)

    composite = roman_unit / u.s
    assert isinstance(composite, units.CompositeUnit)

    file_path = tmp_path / "test.asdf"
    with asdf.AsdfFile() as af:
        af["composite"] = composite
        af.write_to(file_path)

    with asdf.open(file_path) as af:
        assert isinstance(af["composite"], units.CompositeUnit)
        assert af["composite"] == composite

        ru = af["composite"].bases[0]
        assert isinstance(ru, units.Unit)
        assert ru == roman_unit
        assert af["composite"].powers[0] == 1

        uu = af["composite"].bases[1]
        assert isinstance(uu, u.NamedUnit) and not isinstance(uu, units.Unit)
        assert uu == u.s
        assert af["composite"].powers[1] == -1


@pytest.mark.parametrize("unit", units.ROMAN_UNIT_SYMBOLS)
def test_astropy_unit_div_roman_unit(unit, tmp_path):
    roman_unit = getattr(units, unit)

    composite = roman_unit / u.s
    assert isinstance(composite, units.CompositeUnit)

    composite = composite**-1
    assert isinstance(composite, units.CompositeUnit)

    file_path = tmp_path / "test.asdf"
    with asdf.AsdfFile() as af:
        af["composite"] = composite
        af.write_to(file_path)

    with asdf.open(file_path) as af:
        assert isinstance(af["composite"], units.CompositeUnit)
        assert af["composite"] == composite

        uu = af["composite"].bases[0]
        assert isinstance(uu, u.NamedUnit) and not isinstance(uu, units.Unit)
        assert uu == u.s
        assert af["composite"].powers[0] == 1

        ru = af["composite"].bases[1]
        assert isinstance(ru, units.Unit)
        assert ru == roman_unit
        assert af["composite"].powers[1] == -1


@pytest.mark.parametrize("unit", units.ROMAN_UNIT_SYMBOLS)
def test_roman_unit_mul_astropy_unit(unit, tmp_path):
    roman_unit = getattr(units, unit)

    composite = roman_unit * u.s
    assert isinstance(composite, units.CompositeUnit)

    file_path = tmp_path / "test.asdf"
    with asdf.AsdfFile() as af:
        af["composite"] = composite
        af.write_to(file_path)

    with asdf.open(file_path) as af:
        assert isinstance(af["composite"], units.CompositeUnit)
        assert af["composite"] == composite

        ru = af["composite"].bases[0]
        assert isinstance(ru, units.Unit)
        assert ru == roman_unit
        assert af["composite"].powers[0] == 1

        uu = af["composite"].bases[1]
        assert isinstance(uu, u.NamedUnit) and not isinstance(uu, units.Unit)
        assert uu == u.s
        assert af["composite"].powers[1] == 1


def test_force_roman_unit():
    # Roman units
    for unit in units.ROMAN_UNIT_SYMBOLS:
        # Basic conversion
        assert isinstance(units.force_roman_unit(getattr(units, unit)), units.Unit)
        assert isinstance(units.force_roman_unit(getattr(u, unit)), units.Unit)

        # Powers
        assert isinstance(units.force_roman_unit(getattr(units, unit) ** -1), units.CompositeUnit)
        assert isinstance(units.force_roman_unit(getattr(u, unit) ** -1), units.CompositeUnit)

        # Division
        assert isinstance(units.force_roman_unit(getattr(units, unit) / u.s), units.CompositeUnit)
        assert isinstance(units.force_roman_unit(getattr(u, unit) / u.s), units.CompositeUnit)
        assert isinstance(units.force_roman_unit(u.s / getattr(units, unit)), units.CompositeUnit)
        assert isinstance(units.force_roman_unit(u.s / getattr(u, unit)), units.CompositeUnit)

        # Multiplication
        assert isinstance(units.force_roman_unit(getattr(units, unit) * u.s), units.CompositeUnit)
        assert isinstance(units.force_roman_unit(getattr(u, unit) * u.s), units.CompositeUnit)
        assert isinstance(units.force_roman_unit(u.s * getattr(units, unit)), units.CompositeUnit)
        assert isinstance(units.force_roman_unit(u.s * getattr(u, unit)), units.CompositeUnit)

    # Non-Roman units
    for unit in [u.m, u.kg]:
        # Basic conversion
        assert isinstance(uu := units.force_roman_unit(unit), u.NamedUnit) and not isinstance(uu, units.Unit)

        # Powers
        assert isinstance(units.force_roman_unit(unit**-1), u.CompositeUnit) and not isinstance(uu, units.CompositeUnit)

        # Division
        assert isinstance(units.force_roman_unit(unit / u.s), u.CompositeUnit) and not isinstance(uu, units.CompositeUnit)
        assert isinstance(units.force_roman_unit(u.s / unit), u.CompositeUnit) and not isinstance(uu, units.CompositeUnit)

        # Multiplication
        assert isinstance(units.force_roman_unit(unit * u.s), u.CompositeUnit) and not isinstance(uu, units.CompositeUnit)
        assert isinstance(units.force_roman_unit(u.s * unit), u.CompositeUnit) and not isinstance(uu, units.CompositeUnit)
