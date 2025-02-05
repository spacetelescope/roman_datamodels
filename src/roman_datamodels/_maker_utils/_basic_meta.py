from roman_datamodels.stnode import FlushOptions


def mk_calibration_software_name(**kwargs):
    """
    Create a dummy CalibrationSoftwareName object with valid values

    Returns
    -------
    roman_datamodels.stnode.CalibrationSoftwareName
    """
    from roman_datamodels.nodes import CalibrationSoftwareName

    if "calibration_software_name" in kwargs:
        return CalibrationSoftwareName(kwargs["calibration_software_name"])
    return CalibrationSoftwareName.default()


def mk_calibration_software_version(**kwargs):
    """
    Create a dummy CalibrationSoftwareVersion object with valid values

    Returns
    -------
    roman_datamodels.stnode.CalibrationSoftwareVersion
    """
    from roman_datamodels.nodes import CalibrationSoftwareVersion

    if "calibration_software_version" in kwargs:
        return CalibrationSoftwareVersion(kwargs["calibration_software_version"])
    return CalibrationSoftwareVersion.default()


def mk_sdf_software_version(**kwargs):
    """
    Create a dummy SdfSoftwareVersion object with valid values

    Returns
    -------
    roman_datamodels.stnode.SdfSoftwareVersion
    """
    from roman_datamodels.nodes import SdfSoftwareVersion

    if "sdf_software_version" in kwargs:
        return SdfSoftwareVersion(kwargs["sdf_software_version"])
    return SdfSoftwareVersion.default()


def mk_filename(**kwargs):
    """
    Create a dummy Filename object with valid values

    Returns
    -------
    roman_datamodels.stnode.Filename
    """
    from roman_datamodels.nodes import Filename

    if "filename" in kwargs:
        return Filename(kwargs["filename"])
    return Filename.default()


def mk_file_date(**kwargs):
    """
    Create a dummy FileDate object with valid values

    Returns
    -------
    roman_datamodels.stnode.FileDate
    """
    from roman_datamodels.nodes import FileDate

    if "file_date" in kwargs:
        return FileDate(kwargs["file_date"])
    return FileDate.default()


def mk_model_type(**kwargs):
    """
    Create a dummy ModelType object with valid values

    Returns
    -------
    roman_datamodels.stnode.ModelType
    """
    from roman_datamodels.nodes import ModelType

    if "model_type" in kwargs:
        return ModelType(kwargs["model_type"])
    return ModelType.default()


def mk_origin(**kwargs):
    """
    Create a dummy Origin object with valid values

    Returns
    -------
    roman_datamodels.stnode.Origin
    """
    from roman_datamodels.nodes import Origin

    if "origin" in kwargs:
        return Origin(kwargs["origin"])
    return Origin.default()


def mk_prd_version(**kwargs):
    """
    Create a dummy PrdVersion object with valid values

    Returns
    -------
    roman_datamodels.stnode.PrdVersion
    """
    from roman_datamodels.nodes import PrdVersion

    if "prd_version" in kwargs:
        return PrdVersion(kwargs["prd_version"])
    return PrdVersion.default()


def mk_product_type(**kwargs):
    """
    Create a dummy ProductType object with valid values

    Returns
    -------
    roman_datamodels.stnode.ProductType
    """
    from roman_datamodels.nodes import ProductType

    if "product_type" in kwargs:
        return ProductType(kwargs["product_type"])
    return ProductType.default()


def mk_telescope(**kwargs):
    """
    Create a dummy Telescope object with valid values

    Returns
    -------
    roman_datamodels.stnode.Telescope
    """
    from roman_datamodels.nodes import Telescope

    if "telescope" in kwargs:
        return Telescope(kwargs["telescope"])
    return Telescope.default()


def mk_basic_meta(**kwargs):
    """
    Create a dummy basic metadata dictionary with valid values for attributes

    Returns
    -------
    dict (defined by the basic-1.0.0 schema)
    """
    from roman_datamodels.nodes import Basic

    meta = Basic(kwargs)
    meta.flush(FlushOptions.EXTRA, recurse=True)

    return meta
