"""
Run tests on the data model default generation
"""
import astropy.units as u
import numpy as np
import pytest
from astropy.time import Time

from roman_datamodels.datamodels import _generated
from roman_datamodels.pydantic import BaseRomanDataModel

models = [getattr(_generated, name) for name in _generated.__all__ if issubclass(getattr(_generated, name), BaseRomanDataModel)]


@pytest.mark.parametrize("model", models)
def test_make_default(model):
    """
    Simply test that making the model with defaults doesn't raise an error.
        This is only a face value check, not an exactness check.
    """

    # _shrink=True is used to limit testing memory use
    assert isinstance(model.make_default(_shrink=True), model)


#### TEST DEFAULT CORNER CASES ####
def test_read_pattern():
    """
    This is an arbitrary test for default model construction.
        Exposure is used because it contains read_pattern
    """

    model = _generated.Exposure.make_default(_shrink=True)

    # check read_pattern
    assert isinstance(model.read_pattern, list)
    assert model.read_pattern == [[1], [2, 3], [4], [5, 6, 7, 8], [9, 10], [11]]


def test_cal_logs():
    """
    This is an arbitrary test for default model construction.
        WfiMosaicModel is used purely as an example for something with CalLogs
    """

    model = _generated.WfiMosaicModel.make_default(_shrink=True)

    # check cal_logs
    assert isinstance(model.cal_logs, _generated.cal_logs.CalLogs)
    assert model.cal_logs.root == [
        "2021-11-15T09:15:07.12Z :: FlatFieldStep :: INFO :: Completed",
        "2021-11-15T10:22.55.55Z :: RampFittingStep :: WARNING :: Wow, lots of Cosmic Rays detected",
    ]


def test_p_exptype():
    """
    This is an arbitrary test for default model construction.
        RefExposureType is used purely to test the p_exptype field
    """

    model = _generated.RefExposureType.make_default(_shrink=True)

    # check p_exptype
    assert isinstance(model.exposure.p_exptype, str)
    assert model.exposure.p_exptype == "WFI_IMAGE|WFI_GRISM|WFI_PRISM|"


def test_coordinate_distortion_transform():
    """
    This is an arbitrary test for default model construction.
        DistortionRefModel is used purely to test the coordinate_distortion_transform field
    """
    from astropy import modeling

    model = _generated.DistortionRefModel.make_default(_shrink=True)

    # check coordinate_distortion_transform
    assert isinstance(model.coordinate_distortion_transform, modeling.CompoundModel)
    assert isinstance(model.coordinate_distortion_transform[0], modeling.models.Shift)
    assert model.coordinate_distortion_transform[0].offset == 1
    assert isinstance(model.coordinate_distortion_transform[1], modeling.models.Shift)
    assert model.coordinate_distortion_transform[1].offset == 2


def test_roman_data_model():
    """
    This is an arbitrary test for default model construction.
        Common is used purely to because it has field that are other RomanDataModels
    """

    model = _generated.Common.make_default(_shrink=True)

    # check coordinates (another RomanDataModel)
    assert isinstance(model.coordinates, _generated.Coordinates)
    assert model.coordinates.reference_frame == "ICRS"


def test_float():
    """
    This is an arbitrary test for default model construction
        Ephemeris is used purely as an example for something with a float value
    """

    model = _generated.Ephemeris.make_default(_shrink=True)

    # check earth_angle (float)
    assert isinstance(model.earth_angle, float)
    assert model.earth_angle == -999999.0


def test_int():
    """
    This is an arbitrary test for default model construction
        Guidestar is used purely as an example for something with an integer value
    """

    model = _generated.Guidestar.make_default(_shrink=True)

    # check gw_window_xstart (int)
    assert isinstance(model.gw_window_xstart, int)
    assert model.gw_window_xstart == -999999


def test_str():
    """
    This is an arbitrary test for default model construction
        Program is used purely as an example for something with a string value
    """

    model = _generated.Program.make_default(_shrink=True)

    # check title (str)
    assert isinstance(model.title, str)
    assert model.title == "dummy value"


def test_bool():
    """
    This is an arbitrary test for default model construction
        Visit is used purely as an example for something with a string value
    """

    model = _generated.Visit.make_default(_shrink=True)

    # check internal_target (bool)
    assert isinstance(model.internal_target, bool)
    assert model.internal_target is False


def test_enum():
    """
    This is an arbitrary test for default model construction
        Aperture is used purely as an example for something with an enumerated value
    """
    # Import the module directly so that we can access the enum directly
    from roman_datamodels.datamodels._generated import aperture

    model = aperture.Aperture.make_default(_shrink=True)

    # check name (enum)
    assert isinstance(model.name, str)
    #    Note: in py3.12+ we can use `assert model.name in aperture.Name` because
    #          __contains__ now works on the base value in addition to the enum item.
    assert model.name in [name.value for name in aperture.Name]
    assert model.name == "WFI_01_FULL"


def test_list():
    """
    This is an arbitrary test for default model construction
        AssociationsModel is used purely as an example for something with a list
    """
    # Import the module directly so that we can access a sub model directly
    from roman_datamodels.datamodels._generated.data_products import associations

    model = associations.AssociationsModel.make_default(_shrink=True)

    # check products (list)
    assert isinstance(model.products, list)
    for product in model.products:
        assert isinstance(product, associations.Product)
        assert product.name == "dummy value"

        assert isinstance(product.members, list)
        for member in product.members:
            assert isinstance(member, associations.Member)
            assert member.expname == "dummy value"
            assert member.exposerr == "dummy value"
            assert member.exptype == "SCIENCE"


def test_dict_and_phot_table():
    """
    This is an arbitrary test for default model construction
        WfiImgPhotomRefModel is used purely as an example for something with a dict. It also has a phot_table
    """
    keys = ("F062", "F087", "F106", "F129", "F146", "F158", "F184", "F213", "GRISM", "PRISM", "DARK")

    # Import the module directly so that we can access a sub model directly
    from roman_datamodels.datamodels._generated.reference_files import wfi_img_photom

    model = wfi_img_photom.WfiImgPhotomRefModel.make_default(_shrink=True)

    # check phot_table (phot_table)
    assert isinstance(model.phot_table, dict)
    assert tuple(model.phot_table.keys()) == keys
    for value in model.phot_table.values():
        assert isinstance(value, wfi_img_photom.PhotTable)
        assert value.photmjsr.value == 0.0
        assert value.uncertainty.value == 0.0
        assert value.pixelareasr.value == 0.0


def test_quantity():
    """
    This is an arbitrary test for default model construction.
        WfiScienceRawModel is used purely as an example for something with quantities.
    """

    model = _generated.WfiScienceRawModel.make_default(_shrink=True)

    # Check data (quantity)
    assert isinstance(model.data, u.Quantity)
    assert model.data.unit == u.DN
    assert model.data.shape == (8, 8, 8)
    assert model.data.dtype == np.uint16
    assert (model.data.value == 0).all()


def test_scalar_quantity():
    """
    This is an arbitrary test for default model construction
        Photometry is used purely as an example for something with a scalar astropy.Quantity
    """

    model = _generated.Photometry.make_default(_shrink=True)

    # check conversion_megajanskys (scalar astropy.Quantity)
    assert isinstance(model.conversion_megajanskys, u.Quantity)
    assert model.conversion_megajanskys.isscalar
    assert model.conversion_megajanskys.unit == u.MJy / u.sr
    assert model.conversion_megajanskys.value == 0.0


def test_time():
    """
    This is an arbitrary test for default model construction
        Basic is used purely as an example for something with a astropy.Time value
    """

    model = _generated.Basic.make_default(_shrink=True)

    # check file_date (time)
    assert isinstance(model.file_date, Time)
    assert str(model.file_date) == "2020-01-01T00:00:00.000"


def test_unit():
    """
    This is an arbitrary test for default model construction
        RefpixRefModel is used purely as an example for something with a astropy.unit value
    """

    model = _generated.RefpixRefModel.make_default(_shrink=True)

    # check meta.input_units (astropy.unit)
    assert model.meta.input_units == u.DN


def test_ndarray():
    """
    This is an arbitrary test for default model construction.
        WfiImageModel is used purely as an example for something with an ndarray.
    """

    model = _generated.WfiImageModel.make_default(_shrink=True)

    # check dq (ndarray)
    assert isinstance(model.dq, np.ndarray)
    assert model.dq.shape == (8, 8)
    assert model.dq.dtype == np.uint32


def test_aliased_field():
    """
    This is an arbitrary test for default model construction
        Observation is used purely as an example for something with an aliased field
    """

    model = _generated.Observation.make_default(_shrink=True)

    # check pass_ (true field)
    assert isinstance(model.pass_, int)
    assert model.pass_ == -999999


def test_optional_field():
    """
    This is an arbitrary test for default model construction
        WfiScienceRawModel is used purely as an example for something with an optional field
    """

    model = _generated.WfiScienceRawModel.make_default(_shrink=True)

    # resultantdq is optional
    assert model.resultantdq is None
