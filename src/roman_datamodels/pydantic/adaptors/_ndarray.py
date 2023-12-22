from typing import Annotated, Any, Callable, ClassVar, Optional, TypedDict, Union

import numpy as np
from asdf.tags.core import NDArrayType
from numpy.typing import DTypeLike
from pydantic import GetJsonSchemaHandler, PositiveInt
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema

from ._adaptor_tags import asdf_tags

__all__ = ["NdArray"]

NDArrayLike = Union[np.ndarray, NDArrayType]


class _NDArrayMeta(TypedDict):
    dtype: DTypeLike
    ndim: int


_dtype_schema = core_schema.union_schema(
    [
        core_schema.is_subclass_schema(np.number),
        core_schema.is_subclass_schema(np.bool_),
    ],
)
_ndim_schema = core_schema.int_schema(ge=0)


def _validate_array(
    array: NDArrayLike,
    validator: core_schema.ValidatorFunctionWrapHandler,
) -> NDArrayLike:
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


class _AsdfNdArrayPydanticAnnotation:
    dtype: ClassVar[Optional[DTypeLike]]
    ndim: ClassVar[Optional[PositiveInt]]

    @classmethod
    def factory(cls, *, dtype: Optional[DTypeLike] = None, ndim: Optional[PositiveInt] = None) -> type:
        name = f"{cls.__name__}"
        if dtype is not None:
            name += f"_{dtype.__name__}"
        if ndim is not None:
            name += f"_{ndim}"

        return type(
            name,
            (cls,),
            {
                "dtype": dtype,
                "ndim": ndim,
            },
        )

    @classmethod
    def _dtype_schema(cls) -> core_schema.CoreSchema:
        return _dtype_schema if cls.dtype is None else core_schema.literal_schema([cls.dtype])

    @classmethod
    def _ndim_schema(cls) -> core_schema.CoreSchema:
        return _ndim_schema if cls.ndim is None else core_schema.literal_schema([cls.ndim])

    @classmethod
    def _nd_array_schema(cls) -> core_schema.CoreSchema:
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
        schema = {
            "title": None,
            "tag": asdf_tags.ASDF_NDARRAY.value,
        }
        if cls.dtype is not None:
            schema["datatype"] = cls.dtype.__name__

        if cls.ndim is not None:
            schema["ndim"] = cls.ndim
        return schema


_Factory = Union[DTypeLike, tuple[DTypeLike, PositiveInt]]


class _NdArray:
    @staticmethod
    def __getitem__(factory: _Factory) -> type:
        if not isinstance(factory, tuple):
            factory = (factory,)

        if len(factory) < 1 or len(factory) > 2:
            raise TypeError("NdArray requires a dtype and optionally a dimension.")

        dtype: DTypeLike = factory[0]
        ndim: Optional[int] = factory[1] if len(factory) > 1 else None

        return Annotated[
            Union[
                NDArrayType,
                np.ndarray[ndim if ndim else Any, dtype if dtype else dtype],
            ],
            _AsdfNdArrayPydanticAnnotation.factory(dtype=dtype, ndim=ndim),
        ]


NdArray = _NdArray()
