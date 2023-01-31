from astropy import units as u

__all__ = ["Unit"]


ROMAN_UNIT_SYMBOLS = ["DN", "electron"]


class UnitMixin:
    def __pow__(self, p):
        from astropy.units.core import validate_power

        p = validate_power(p)
        return CompositeUnit(1, [self], [p], _error_check=False)

    def __truediv__(self, m):
        if isinstance(m, (bytes, str)):
            m = Unit(m)

        if isinstance(m, u.UnitBase):
            if m.is_unity():
                return self
            return CompositeUnit(1, [self, m], [1, -1], _error_check=False)

        try:
            # Cannot handle this as Unit, re-try as Quantity
            from astropy.units.quantity import Quantity

            return Quantity(1, self) / m
        except TypeError:
            return NotImplemented

    def __mul__(self, m):
        if isinstance(m, (bytes, str)):
            m = u.Unit(m)

        if isinstance(m, u.UnitBase):
            if m.is_unity():
                return self
            elif self.is_unity():
                return m
            return CompositeUnit(1, [self, m], [1, 1], _error_check=False)

        # Cannot handle this as Unit, re-try as Quantity.
        try:
            from astropy.units.quantity import Quantity

            return Quantity(1, unit=self) * m
        except TypeError:
            return NotImplemented


class CompositeUnit(UnitMixin, u.CompositeUnit):
    """
    Class for handling composite units containing a roman unit.
    """

    _tag = "asdf://stsci.edu/datamodels/roman/tags/unit-1.0.0"


class Unit(UnitMixin, u.Unit):
    """
    Class for the non-VOunits, which need to be serialized by Roman.
    """

    _tag = "asdf://stsci.edu/datamodels/roman/tags/unit-1.0.0"


def def_roman_unit(symbol):
    """
    Define a Roman unit version of an astropy unit.

    This will automatically add the unit to the namespace of this module

    Parameters
    ----------
    symbol : str
        The symbol of the astropy unit to define a Roman unit for.

    Returns
    -------

    A RomanUnit instance
    """

    represents = getattr(u, symbol)

    return Unit(symbol, represents=represents, namespace=globals())


def force_roman_unit(unit):
    """
    Force a unit to be a roman unit. If necessary

    Parameters
    ----------

    unit :
        The unit to force to be a roman unit

    Returns
    -------
        A roman unit version if called for
    """

    import astropy.units as u

    import roman_datamodels.units as units

    if (ru := getattr(units, unit.to_string(), None)) is not None:
        return ru
    elif isinstance(unit, u.CompositeUnit):
        bases = [getattr(units, base.to_string(), base) for base in unit.bases]
        if any([isinstance(base, units.Unit) for base in bases]):
            return units.CompositeUnit(unit.scale, bases, unit.powers)

    return unit


for unit in ROMAN_UNIT_SYMBOLS:
    def_roman_unit(unit)
