import asdf
import numpy as np
import pytest
from pydantic import BaseModel, ValidationError

from roman_datamodels.core.adaptors import NdArray, asdf_tags, get_adaptor

dtypes = (
    None,
    np.int32,
    np.uint32,
    np.float32,
    np.complex128,
)
ndims = (None, 2, 3, 5)


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
        "tag": asdf_tags.ND_ARRAY.value,
    }
    if dtype is not None:
        truth["datatype"] = dtype.__name__
    if ndim is not None:
        truth["ndim"] = ndim

    class TestModel(BaseModel):
        array: NdArray[dtype, ndim]

    # Grab the json schema produced by the annotation
    assert truth == TestModel.model_json_schema()["properties"]["array"]


@pytest.mark.parametrize("dtype", dtypes)
@pytest.mark.parametrize("ndim", [0, 2, 3])
@pytest.mark.parametrize("default_shape", [(7, 8), (7, 8, 9)])
class TestMakeDefault:
    """Test default creation"""

    def test_default(self, dtype, ndim, default_shape):
        """No arguments"""
        adaptor = get_adaptor(NdArray[dtype, ndim, default_shape])

        # This will produce an error as a default cannot be made that satisfies the annotation
        if len(default_shape) < ndim:
            with pytest.raises(ValueError, match=r"Shape .* does not have the expected ndim .*"):
                adaptor.make_default()

            # Return early
            return

        # Test the default
        default = adaptor.make_default()
        assert isinstance(default, np.ndarray)

        # Default for dtype=None in np.fill is np.int64
        assert default.dtype == np.int64 if dtype is None else dtype
        assert default.ndim == ndim
        # When zero dimensional the shape is empty
        assert default.shape == (default_shape[-ndim:] if ndim > 0 else ())
        assert (default == 0).all()

    def test_fill(self, dtype, ndim, default_shape):
        """Pass a fill value"""
        adaptor = get_adaptor(NdArray[dtype, ndim, default_shape])
        fill = np.int64(4) if dtype is None else dtype(4)

        # This will produce an error as a default cannot be made that satisfies the annotation
        if len(default_shape) < ndim:
            with pytest.raises(ValueError, match=r"Shape .* does not have the expected ndim .*"):
                adaptor.make_default(fill=fill)

            # Return early
            return

        # Test with the fill value
        default = adaptor.make_default(fill=fill)
        assert isinstance(default, np.ndarray)

        # Default for dtype=None in np.fill is np.int64
        assert default.dtype == np.int64 if dtype is None else dtype
        assert default.ndim == ndim
        # When zero dimensional the shape is empty
        assert default.shape == (default_shape[-ndim:] if ndim > 0 else ())
        assert (default == fill).all()

    @pytest.mark.parametrize("shape", [(1, 2), (3, 4, 5)])
    def test_shape(self, dtype, ndim, default_shape, shape):
        """Pass a shape"""
        adaptor = get_adaptor(NdArray[dtype, ndim, default_shape])

        # This will produce an error as a default cannot be made that satisfies the annotation
        if len(shape) < ndim:
            with pytest.raises(ValueError, match=r"Shape .* does not have the expected ndim .*"):
                adaptor.make_default(shape=shape)

            # Return early
            return

        # Test with the fill value
        default = adaptor.make_default(shape=shape)
        assert isinstance(default, np.ndarray)

        # Default for dtype=None in np.fill is np.int64
        assert default.dtype == np.int64 if dtype is None else dtype
        assert default.ndim == ndim
        # When zero dimensional the shape is empty
        assert default.shape == (shape[-ndim:] if ndim > 0 else ())
        assert (default == 0).all()
