"""
Define a Pydantic adaptor for an astropy Time.
"""
from __future__ import annotations

__all__ = ["AstropyTime"]

from typing import TYPE_CHECKING, Annotated, Any, ClassVar

from astropy.time import Time
from pydantic import GetCoreSchemaHandler, GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema

from ._base import Adaptor, AdaptorGen

if TYPE_CHECKING:
    from roman_datamodels.generator._schema import RadSchemaObject


class AstropyTime(Adaptor):
    """
    The pydantic adaptor for an astropy Time.

    This does not allow any constraints on the time, it basically does an isinstance check.
    """

    _tags: ClassVar[tuple[str]] = ("tag:stsci.edu:asdf/time/time-*",)

    @classmethod
    def factory(cls, **kwargs) -> type:
        """
        Generate a new AstropyTime type constrained to the values given.

        Parameters
        ----------
        kwargs
            The values to constrain the type to.

        Returns
        -------
        The new type.
        """

        return cls

    @classmethod
    def __class_getitem__(cls, factory: None) -> type:
        """Make this consistent with the other adaptors."""

        return Annotated[Time, cls.factory()]

    @classmethod
    def make_default(cls, **kwargs) -> Time:
        """
        Create a default instance of the time

        Returns
        -------
        The default time: 2020-01-01T00:00:00.0
        """

        return Time("2020-01-01T00:00:00.000", format="isot", scale="utc")

    @classmethod
    def code_generator(cls, obj: RadSchemaObject) -> AdaptorGen:
        """Create a representation of this adaptor for the schema generator."""
        name = cls.__name__

        # This is the code for the adaptor
        #    AstropyTime[None]
        return AdaptorGen(type_=f"{name}[None]", import_=name)

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _source_type: Any,
        _handler: GetCoreSchemaHandler,
    ) -> core_schema.CoreSchema:
        """
        Specify the pydantic_core schema for an astropy Time.
            This is what is used to validate a model field against its annotation.
        """

        def validate_from_str(value: str) -> Time:
            return Time(value)

        validate_from_str = core_schema.chain_schema(
            [
                core_schema.str_schema(),
                core_schema.no_info_plain_validator_function(validate_from_str),
            ],
        )

        return core_schema.json_or_python_schema(
            json_schema=validate_from_str,
            python_schema=core_schema.is_instance_schema(Time),
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
        return {
            "title": None,
            "tag": AstropyTime._tags[0],
        }
