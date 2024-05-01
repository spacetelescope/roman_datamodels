from astropy import time

from roman_datamodels import stnode

from ._base import NOSTR


def mk_tvac_calibration_software_version(**kwargs):
    """
    Create a dummy CalibrationSoftwareVersion object with valid values

    Returns
    -------
    roman_datamodels.stnode.TvacCalibrationSoftwareVersion
    """
    return stnode.TvacCalibrationSoftwareVersion(kwargs.get("calibration_software_version", "9.9.0"))


def mk_tvac_sdf_software_version(**kwargs):
    """
    Create a dummy SdfSoftwareVersion object with valid values

    Returns
    -------
    roman_datamodels.stnode.TvacSdfSoftwareVersion
    """

    return stnode.TvacSdfSoftwareVersion(kwargs.get("sdf_software_version", "7.7.7"))


def mk_tvac_filename(**kwargs):
    """
    Create a dummy Filename object with valid values

    Returns
    -------
    roman_datamodels.stnode.TvacFilename
    """
    return stnode.TvacFilename(kwargs.get("filename", NOSTR))


def mk_tvac_file_date(**kwargs):
    """
    Create a dummy FileDate object with valid values

    Returns
    -------
    roman_datamodels.stnode.TvacFileDate
    """

    return stnode.TvacFileDate(kwargs.get("file_date", time.Time("2020-01-01T00:00:00.0", format="isot", scale="utc")))


def mk_tvac_model_type(**kwargs):
    """
    Create a dummy ModelType object with valid values

    Returns
    -------
    roman_datamodels.stnode.TvacModelType
    """
    return stnode.TvacModelType(kwargs.get("model_type", NOSTR))


def mk_tvac_origin(**kwargs):
    """
    Create a dummy Origin object with valid values

    Returns
    -------
    roman_datamodels.stnode.TvacOrigin
    """

    return stnode.TvacOrigin(kwargs.get("origin", "STSCI"))


def mk_tvac_prd_software_version(**kwargs):
    """
    Create a dummy PrdSoftwareVersion object with valid values

    Returns
    -------
    roman_datamodels.stnode.TvacPrdSoftwareVersion
    """
    return stnode.TvacPrdSoftwareVersion(kwargs.get("prd_software_version", "8.8.8"))


def mk_tvac_telescope(**kwargs):
    """
    Create a dummy Telescope object with valid values

    Returns
    -------
    roman_datamodels.stnode.TvacTelescope
    """
    return stnode.TvacTelescope(kwargs.get("telescope", "ROMAN"))


def mk_tvac_basic_meta(**kwargs):
    """
    Create a dummy basic metadata dictionary with valid values for attributes

    Returns
    -------
    dict (defined by the tvac/basic-1.0.0 schema)
    """
    meta = {}
    meta["calibration_software_version"] = mk_tvac_calibration_software_version(**kwargs)
    meta["sdf_software_version"] = mk_tvac_sdf_software_version(**kwargs)
    meta["filename"] = mk_tvac_filename(**kwargs)
    meta["file_date"] = mk_tvac_file_date(**kwargs)
    meta["model_type"] = mk_tvac_model_type(**kwargs)
    meta["origin"] = mk_tvac_origin(**kwargs)
    meta["prd_software_version"] = mk_tvac_prd_software_version(**kwargs)
    meta["telescope"] = mk_tvac_telescope(**kwargs)

    return meta
