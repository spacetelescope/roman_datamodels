from roman_datamodels.stnode import FlushOptions


def mk_fps_calibration_software_version(**kwargs):
    """
    Create a dummy CalibrationSoftwareVersion object with valid values

    Returns
    -------
    roman_datamodels.stnode.FpsCalibrationSoftwareVersion
    """
    from roman_datamodels.nodes import FpsCalibrationSoftwareVersion

    if "calibration_software_version" in kwargs:
        return FpsCalibrationSoftwareVersion(kwargs["calibration_software_version"])
    return FpsCalibrationSoftwareVersion.default()


def mk_fps_sdf_software_version(**kwargs):
    """
    Create a dummy SdfSoftwareVersion object with valid values

    Returns
    -------
    roman_datamodels.stnode.FpsSdfSoftwareVersion
    """
    from roman_datamodels.nodes import FpsSdfSoftwareVersion

    if "sdf_software_version" in kwargs:
        return FpsSdfSoftwareVersion(kwargs["sdf_software_version"])
    return FpsSdfSoftwareVersion.default()


def mk_fps_filename(**kwargs):
    """
    Create a dummy Filename object with valid values

    Returns
    -------
    roman_datamodels.stnode.FpsFilename
    """
    from roman_datamodels.nodes import FpsFilename

    if "filename" in kwargs:
        return FpsFilename(kwargs["filename"])
    return FpsFilename.default()


def mk_fps_file_date(**kwargs):
    """
    Create a dummy FileDate object with valid values

    Returns
    -------
    roman_datamodels.stnode.FpsFileDate
    """
    from roman_datamodels.nodes import FpsFileDate

    if "file_date" in kwargs:
        return FpsFileDate(kwargs["file_date"])
    return FpsFileDate.default()


def mk_fps_model_type(**kwargs):
    """
    Create a dummy ModelType object with valid values

    Returns
    -------
    roman_datamodels.stnode.FpsModelType
    """
    from roman_datamodels.nodes import FpsModelType

    if "model_type" in kwargs:
        return FpsModelType(kwargs["model_type"])
    return FpsModelType.default()


def mk_fps_origin(**kwargs):
    """
    Create a dummy Origin object with valid values

    Returns
    -------
    roman_datamodels.stnode.FpsOrigin
    """
    from roman_datamodels.nodes import FpsOrigin

    if "origin" in kwargs:
        return FpsOrigin(kwargs["origin"])
    return FpsOrigin.default()


def mk_fps_prd_software_version(**kwargs):
    """
    Create a dummy PrdSoftwareVersion object with valid values

    Returns
    -------
    roman_datamodels.stnode.FpsPrdSoftwareVersion
    """
    from roman_datamodels.nodes import FpsPrdSoftwareVersion

    if "prd_software_version" in kwargs:
        return FpsPrdSoftwareVersion(kwargs["prd_software_version"])
    return FpsPrdSoftwareVersion.default()


def mk_fps_telescope(**kwargs):
    """
    Create a dummy Telescope object with valid values

    Returns
    -------
    roman_datamodels.stnode.fpsTelescope
    """
    from roman_datamodels.nodes import FpsTelescope

    if "telescope" in kwargs:
        return FpsTelescope(kwargs["telescope"])
    return FpsTelescope.default()


def mk_fps_basic_meta(**kwargs):
    """
    Create a dummy basic metadata dictionary with valid values for attributes

    Returns
    -------
    dict (defined by the fps/basic-1.0.0 schema)
    """
    from roman_datamodels.nodes import FpsBasic

    meta = FpsBasic(kwargs)
    meta.flush(FlushOptions.EXTRA, recurse=True)

    return meta
