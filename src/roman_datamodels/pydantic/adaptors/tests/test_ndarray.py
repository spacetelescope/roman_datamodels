import asdf
import numpy as np
import pytest
from pydantic import BaseModel, ValidationError

from roman_datamodels.pydantic.adaptors._adaptor_tags import asdf_tags
from roman_datamodels.pydantic.adaptors._ndarray import NdArray

dtypes = (
    None,
    np.int8,
    np.int16,
    np.uint16,
    np.int32,
    np.uint32,
    np.int64,
    np.uint64,
    np.float32,
    np.float64,
    np.complex64,
    np.complex128,
    np.bool_,
)
ndims = (None, 0, 1, 2, 3, 4, 5, 6)


def _generate_array(dtype, ndim):
    if dtype is None:
        dtype = np.float32

    if ndim == 0:
        return np.array(1, dtype=dtype)

    _ndim = 7 if ndim is None else ndim
    return np.broadcast_to(np.arange(2, dtype=dtype), (2,) * _ndim)


@pytest.mark.parametrize("dtype", dtypes)
@pytest.mark.parametrize("ndim", ndims)
def test_ndarray_validates(dtype, ndim):
    """
    Test that ndarray validates and does not get copied
    """

    class TestModel(BaseModel):
        array: NdArray[dtype, ndim]

    array = _generate_array(dtype, ndim)

    model = TestModel(array=array)
    assert isinstance(model.array, np.ndarray)  # Check type is preserved
    assert model.array is array

    class TestNoneModel(BaseModel):
        array: NdArray[None]

    # Test that all arrays are valid in the None model
    none_model = TestNoneModel(array=array)
    assert none_model.array is array


@pytest.mark.parametrize("dtype", zip(dtypes[1:], dtypes[1:][::-1]))
@pytest.mark.parametrize("ndim", zip(ndims, ndims[::-1]))
def test_ndarray_fails(dtype, ndim):
    """
    Test that an incorrect ndarray fails to validate
    """
    model_dtype, array_dtype = dtype
    model_ndim, array_ndim = ndim

    class TestModel(BaseModel):
        array: NdArray[model_dtype, model_ndim]

    # Both dtype and ndim are wrong
    with pytest.raises(ValidationError):
        TestModel(array=_generate_array(array_dtype, array_ndim))

    # Only dtype is wrong
    with pytest.raises(ValidationError):
        TestModel(array=_generate_array(array_dtype, model_ndim))

    # Only ndim is "wrong"
    if model_ndim is None:
        # when ndim is None, any positive ndim is valid
        TestModel(array=_generate_array(model_dtype, array_ndim))
    else:
        with pytest.raises(ValidationError):
            TestModel(array=_generate_array(model_dtype, array_ndim))

    # Both correct
    TestModel(array=_generate_array(model_dtype, model_ndim))


@pytest.mark.parametrize("dtype", dtypes)
@pytest.mark.parametrize("ndim", ndims)
def test_NDArrayType_validates(tmp_path, dtype, ndim):
    """
    Test that a NDArrayType validates and does not get copied or loaded by asdf
    """
    file_name = tmp_path / "test.asdf"

    class TestModel(BaseModel):
        array: NdArray[dtype, ndim]

    class TestNoneModel(BaseModel):
        array: NdArray[None]

    asdf.AsdfFile({"array": _generate_array(dtype, ndim)}).write_to(file_name)

    with asdf.open(file_name) as af:
        array = af["array"]
        assert isinstance(array, asdf.tags.core.NDArrayType)
        assert array._array is None  # Check array is not loaded

        model = TestModel(array=array)
        assert isinstance(model.array, asdf.tags.core.NDArrayType)  # Check type is preserved
        assert model.array is array  # Check array is not copied
        assert array._array is None  # Check array is not loaded by asdf into memory

        # Test that all arrays are valid in the None model
        none_model = TestNoneModel(array=array)
        assert none_model.array is array


@pytest.mark.parametrize("dtype", zip(dtypes[1:], dtypes[1:][::-1]))
@pytest.mark.parametrize("ndim", zip(ndims, ndims[::-1]))
def test_NDArrayType_fails(tmp_path, dtype, ndim):
    """
    Test that an incorrect NDArrayType fails to validate
    """
    file_name = tmp_path / "test.asdf"

    model_dtype, array_dtype = dtype
    model_ndim, array_ndim = ndim

    class TestModel(BaseModel):
        array: NdArray[model_dtype, model_ndim]

    asdf.AsdfFile(
        {
            "both_bad": _generate_array(array_dtype, array_ndim),
            "dtype_bad": _generate_array(array_dtype, model_ndim),
            "ndim_bad": _generate_array(model_dtype, array_ndim),
            "both_good": _generate_array(model_dtype, model_ndim),
        }
    ).write_to(file_name)

    with asdf.open(file_name) as af:
        # Both dtype and ndim are wrong
        with pytest.raises(ValidationError):
            TestModel(array=af["both_bad"])

        # Only dtype is wrong
        with pytest.raises(ValidationError):
            TestModel(array=af["dtype_bad"])

        # Only ndim is "wrong"
        if model_ndim is None:
            # when ndim is None, any positive ndim is valid
            TestModel(array=af["ndim_bad"])
        else:
            with pytest.raises(ValidationError):
                TestModel(array=af["ndim_bad"])

        # Both correct
        TestModel(array=af["both_good"])


def test_non_ndarray_fails():
    """
    Test that a non-ndarray fails to validate
    """

    class TestModel(BaseModel):
        array: NdArray[np.float32]

    with pytest.raises(ValidationError):
        TestModel(array=1)

    class TestNoneModel(BaseModel):
        array: NdArray[None]

    with pytest.raises(ValidationError):
        TestNoneModel(array=1)


def test_type_annotation_fails():
    with pytest.raises(TypeError):
        NdArray[()]

    with pytest.raises(TypeError):
        NdArray[np.float32, 2, 3]


@pytest.mark.parametrize("dtype", dtypes)
@pytest.mark.parametrize("ndim", ndims)
def test_json_schema_return(dtype, ndim):
    truth = {
        "title": None,
        "tag": asdf_tags.ASDF_NDARRAY.value,
    }
    if dtype is not None:
        truth["datatype"] = dtype.__name__
    if ndim is not None:
        truth["ndim"] = ndim

    class TestModel(BaseModel):
        array: NdArray[dtype, ndim]

    # Grab the json schema produced by the annotation
    assert truth == TestModel.model_json_schema()["properties"]["array"]
