from roman_datamodels.stnode import FlushOptions

from ._base import NOSTR


def mk_tvac_calibration_software_version(**kwargs):
    """
    Create a dummy CalibrationSoftwareVersion object with valid values

    Returns
    -------
    roman_datamodels.stnode.TvacCalibrationSoftwareVersion
    """
    from roman_datamodels.nodes import TvacCalibrationSoftwareVersion

    if "calibration_software_version" in kwargs:
        return TvacCalibrationSoftwareVersion(kwargs["calibration_software_version"])
    return TvacCalibrationSoftwareVersion.default()


def mk_tvac_sdf_software_version(**kwargs):
    """
    Create a dummy SdfSoftwareVersion object with valid values

    Returns
    -------
    roman_datamodels.stnode.TvacSdfSoftwareVersion
    """
    from roman_datamodels.nodes import TvacSdfSoftwareVersion

    if "sdf_software_version" in kwargs:
        return TvacSdfSoftwareVersion(kwargs["sdf_software_version"])
    return TvacSdfSoftwareVersion.default()


def mk_tvac_filename(**kwargs):
    """
    Create a dummy Filename object with valid values

    Returns
    -------
    roman_datamodels.stnode.TvacFilename
    """
    from roman_datamodels.nodes import TvacFilename

    if "filename" in kwargs:
        return TvacFilename(kwargs["filename"])
    return TvacFilename.default()


def mk_tvac_file_date(**kwargs):
    """
    Create a dummy FileDate object with valid values

    Returns
    -------
    roman_datamodels.stnode.TvacFileDate
    """
    from roman_datamodels.nodes import TvacFileDate

    if "file_date" in kwargs:
        return TvacFileDate(kwargs["file_date"])
    return TvacFileDate.default()


def mk_tvac_model_type(**kwargs):
    """
    Create a dummy ModelType object with valid values

    Returns
    -------
    roman_datamodels.stnode.TvacModelType
    """
    from roman_datamodels.nodes import TvacModelType

    if "model_type" in kwargs:
        return TvacModelType(kwargs["model_type"])
    return TvacModelType(NOSTR)


def mk_tvac_origin(**kwargs):
    """
    Create a dummy Origin object with valid values

    Returns
    -------
    roman_datamodels.stnode.TvacOrigin
    """
    from roman_datamodels.nodes import TvacOrigin

    if "origin" in kwargs:
        return TvacOrigin(kwargs["origin"])
    return TvacOrigin.default()


def mk_tvac_prd_software_version(**kwargs):
    """
    Create a dummy PrdSoftwareVersion object with valid values

    Returns
    -------
    roman_datamodels.stnode.TvacPrdSoftwareVersion
    """
    from roman_datamodels.nodes import TvacPrdSoftwareVersion

    if "prd_software_version" in kwargs:
        return TvacPrdSoftwareVersion(kwargs["prd_software_version"])
    return TvacPrdSoftwareVersion.default()


def mk_tvac_telescope(**kwargs):
    """
    Create a dummy Telescope object with valid values

    Returns
    -------
    roman_datamodels.stnode.TvacTelescope
    """
    from roman_datamodels.nodes import TvacTelescope

    if "telescope" in kwargs:
        return TvacTelescope(kwargs["telescope"])
    return TvacTelescope.default()


def mk_tvac_basic_meta(**kwargs):
    """
    Create a dummy basic metadata dictionary with valid values for attributes

    Returns
    -------
    dict (defined by the tvac/basic-1.0.0 schema)
    """
    from roman_datamodels.nodes import TvacBasic

    meta = TvacBasic(kwargs)
    meta.flush(FlushOptions.EXTRA, recurse=True)

    return meta
