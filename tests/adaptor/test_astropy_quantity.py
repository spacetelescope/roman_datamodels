import astropy.units as u
import numpy as np
import pytest
from pydantic import BaseModel, ValidationError

from roman_datamodels.core.adaptors import AstropyQuantity, AstropyUnit, NdArray, get_adaptor
from roman_datamodels.core.adaptors._astropy_unit import _get_unit_symbol

dtypes = (
    None,
    np.uint16,
    np.float32,
    np.complex128,
)
ndims = (None, 2, 3)
units = (None, u.DN, u.DN / u.s, (u.DN / u.s) ** 2, (u.electron, u.DN))


def _generate_quantity(dtype, unit, ndim):
    if isinstance(unit, tuple):
        # Cannot use a dual unit for a quantity
        unit = unit[0]

    if dtype is None:
        dtype = np.float32

    if ndim == 0:
        return u.Quantity(np.array(1), unit=unit, dtype=dtype)

    _ndim = 5 if ndim is None else ndim
    return u.Quantity(np.broadcast_to(np.arange(2), (2,) * _ndim), unit=unit, dtype=dtype)


@pytest.mark.parametrize("dtype", dtypes)
@pytest.mark.parametrize("ndim", ndims)
@pytest.mark.parametrize("unit", units)
def test_quantity_validates(dtype, ndim, unit):
    """
    Test that quantity validates and does not get copied
    """

    class TestModel(BaseModel):
        quantity: AstropyQuantity[dtype, ndim, unit]

    quantity = _generate_quantity(dtype, unit, ndim)

    model = TestModel(quantity=quantity)
    assert isinstance(model.quantity, u.Quantity)
    assert model.quantity is quantity

    # Test quantity can have two different units
    if not isinstance(unit, tuple):  # cannot use an already dual unit
        e_quantity = _generate_quantity(dtype, u.electron, ndim)

        class TestDuelUnitModel(BaseModel):
            quantity: AstropyQuantity[dtype, ndim, (unit, u.electron)]

        model0 = TestDuelUnitModel(quantity=quantity)
        assert model0.quantity is quantity
        model1 = TestDuelUnitModel(quantity=e_quantity)
        assert model1.quantity is e_quantity

    # Test that something is any sort of quantity
    class TestNoneModel(BaseModel):
        quantity: AstropyQuantity[None]

    none_model = TestNoneModel(quantity=quantity)
    assert none_model.quantity is quantity


@pytest.mark.parametrize("dtype", zip(dtypes, dtypes[1:] + dtypes[:1]))
@pytest.mark.parametrize("ndim", zip(ndims, ndims[1:] + ndims[:1]))
@pytest.mark.parametrize("unit", zip(units, units[1:] + units[:1]))
def test_quantity_fail(dtype, ndim, unit):
    """
    Test that invalid quantities fail to validate
    """
    model_dtype, quantity_dtype = dtype
    model_ndim, quantity_ndim = ndim
    model_unit, quantity_unit = unit

    class TestModel(BaseModel):
        quantity: AstropyQuantity[model_dtype, model_ndim, model_unit]

    # All bad
    if model_dtype or model_ndim or model_unit:
        with pytest.raises(ValidationError):
            TestModel(quantity=_generate_quantity(quantity_dtype, quantity_unit, quantity_ndim))
    else:
        # when all are None, any quantity is valid
        TestModel(quantity=_generate_quantity(quantity_dtype, quantity_unit, quantity_ndim))

    # only ndim good
    if model_dtype or model_unit:
        with pytest.raises(ValidationError):
            TestModel(quantity=_generate_quantity(quantity_dtype, quantity_unit, model_ndim))
    else:
        # when dtype and unit are none, any dtype/unit is valid
        TestModel(quantity=_generate_quantity(quantity_dtype, quantity_unit, model_ndim))

    # only unit good
    if model_dtype or model_ndim:
        with pytest.raises(ValidationError):
            TestModel(quantity=_generate_quantity(quantity_dtype, model_unit, quantity_ndim))
    else:
        # when dtype and ndim are none, any dtype/ndim is valid
        TestModel(quantity=_generate_quantity(quantity_dtype, model_unit, quantity_ndim))

    # only dtype good
    if model_ndim or model_unit:
        with pytest.raises(ValidationError):
            TestModel(quantity=_generate_quantity(model_dtype, quantity_unit, quantity_ndim))
    else:
        # when ndim and unit are none, any ndim/unit is valid
        TestModel(quantity=_generate_quantity(model_dtype, quantity_unit, quantity_ndim))

    # only ndim bad
    if model_ndim:
        with pytest.raises(ValidationError):
            TestModel(quantity=_generate_quantity(model_dtype, model_unit, quantity_ndim))
    else:
        # when ndim is 0 or None, any positive ndim is valid
        TestModel(quantity=_generate_quantity(model_dtype, model_unit, quantity_ndim))

    # only unit bad
    if model_unit:
        with pytest.raises(ValidationError):
            TestModel(quantity=_generate_quantity(model_dtype, quantity_unit, model_ndim))
    else:
        # when unit is None, any unit is valid
        TestModel(quantity=_generate_quantity(model_dtype, quantity_unit, model_ndim))

    if model_dtype:
        with pytest.raises(ValidationError):
            TestModel(quantity=_generate_quantity(quantity_dtype, model_unit, model_ndim))
    else:
        # when dtype is None, any dtype is valid
        TestModel(quantity=_generate_quantity(quantity_dtype, model_unit, model_ndim))

    # All good should work
    TestModel(quantity=_generate_quantity(model_dtype, model_unit, model_ndim))


def test_non_quantity_fails():
    """Test that passing a non quantity fails"""

    class TestModel(BaseModel):
        quantity: AstropyQuantity[None]

    with pytest.raises(ValidationError):
        TestModel(quantity=1)

    with pytest.raises(ValidationError):
        TestModel(quantity=u.s)

    with pytest.raises(ValidationError):
        TestModel(quantity=None)

    with pytest.raises(ValidationError):
        TestModel(quantity=np.array([1, 2, 3], dtype=np.float32))


@pytest.mark.parametrize("dtype", dtypes)
@pytest.mark.parametrize("ndim", ndims)
@pytest.mark.parametrize("unit", units)
def test_json_schema_return(dtype, ndim, unit):
    """
    Test the json schema representation
    """
    truth = {
        "title": None,
        "tag": AstropyQuantity._tags[0],
    }
    properties = {}
    value = {}
    if dtype is not None:
        value["datatype"] = dtype.__name__
    if ndim is not None:
        value["ndim"] = ndim
    if value:
        properties["value"] = {"title": None, "tag": NdArray._tags[0], **value}
    if unit is not None:
        properties["unit"] = {
            "title": None,
            "tag": AstropyUnit._tags[0],
            "enum": sorted(unit, key=_get_unit_symbol) if isinstance(unit, tuple) else [unit],
        }
    if properties:
        truth["properties"] = properties

    class TestModel(BaseModel):
        quantity: AstropyQuantity[dtype, ndim, unit]

    assert TestModel.model_json_schema()["properties"]["quantity"] == truth


@pytest.mark.parametrize("dtype", dtypes)
@pytest.mark.parametrize("ndim", [0, 2, 3])
@pytest.mark.parametrize("unit", units)
@pytest.mark.parametrize("default_shape", [(7, 8), (7, 8, 9)])
class TestMakeDefault:
    """Test creating a default value"""

    def test_default(self, dtype, ndim, unit, default_shape):
        """No arguments"""
        adaptor = get_adaptor(AstropyQuantity[dtype, ndim, unit, default_shape])

        # This will produce an error as a default cannot be made that satisfies the annotation
        if len(default_shape) < ndim:
            with pytest.raises(ValueError, match=r"Shape .* does not have the expected ndim .*"):
                adaptor.make_default()

            # Return early
            return

        unit_truth = unit[0] if isinstance(unit, tuple) else unit
        if unit_truth is None:
            unit_truth = u.dimensionless_unscaled

        # Test the default
        default = adaptor.make_default()
        assert isinstance(default, np.ndarray)

        # Default for dtype=None in np.fill is np.int64
        assert default.dtype == np.int64 if dtype is None else dtype
        assert default.ndim == ndim
        # When zero dimensional the shape is empty
        assert default.shape == (default_shape[-ndim:] if ndim > 0 else ())
        assert default.unit == unit_truth
        if ndim == 0:
            assert default == 0 * unit_truth
        else:
            assert (default == 0 * unit_truth).all()

    def test_fill(self, dtype, ndim, unit, default_shape):
        """Pass a fill value"""
        adaptor = get_adaptor(AstropyQuantity[dtype, ndim, unit, default_shape])
        fill = np.int64(4) if dtype is None else dtype(4)

        # This will produce an error as a default cannot be made that satisfies the annotation
        if len(default_shape) < ndim:
            with pytest.raises(ValueError, match=r"Shape .* does not have the expected ndim .*"):
                adaptor.make_default(fill=fill)

            # Return early
            return

        unit_truth = unit[0] if isinstance(unit, tuple) else unit
        if unit_truth is None:
            unit_truth = u.dimensionless_unscaled

        # Test the default
        default = adaptor.make_default(fill=fill)
        assert isinstance(default, np.ndarray)

        # Default for dtype=None in np.fill is np.int64
        assert default.dtype == np.int64 if dtype is None else dtype
        assert default.ndim == ndim
        # When zero dimensional the shape is empty
        assert default.shape == (default_shape[-ndim:] if ndim > 0 else ())
        assert default.unit == unit_truth
        if ndim == 0:
            assert default == fill * unit_truth
        else:
            assert (default == fill * unit_truth).all()

    @pytest.mark.parametrize("shape", [(1, 2), (3, 4, 5)])
    def test_shape(self, dtype, ndim, unit, default_shape, shape):
        """Pass a shape value"""
        adaptor = get_adaptor(AstropyQuantity[dtype, ndim, unit, default_shape])

        # This will produce an error as a default cannot be made that satisfies the annotation
        if len(shape) < ndim:
            with pytest.raises(ValueError, match=r"Shape .* does not have the expected ndim .*"):
                adaptor.make_default(shape=shape)

            # Return early
            return

        unit_truth = unit[0] if isinstance(unit, tuple) else unit
        if unit_truth is None:
            unit_truth = u.dimensionless_unscaled

        # Test the default
        default = adaptor.make_default(shape=shape)
        assert isinstance(default, np.ndarray)

        # Default for dtype=None in np.fill is np.int64
        assert default.dtype == np.int64 if dtype is None else dtype
        assert default.ndim == ndim
        # When zero dimensional the shape is empty
        assert default.shape == (shape[-ndim:] if ndim > 0 else ())
        assert default.unit == unit_truth
        if ndim == 0:
            assert default == 0 * unit_truth
        else:
            assert (default == 0 * unit_truth).all()

    def test_unit(self, dtype, ndim, unit, default_shape):
        """Pass a unit value"""
        adaptor = get_adaptor(AstropyQuantity[dtype, ndim, unit, default_shape])

        unit_ = unit[0] if isinstance(unit, tuple) else unit

        # This will produce an error as a default cannot be made that satisfies the annotation
        if len(default_shape) < ndim:
            with pytest.raises(ValueError, match=r"Shape .* does not have the expected ndim .*"):
                adaptor.make_default(unit=unit_)

            # Return early
            return

        unit_truth = unit[0] if isinstance(unit, tuple) else unit
        if unit_truth is None:
            unit_truth = u.dimensionless_unscaled

        # Test the default
        default = adaptor.make_default(unit=unit_)
        assert isinstance(default, np.ndarray)

        # Default for dtype=None in np.fill is np.int64
        assert default.dtype == np.int64 if dtype is None else dtype
        assert default.ndim == ndim
        # When zero dimensional the shape is empty
        assert default.shape == (default_shape[-ndim:] if ndim > 0 else ())
        assert default.unit == unit_truth
        if ndim == 0:
            assert default == 0 * unit_truth
        else:
            assert (default == 0 * unit_truth).all()

        with pytest.raises(ValueError, match=r"Unit .* is not in the list of valid units .*"):
            adaptor.make_default(unit=u.s)
