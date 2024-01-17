"""
This module is to facilitate easy identification of Pydantic Adaptors, in the
context of the FieldInfo data encoded into a Pydantic model.
"""
from __future__ import annotations

__all__ = ["Adaptor", "get_adaptor", "is_adaptor", "AdaptorGen"]

import abc
from collections.abc import Callable
from inspect import isclass
from typing import TYPE_CHECKING, Annotated, Any, NamedTuple, get_args, get_origin

from pydantic import GetJsonSchemaHandler
from pydantic.fields import FieldInfo
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema

from roman_datamodels.core._utils import remove_uri_version

if TYPE_CHECKING:
    from roman_datamodels.generator._schema import RadSchemaObject


class Adaptor(abc.ABC):
    """Base class for all Adaptors."""

    @abc.abstractproperty
    def _tags(cls) -> tuple[str]:
        """The tags to use for this Adaptor."""
        ...

    @classmethod
    def tags(cls) -> tuple[str]:
        """The tags to use for this Adaptor."""
        return tuple(remove_uri_version(tag) for tag in cls._tags)

    @abc.abstractclassmethod
    def factory(cls, **kwargs) -> type:
        """Generate a new Adaptor type constrained to the values given."""
        ...

    @abc.abstractclassmethod
    def __class_getitem__(cls, factory: Any) -> type:
        """Turn the typical python annotation style something suitable for Pydantic."""
        ...

    @abc.abstractclassmethod
    def make_default(cls, **kwargs):
        """Create a default instance of the type described by the Adaptor."""
        ...

    @classmethod
    def code_generator(cls, obj: RadSchemaObject) -> AdaptorGen:
        """Create the code used by the generator to represent the Adaptor."""

    @abc.abstractclassmethod
    def __get_pydantic_core_schema__(
        cls,
        _source_type: Any,
        _handler: Callable[[Any], core_schema.CoreSchema],
    ) -> core_schema.CoreSchema:
        """Specify the pydantic_core schema for the Adaptor."""
        ...

    @abc.abstractclassmethod
    def __get_pydantic_json_schema__(
        cls,
        _core_schema: core_schema.CoreSchema,
        handler: GetJsonSchemaHandler,
    ) -> JsonSchemaValue:
        """Specify the json schema for the Adaptor pydantic will write."""
        ...


def get_adaptor(obj) -> Adaptor | None:
    """
    Determine if the given object is an Adaptor.
    """
    # Extract obj is a field
    if isinstance(obj, FieldInfo):
        if metadata := obj.metadata:
            if not isinstance(metadata, list):
                metadata = [metadata]

            for item in metadata:
                adaptor = get_adaptor(item)
                if adaptor is not None:
                    return adaptor

        return get_adaptor(obj.annotation)

    # Exclude Adaptor itself
    if obj is Adaptor:
        return None

    # If obj is a class check if it is an adaptor subclass
    if isclass(obj) and issubclass(obj, Adaptor):
        return obj

    # If obj is an Annotated check if the last argument is an adaptor
    if isclass(origin := get_origin(obj)) and issubclass(origin, Annotated):
        return len(get_args(obj)) == 2 and get_adaptor(get_args(obj)[-1])

    args = get_args(obj)
    if len(args) > 0 and args[-1] is type(None):
        return get_adaptor(args[0])

    # Fall back on checking if obj is an instance of an adaptor
    if isinstance(obj, Adaptor):
        return obj

    return None


def is_adaptor(obj: type) -> bool:
    """
    Determine if the given object is an Adaptor.
    """
    return get_adaptor(obj) is not None


class AdaptorGen(NamedTuple):
    """
    A representation of an Adaptor.

    This is used to encode the Adaptor into the FieldInfo metadata.
    """

    type_: str
    import_: str
