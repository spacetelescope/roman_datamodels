"""
Define a Pydantic adaptor for an astropy Quantity.
"""
__all__ = ["AstropyQuantity"]

from typing import Annotated, Any, Optional, TypedDict, Union

import astropy.units as u
from numpy.typing import DTypeLike
from pydantic import GetCoreSchemaHandler, GetJsonSchemaHandler, PositiveInt
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema

from ._adaptor_tags import asdf_tags
from ._astropy_unit import Unit, Units, _AstropyUnitPydanticAnnotation
from ._base import Adaptor
from ._ndarray import NDArrayLike, _AsdfNdArrayPydanticAnnotation


class _QuantitySplit(TypedDict):
    value: NDArrayLike
    unit: Unit


def _validate_quantity(
    quantity: u.Quantity,
    validator: core_schema.ValidatorFunctionWrapHandler,
) -> u.Quantity:
    """
    Wrap a validator around a quantity so that it can validate each part of the quantity.
    """
    split = _QuantitySplit(
        value=quantity.value,
        unit=quantity.unit,
    )
    validator(input_value=split)

    return quantity


def _validate_scalar(
    scalar: DTypeLike,
) -> DTypeLike:
    """
    Assists in validating a scalar astropy Quantities.
    """
    return scalar.dtype.type


class _AstropyQuantityPydanticAnnotation(_AsdfNdArrayPydanticAnnotation, _AstropyUnitPydanticAnnotation):
    """
    The pydantic adaptor for an astropy Quantity.

    This will be attached to the type via typing.Annotated so that Pydantic can use it to
    validate that a field is the right quantity.
    """

    @classmethod
    def factory(
        cls,
        *,
        dtype: DTypeLike | None = None,
        ndim: PositiveInt | None = None,
        unit: Units = None,
        default_shape: tuple[PositiveInt, ...] | None = None,
    ) -> type:
        """Construct a new Adaptor type constrained to the values given."""

        units = cls._get_units(unit)
        name = f"{super().factory(dtype=dtype, ndim=ndim, default_shape=default_shape).__name__}"
        if units is not None:
            name += f"_{cls._get_unit_name(units).replace(' ', '')}"

        return type(
            name,
            (cls,),
            {"units": units, "dtype": dtype, "ndim": ndim, "default_shape": default_shape},
        )

    @classmethod
    def make_default(
        cls, *, shape: tuple[PositiveInt, ...] | None = None, fill: float | None = None, _shrink: bool = False, **kwargs
    ) -> u.Quantity:
        """
        Create a default instance of the Quantity with unit being the first unit listed.

        Parameters
        ----------
        shape : tuple of int, optional
            Override the default shape. Required if no default shape is defined.
        fill : float, optional
            The value to fill the array with. Default is 0.
        _shrink : bool, optional
            If true, the shape will be shrunk to a maximum of 8 in each dimension. This is for
            testing. Default is False

        Returns
        -------
        Quantity of the default shape and dtype filled with the fill value, with unit the first
        unit listed in the annotation.
        """
        array = super().make_default(shape=shape, fill=fill, _shrink=_shrink)
        unit = super(_AsdfNdArrayPydanticAnnotation, cls).make_default(**kwargs)

        return u.Quantity(array, unit=unit, dtype=cls.dtype)

    @classmethod
    def _value_schema(
        cls,
        _source_type: Any,
        _handler: GetCoreSchemaHandler,
    ) -> core_schema.CoreSchema:
        """Create the pydantic_core schema to validate the value part of a quantity."""
        if not cls.ndim:
            return core_schema.chain_schema(
                [
                    core_schema.no_info_plain_validator_function(_validate_scalar),
                    cls._dtype_schema(),
                ],
            )
        return super().__get_pydantic_core_schema__(_source_type, _handler)["python_schema"]

    @classmethod
    def _unit_schema(
        cls,
        _source_type: Any,
        _handler: GetCoreSchemaHandler,
    ) -> core_schema.CoreSchema:
        """Create the pydantic_core schema to validate the unit part of a quantity."""
        return super(_AsdfNdArrayPydanticAnnotation, cls).__get_pydantic_core_schema__(_source_type, _handler)["python_schema"]

    @classmethod
    def _quantity_schema(
        cls,
        _source_type: Any,
        _handler: GetCoreSchemaHandler,
    ) -> core_schema.CoreSchema:
        """Create the pydantic_core schema to validate a quantity."""
        return core_schema.no_info_wrap_validator_function(
            function=_validate_quantity,
            schema=core_schema.typed_dict_schema(
                {
                    "value": core_schema.typed_dict_field(cls._value_schema(_source_type, _handler)),
                    "unit": core_schema.typed_dict_field(cls._unit_schema(_source_type, _handler)),
                }
            ),
        )

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _source_type: Any,
        _handler: GetCoreSchemaHandler,
    ) -> core_schema.CoreSchema:
        """
        Specify the pydantic_core schema for an astropy Quantity.
            This is what is used to validate a model field against its annotation.
        """
        quantity_schema = cls._quantity_schema(_source_type, _handler)

        return core_schema.json_or_python_schema(
            python_schema=core_schema.chain_schema(
                [
                    core_schema.is_instance_schema(u.Quantity),
                    quantity_schema,
                ]
            ),
            json_schema=quantity_schema,
            serialization=core_schema.plain_serializer_function_ser_schema(lambda value: value),
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
            "tag": asdf_tags.ASTROPY_QUANTITY.value,
        }
        if cls.units is None and cls.dtype is None and cls.ndim is None:
            return schema

        properties_schema = {}

        if cls.units is not None:
            properties_schema["unit"] = super(_AsdfNdArrayPydanticAnnotation, cls).__get_pydantic_json_schema__(
                _core_schema, handler
            )

        if cls.dtype is not None or cls.ndim is not None:
            properties_schema["value"] = super().__get_pydantic_json_schema__(_core_schema, handler)

        schema["properties"] = properties_schema

        return schema


_Factory = Union[
    DTypeLike, tuple[Optional[DTypeLike], Optional[PositiveInt]], tuple[Optional[DTypeLike], Optional[PositiveInt], Units]
]


class _AstropyQuantity(Adaptor):
    """
    This is a Hack class to make the AstropyQuantity annotation "look" like how python annotations
    typically look
    """

    @classmethod
    def make_default(cls, **kwargs):
        raise NotImplementedError("This cannot be called on this class")

    @staticmethod
    def __getitem__(factory: _Factory) -> type:
        """Turn the typical python annotation style something suitable for Pydantic."""
        if not isinstance(factory, tuple):
            factory = (factory,)

        if len(factory) < 1 or len(factory) > 4:
            raise TypeError("AstropyQuantity requires a dtype.")

        dtype: DTypeLike | None = factory[0]
        ndim: PositiveInt | None = factory[1] if len(factory) > 2 else None
        unit: Units = factory[2] if len(factory) > 1 else None
        default_shape: tuple[PositiveInt, ...] | None = factory[3] if len(factory) > 3 else None

        return Annotated[
            u.Quantity,
            _AstropyQuantityPydanticAnnotation.factory(dtype=dtype, ndim=ndim, unit=unit, default_shape=default_shape),
        ]


# Turn the Hack into a singleton instance
AstropyQuantity = _AstropyQuantity()
