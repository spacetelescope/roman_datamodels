"""
This module contains the pydantic adaptor for an astropy units.
"""
from __future__ import annotations

__all__ = ["Unit", "AstropyUnit"]

import warnings
from typing import TYPE_CHECKING, Annotated, Any, ClassVar, Optional, Union

import astropy.units as u
from pydantic import GetCoreSchemaHandler, GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema

from ._base import Adaptor, AdaptorGen

if TYPE_CHECKING:
    from roman_datamodels.generator._schema import RadSchemaObject

# This is due to the annoying fact that there is no root class for astropy units.
#     This covers all the types supported by ASDF
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
    """
    Build a string, symbol, representation of a unit.
    """
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
    """
    Wrap a validator around a unit so that it can validate the symbol.
    """
    validator(input_value=_get_unit_symbol(unit))

    return unit


# This is based on the ASDF schema for unit symbols. This translates that logic
#     into a pydantic_core schema.
astropy_unit_schema = core_schema.no_info_wrap_validator_function(
    function=_validate_unit, schema=core_schema.str_schema(pattern="[\x00-\x7f]*")
)


class AstropyUnit(Adaptor):
    """
    The pydantic adaptor for an astropy Unit.

    This will be attached to the type via typing.Annotated so that Pydantic can use it to
    validate that a field is the right unit. Note that it supports a list of possible units
    """

    _tags: ClassVar[tuple[str]] = (
        "tag:astropy.org:astropy/units/unit-*",
        "tag:stsci.edu:asdf/unit/unit-*",
    )

    units: ClassVar[list[Unit] | None] = None

    @classmethod
    def _get_units(cls, unit: Units) -> list[str] | None:
        """
        Translate the possible types of unit listings into something which
        can be used by this adaptor.
        """
        # No specific unit specified
        if unit is None:
            return

        # This handles if a single unit is passed
        if not isinstance(unit, (list, tuple)):
            unit = [unit]
        else:
            unit = list(unit)

        # Remove any None values, leaving only the units
        if None in unit:
            unit.remove(None)
            unit.append(u.dimensionless_unscaled)

        return unit

    @classmethod
    def _get_unit_name(cls, units: Units | None) -> str:
        """Create a name for the unit based on the symbols of the units."""
        return "" if units is None else "_".join([_get_unit_symbol(unit) for unit in units])

    @classmethod
    def factory(cls, *, unit: Units = None) -> type:
        """Construct a new Adaptor type constrained to the values given."""
        units = cls._get_units(unit)
        return type(
            cls.__name__ if units is None else f"{cls.__name__}_{cls._get_unit_name(units)}",
            (cls,),
            {"units": units},
        )

    def __class_getitem__(cls, unit: Units = None) -> type:
        """Turn the typical python annotation style something suitable for Pydantic."""
        return Annotated[Unit, cls.factory(unit=unit)]

    @classmethod
    def make_default(cls, *, unit: Unit = None, **kwargs) -> u.Unit:
        """
        Return the default unit, this is assumed to be the first unit listed

        Returns
        -------
        Returns the first unit
        """

        if unit is not None:
            for default in [] if cls.units is None else cls.units:
                if default == unit:
                    return unit
            else:
                raise ValueError(f"Unit {unit} is not in the list of valid units {cls.units}")

        if cls.units is None:
            return u.dimensionless_unscaled

        return cls.units[0]

    @classmethod
    def _extract_code(cls, obj: RadSchemaObject, import_: str) -> tuple(str, str):
        """
        Partially write the code for this adaptor based on the parsed schema
        """
        # it is possible for there to be no additional unit specification
        # it is also assumed that unit specification will be an enumerated list of
        # valid astropy unit string(s)
        type_ = None
        if obj is not None and obj.enum is not None:
            import_ += ", Unit"

            # Transform the enum units into a python code snippet
            units = [f'Unit("{u}")' for u in obj.enum]

            if len(units) == 1:
                # Reduce the units to a single unit if possible
                type_ = units[0]
            else:
                # Otherwise join the units into a tuple
                type_ = f"({', '.join(units)})"

        # This is (
        #   "<unit(s)>",
        #   "<imports needed>", (note we assume AstropyUnit is fed into the import_ already, so this can
        #                        be reused for AstropyQuantity)
        # )
        return type_, import_

    @classmethod
    def code_generator(cls, obj: RadSchemaObject) -> AdaptorGen:
        """Create a representation of this adaptor for the schema generator."""
        name = cls.__name__

        # extract the base code for this adaptor
        type_, import_ = cls._extract_code(obj, name)

        # This is the code for the adaptor
        #    AstropyUnit[<unit(s)>]
        return AdaptorGen(type_=f"{name}[{type_}]", import_=import_)

    @classmethod
    def _units_schema(cls) -> core_schema.CoreSchema:
        """Create the pydantic_core schema to validate a unit."""
        return astropy_unit_schema if cls.units is None else core_schema.literal_schema(cls.units)

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _source_type: Any,
        _handler: GetCoreSchemaHandler,
    ) -> core_schema.CoreSchema:
        """
        Specify the pydantic_core schema for an astropy Unit.
            This is what is used to validate a model field against its annotation.
        """
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
        """
        This enables Pydantic to generate a JsonSchema for the annotation
            This is to allow us to create single monolithic JsonSchemas for each
            data product if we wish.
        """
        schema = {
            "title": None,
            "tag": AstropyUnit._tags[0],
        }
        if cls.units is None:
            return schema

        return {**schema, "enum": sorted(_get_unit_symbol(unit) for unit in cls.units)}
