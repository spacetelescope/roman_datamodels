import warnings
from typing import Annotated, Any, ClassVar, Optional, Union

import astropy.units as u
from pydantic import GetCoreSchemaHandler, GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema

from ._adaptor_tags import asdf_tags

__all__ = ["Unit", "AstropyUnit"]


Unit = Union[
    u.CompositeUnit,
    u.IrreducibleUnit,
    u.NamedUnit,
    u.PrefixUnit,
    u.Unit,
    u.UnrecognizedUnit,
    u.function.mixin.IrreducibleFunctionUnit,
    u.function.mixin.RegularFunctionUnit,
]
Units = Optional[Union[Unit, list[Unit], tuple[Unit, ...]]]


def _get_unit_symbol(unit: Unit) -> str:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=u.UnitsWarning)

        try:
            return unit.to_string(format="vounit")
        except (u.UnitsError, ValueError):
            return unit.to_string()


def _validate_unit(
    unit: Unit,
    validator: core_schema.ValidatorFunctionWrapHandler,
) -> Unit:
    symbol = _get_unit_symbol(unit)
    validator(input_value=symbol)

    return unit


astropy_unit_schema = core_schema.no_info_wrap_validator_function(
    function=_validate_unit, schema=core_schema.str_schema(pattern="[\x00-\x7f]*")
)


class _AstropyUnitPydanticAnnotation:
    units: ClassVar[Optional[list[Unit]]] = None

    @classmethod
    def _get_units(cls, unit: Units) -> Optional[list[str]]:
        if unit is None:
            return

        if not isinstance(unit, (list, tuple)):
            unit = [unit]

        units = set(unit)
        if None in units:
            units.remove(None)
            units.add(u.dimensionless_unscaled)

        return list(units)

    @classmethod
    def _get_unit_name(cls, units: Optional[Units]) -> str:
        return "" if units is None else "_".join([_get_unit_symbol(unit) for unit in units])

    @classmethod
    def factory(cls, *, unit: Units = None) -> type:
        units = cls._get_units(unit)
        return type(
            cls.__name__ if units is None else f"{cls.__name__}_{cls._get_unit_name(units)}",
            (cls,),
            {"units": units},
        )

    @classmethod
    def make_default(cls, **kwargs) -> u.Unit:
        """
        Return the default unit, this is assumed to be the first unit listed

        Returns
        -------
        Returns the first unit
        """
        if cls.units is None:
            return u.dimensionless_unscaled

        return cls.units[0]

    @classmethod
    def _units_schema(cls) -> core_schema.CoreSchema:
        return astropy_unit_schema if cls.units is None else core_schema.literal_schema(cls.units)

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _source_type: Any,
        _handler: GetCoreSchemaHandler,
    ) -> core_schema.CoreSchema:
        units_schema = cls._units_schema()

        return core_schema.json_or_python_schema(
            python_schema=core_schema.chain_schema(
                [
                    core_schema.is_instance_schema(Unit),
                    units_schema,
                ],
            ),
            json_schema=units_schema,
            serialization=core_schema.plain_serializer_function_ser_schema(_get_unit_symbol, when_used="json"),
        )

    @classmethod
    def __get_pydantic_json_schema__(
        cls,
        _core_schema: core_schema.CoreSchema,
        handler: GetJsonSchemaHandler,
    ) -> JsonSchemaValue:
        schema = {
            "title": None,
            "tag": asdf_tags.ASTROPY_UNIT.value,
        }
        if cls.units is None:
            return schema

        return {**schema, "enum": sorted(_get_unit_symbol(unit) for unit in cls.units)}


class _AstropyUnit:
    """Hack to make it look like it has the style of a type annotation."""

    @staticmethod
    def __getitem__(unit: Units = None) -> type:
        return Annotated[Unit, _AstropyUnitPydanticAnnotation.factory(unit=unit)]


AstropyUnit = _AstropyUnit()
