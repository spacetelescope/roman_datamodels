"""
This module is to facilitate easy identification of Pydantic Adaptors, in the
context of the FieldInfo data encoded into a Pydantic model.
"""
import abc
from inspect import isclass
from typing import Annotated, get_args, get_origin

from pydantic.fields import FieldInfo

__all__ = ["Adaptor", "get_adaptor", "is_adaptor"]


class Adaptor(abc.ABC):
    """Base class for all Adaptors."""

    @abc.abstractclassmethod
    def make_default(cls, **kwargs):
        """Create a default instance of the Adaptor."""
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
