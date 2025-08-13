from astropy import time

from roman_datamodels import stnode

from ._base import NOFN, NOSTR


def mk_calibration_software_name(**kwargs):
    """
    Create a dummy CalibrationSoftwareName object with valid values

    Returns
    -------
    roman_datamodels.stnode.CalibrationSoftwareName
    """
    return stnode.CalibrationSoftwareName(kwargs.get("calibration_software_name", "RomanCAL"))


def mk_calibration_software_version(**kwargs):
    """
    Create a dummy CalibrationSoftwareVersion object with valid values

    Returns
    -------
    roman_datamodels.stnode.CalibrationSoftwareVersion
    """
    return stnode.CalibrationSoftwareVersion(kwargs.get("calibration_software_version", "9.9.0"))


def mk_sdf_software_version(**kwargs):
    """
    Create a dummy SdfSoftwareVersion object with valid values

    Returns
    -------
    roman_datamodels.stnode.SdfSoftwareVersion
    """

    return stnode.SdfSoftwareVersion(kwargs.get("sdf_software_version", "7.7.7"))


def mk_filename(**kwargs):
    """
    Create a dummy Filename object with valid values

    Returns
    -------
    roman_datamodels.stnode.Filename
    """
    return stnode.Filename(kwargs.get("filename", NOFN))


def mk_file_date(**kwargs):
    """
    Create a dummy FileDate object with valid values

    Returns
    -------
    roman_datamodels.stnode.FileDate
    """

    return stnode.FileDate(kwargs.get("file_date", time.Time("2020-01-01T00:00:00.0", format="isot", scale="utc")))


def mk_model_type(**kwargs):
    """
    Create a dummy ModelType object with valid values

    Returns
    -------
    roman_datamodels.stnode.ModelType
    """
    return stnode.ModelType(kwargs.get("model_type", NOSTR))


def mk_origin(**kwargs):
    """
    Create a dummy Origin object with valid values

    Returns
    -------
    roman_datamodels.stnode.Origin
    """

    return stnode.Origin(kwargs.get("origin", "STSCI/SOC"))


def mk_prd_version(**kwargs):
    """
    Create a dummy PrdVersion object with valid values

    Returns
    -------
    roman_datamodels.stnode.PrdVersion
    """
    return stnode.PrdVersion(kwargs.get("prd_version", "8.8.8"))


def mk_product_type(**kwargs):
    """
    Create a dummy ProductType object with valid values

    Returns
    -------
    roman_datamodels.stnode.ProductType
    """
    return stnode.ProductType(kwargs.get("product_type", "l2"))


def mk_telescope(**kwargs):
    """
    Create a dummy Telescope object with valid values

    Returns
    -------
    roman_datamodels.stnode.Telescope
    """
    return stnode.Telescope(kwargs.get("telescope", "ROMAN"))


def mk_basic_meta(**kwargs):
    """
    Create a dummy basic metadata dictionary with valid values for attributes

    Returns
    -------
    dict (defined by the basic-1.0.0 schema)
    """
    meta = {}
    meta["calibration_software_name"] = kwargs.get("calibration_software_name", "RomanCAL")
    meta["calibration_software_version"] = kwargs.get("calibration_software_version", "9.9.0")
    meta["product_type"] = kwargs.get("product_type", "l2")
    meta["filename"] = kwargs.get("filename", NOFN)
    meta["file_date"] = kwargs.get("file_date", time.Time("2020-01-01T00:00:00.0", format="isot", scale="utc"))
    meta["model_type"] = kwargs.get("model_type", NOSTR)
    meta["origin"] = kwargs.get("origin", "STSCI/SOC")
    meta["prd_version"] = kwargs.get("prd_version", "8.8.8")
    meta["sdf_software_version"] = kwargs.get("sdf_software_version", "7.7.7")
    meta["telescope"] = kwargs.get("telescope", "ROMAN")

    return meta
