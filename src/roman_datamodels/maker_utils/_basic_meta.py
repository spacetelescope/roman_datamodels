from astropy import time

from roman_datamodels import stnode

from ._base import NOSTR


def mk_calibration_software_version():
    """
    Create a dummy CalibrationSoftwareVersion object with valid values

    Returns
    -------
    roman_datamodels.stnode.CalibrationSoftwareVersion
    """
    return stnode.CalibrationSoftwareVersion("9.9.0")


def mk_sdf_software_version():
    """
    Create a dummy SdfSoftwareVersion object with valid values

    Returns
    -------
    roman_datamodels.stnode.SdfSoftwareVersion
    """

    return stnode.SdfSoftwareVersion("7.7.7")


def mk_filename():
    """
    Create a dummy Filename object with valid values

    Returns
    -------
    roman_datamodels.stnode.Filename
    """
    return stnode.Filename(NOSTR)


def mk_file_date():
    """
    Create a dummy FileDate object with valid values

    Returns
    -------
    roman_datamodels.stnode.FileDate
    """

    return stnode.FileDate(time.Time("2020-01-01T00:00:00.0", format="isot", scale="utc"))


def mk_model_type():
    """
    Create a dummy ModelType object with valid values

    Returns
    -------
    roman_datamodels.stnode.ModelType
    """
    return stnode.ModelType(NOSTR)


def mk_origin():
    """
    Create a dummy Origin object with valid values

    Returns
    -------
    roman_datamodels.stnode.Origin
    """

    return stnode.Origin("STSCI")


def mk_prd_software_version():
    """
    Create a dummy PrdSoftwareVersion object with valid values

    Returns
    -------
    roman_datamodels.stnode.PrdSoftwareVersion
    """
    return stnode.PrdSoftwareVersion("8.8.8")


def mk_telescope():
    """
    Create a dummy Telescope object with valid values

    Returns
    -------
    roman_datamodels.stnode.Telescope
    """
    return stnode.Telescope("ROMAN")


def mk_basic_meta():
    """
    Create a dummy basic metadata dictionary with valid values for attributes
        TODO: This needs to be updated with constructors for the scalar objects

    Returns
    -------
    dict (defined by the basic-1.0.0 schema)
    """
    meta = {}
    meta["calibration_software_version"] = mk_calibration_software_version()
    meta["sdf_software_version"] = mk_sdf_software_version()
    meta["filename"] = mk_filename()
    meta["file_date"] = mk_file_date()
    meta["model_type"] = mk_model_type()
    meta["origin"] = mk_origin()
    meta["prd_software_version"] = mk_prd_software_version()
    meta["telescope"] = mk_telescope()

    return meta
