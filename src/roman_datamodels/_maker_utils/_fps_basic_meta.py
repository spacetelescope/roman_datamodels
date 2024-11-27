from astropy import time

from roman_datamodels import stnode

from ._base import NOSTR


def mk_fps_calibration_software_version(**kwargs):
    """
    Create a dummy CalibrationSoftwareVersion object with valid values

    Returns
    -------
    roman_datamodels.stnode.FpsCalibrationSoftwareVersion
    """
    return stnode.FpsCalibrationSoftwareVersion(kwargs.get("calibration_software_version", "9.9.0"))


def mk_fps_sdf_software_version(**kwargs):
    """
    Create a dummy SdfSoftwareVersion object with valid values

    Returns
    -------
    roman_datamodels.stnode.FpsSdfSoftwareVersion
    """

    return stnode.FpsSdfSoftwareVersion(kwargs.get("sdf_software_version", "7.7.7"))


def mk_fps_filename(**kwargs):
    """
    Create a dummy Filename object with valid values

    Returns
    -------
    roman_datamodels.stnode.FpsFilename
    """
    return stnode.FpsFilename(kwargs.get("filename", NOSTR))


def mk_fps_file_date(**kwargs):
    """
    Create a dummy FileDate object with valid values

    Returns
    -------
    roman_datamodels.stnode.FpsFileDate
    """

    return stnode.FpsFileDate(kwargs.get("file_date", time.Time("2020-01-01T00:00:00.0", format="isot", scale="utc")))


def mk_fps_model_type(**kwargs):
    """
    Create a dummy ModelType object with valid values

    Returns
    -------
    roman_datamodels.stnode.FpsModelType
    """
    return stnode.FpsModelType(kwargs.get("model_type", NOSTR))


def mk_fps_origin(**kwargs):
    """
    Create a dummy Origin object with valid values

    Returns
    -------
    roman_datamodels.stnode.FpsOrigin
    """

    return stnode.FpsOrigin(kwargs.get("origin", "STSCI"))


def mk_fps_prd_software_version(**kwargs):
    """
    Create a dummy PrdSoftwareVersion object with valid values

    Returns
    -------
    roman_datamodels.stnode.FpsPrdSoftwareVersion
    """
    return stnode.FpsPrdSoftwareVersion(kwargs.get("prd_software_version", "8.8.8"))


def mk_fps_telescope(**kwargs):
    """
    Create a dummy Telescope object with valid values

    Returns
    -------
    roman_datamodels.stnode.fpsTelescope
    """
    return stnode.FpsTelescope(kwargs.get("telescope", "ROMAN"))


def mk_fps_basic_meta(**kwargs):
    """
    Create a dummy basic metadata dictionary with valid values for attributes

    Returns
    -------
    dict (defined by the fps/basic-1.0.0 schema)
    """
    meta = {}
    meta["calibration_software_version"] = mk_fps_calibration_software_version(**kwargs)
    meta["sdf_software_version"] = mk_fps_sdf_software_version(**kwargs)
    meta["filename"] = mk_fps_filename(**kwargs)
    meta["file_date"] = mk_fps_file_date(**kwargs)
    meta["model_type"] = mk_fps_model_type(**kwargs)
    meta["origin"] = mk_fps_origin(**kwargs)
    meta["prd_software_version"] = mk_fps_prd_software_version(**kwargs)
    meta["telescope"] = mk_fps_telescope(**kwargs)

    return meta
