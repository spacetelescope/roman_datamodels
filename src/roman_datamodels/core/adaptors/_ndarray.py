"""
Define a Pydantic adaptor for a numpy ndarray (and asdf NDArrayType).
"""
from __future__ import annotations

__all__ = ["NdArray"]

from collections.abc import Callable
from typing import TYPE_CHECKING, Annotated, Any, ClassVar, TypedDict, Union

import numpy as np
from asdf.tags.core import NDArrayType
from numpy.typing import DTypeLike
from pydantic import GetJsonSchemaHandler, PositiveInt
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema

from ._base import Adaptor, AdaptorGen

if TYPE_CHECKING:
    from roman_datamodels.generator._schema import RadSchemaObject

NDArrayLike = Union[np.ndarray, NDArrayType]
_Factory = Union[DTypeLike, tuple[DTypeLike, PositiveInt]]


class _NDArrayMeta(TypedDict):
    dtype: DTypeLike
    ndim: int


# Pydantic core schema for a numpy dtype validation
_dtype_schema = core_schema.union_schema(
    [
        core_schema.is_subclass_schema(np.number),
        core_schema.is_subclass_schema(np.bool_),
    ],
)
# Pydantic core schema for a numpy ndim validation
_ndim_schema = core_schema.int_schema(ge=0)


def _validate_array(
    array: NDArrayLike,
    validator: core_schema.ValidatorFunctionWrapHandler,
) -> NDArrayLike:
    """
    Wrap a validator around an array so that it can be validated correctly
    """
    if isinstance(array, NDArrayType):
        # This is so the binary data is not force loaded into memory
        #    when the array is validated
        meta = _NDArrayMeta(
            dtype=array._dtype.type,
            ndim=len(array._shape),
        )
    else:
        meta = _NDArrayMeta(
            dtype=array.dtype.type,
            ndim=array.ndim,
        )
    validator(input_value=meta)
    return array


class NdArray(Adaptor):
    """
    The pydantic adaptor for an numpy ndarray (and asdf NdArrayType).

    This will be attached to the type via typing.Annotated so that Pydantic can use it to
    validate that a field is the right ndarray.
    """

    _tags: ClassVar[tuple[str]] = ("tag:stsci.edu:asdf/core/ndarray-*",)

    dtype: ClassVar[DTypeLike | None]
    ndim: ClassVar[PositiveInt | None]
    default_shape: ClassVar[tuple[PositiveInt, ...] | None]

    @classmethod
    def factory(
        cls,
        *,
        dtype: DTypeLike | None = None,
        ndim: PositiveInt | None = None,
        default_shape: tuple[PositiveInt, ...] | None = None,
    ) -> type:
        """Construct a new Adaptor type constrained to the values given."""
        name = f"{cls.__name__}"
        if dtype is not None:
            name += f"_{dtype.__name__}"
        if ndim is not None:
            name += f"_{ndim}"

        if default_shape is not None:
            name += f"_default_{'_'.join(str(s) for s in default_shape)}"

        return type(
            name,
            (cls,),
            {
                "dtype": dtype,
                "ndim": ndim,
                "default_shape": default_shape,
            },
        )

    def __class_getitem__(cls, factory: _Factory) -> type:
        """Turn the typical python annotation style something suitable for Pydantic."""
        if not isinstance(factory, tuple):
            factory = (factory,)

        if len(factory) < 1 or len(factory) > 3:
            raise TypeError("NdArray requires a dtype and optionally a dimension.")

        dtype: DTypeLike = factory[0]
        ndim: int | None = factory[1] if len(factory) > 1 else None
        default_shape: tuple[PositiveInt, ...] | None = factory[2] if len(factory) > 2 else None

        return Annotated[
            Union[
                NDArrayType,
                np.ndarray[ndim if ndim else Any, dtype if dtype else dtype],
            ],
            cls.factory(dtype=dtype, ndim=ndim, default_shape=default_shape),
        ]

    @classmethod
    def make_default(
        cls, *, shape: tuple[PositiveInt, ...] | None = None, fill: float | None = None, _shrink: bool = False, **kwargs
    ) -> np.ndarray:
        """
        Create a default instance of the array.

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
        An array of the default shape and dtype filled with the fill value.
        """
        if shape is None:
            shape = cls.default_shape

        if shape is None and cls.ndim == 0:
            shape = tuple()

        if shape is None:
            raise ValueError("No default shape defined.")

        if _shrink:
            shape = tuple((s if s < 8 else 8) for s in shape)

        # TODO: Add default unit tests messing with the shape
        if len(shape) < cls.ndim:
            raise ValueError(f"Shape {shape} does not have the expected ndim {cls.ndim}.")

        # Set the fill value to the default number when passed a scalar value
        #   This is to keep generated data fields in regression files consistent
        #   with the default values.
        if fill is None:
            fill = -999999 if len(shape) == 0 else 0

        if cls.ndim == 0:
            return np.array(fill, dtype=cls.dtype)

        return np.full(shape[-cls.ndim :], fill, dtype=cls.dtype)

    @classmethod
    def _extract_code(cls, obj: RadSchemaObject, import_: str) -> tuple(str, str, str):
        """
        Partially write the code for this adaptor based on the parsed schema
        """
        extras = obj.extras

        # dtype is listed under "datatype"
        dtype = extras.get("datatype", None)

        # datatype may not be specified, in which case we don't need to import numpy
        if dtype is not None:
            # Turn the dtype string into a python code snippet
            dtype = f"np.{dtype}"

            # Include numpy in the imports
            import_ += ", np"

        default_shape = extras.get("default_shape", None)
        if default_shape is not None:
            default_shape = tuple(default_shape)

        # This is (
        #   "<dtype>, <ndim>",
        #   "<default_shape>"",
        #   "<imports needed>", (note we assume NdArray is fed into the import_ already, so this can
        #                        be reused for AstropyQuantity)
        # )
        return f"{dtype}, {extras.get('ndim', None)}", default_shape, import_

    @classmethod
    def code_generator(cls, obj: RadSchemaObject) -> AdaptorGen:
        """Create a representation of this adaptor for the schema generator."""
        name = cls.__name__

        # extract the base code for this adaptor
        type_, default_shape, import_ = cls._extract_code(obj, name)

        # This creates a string representation of the adaptor:
        #    NdArray[<dtype>, <ndim>, <default_shape>]
        return AdaptorGen(type_=f"{name}[{type_}, {default_shape}]", import_=import_)

    @classmethod
    def _dtype_schema(cls) -> core_schema.CoreSchema:
        """Create the pydantic_core schema to validate a dtype."""
        return _dtype_schema if cls.dtype is None else core_schema.literal_schema([cls.dtype])

    @classmethod
    def _ndim_schema(cls) -> core_schema.CoreSchema:
        """Create the pydantic_core schema to validate a ndim."""
        return _ndim_schema if cls.ndim is None else core_schema.literal_schema([cls.ndim])

    @classmethod
    def _nd_array_schema(cls) -> core_schema.CoreSchema:
        """Create the pydantic_core schema to validate an ndarray (or NdArrayType)."""
        return core_schema.no_info_wrap_validator_function(
            function=_validate_array,
            schema=core_schema.typed_dict_schema(
                {
                    "dtype": core_schema.typed_dict_field(cls._dtype_schema()),
                    "ndim": core_schema.typed_dict_field(cls._ndim_schema()),
                }
            ),
        )

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _source_type: Any,
        _handler: Callable[[Any], core_schema.CoreSchema],
    ) -> core_schema.CoreSchema:
        """
        Specify the pydantic_core schema for an ndarray or NdArrayType.
            This is what is used to validate a model field against its annotation.
        """
        np_array_schema = cls._nd_array_schema()

        return core_schema.json_or_python_schema(
            python_schema=core_schema.chain_schema(
                [
                    core_schema.is_instance_schema(NDArrayLike),
                    np_array_schema,
                ]
            ),
            json_schema=np_array_schema,
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
            "tag": NdArray._tags[0],
        }
        if cls.dtype is not None:
            schema["datatype"] = cls.dtype.__name__

        if cls.ndim is not None:
            schema["ndim"] = cls.ndim
        return schema
