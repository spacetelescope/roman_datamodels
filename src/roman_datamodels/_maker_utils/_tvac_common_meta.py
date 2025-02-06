from roman_datamodels.stnode import FlushOptions


def mk_tvac_exposure(**kwargs):
    """
    Create a dummy BaseExposure instance with valid values for attributes
    required by the schema. Utilized by the model maker utilities below.

    Returns
    -------
    roman_datamodels.stnode.TvacExposure
    """
    from roman_datamodels.nodes import TvacExposure

    exp = TvacExposure(kwargs)
    exp.flush(FlushOptions.EXTRA, recurse=True)

    return exp


def mk_tvac_guidestar(**kwargs):
    """
    Create a dummy Guidestar instance with valid values for attributes
    required by the schema. Utilized by the model maker utilities below.

    Returns
    -------
    roman_datamodels.stnode.TvacGuidestar
    """
    from roman_datamodels.nodes import TvacGuidestar

    guide = TvacGuidestar(kwargs)
    guide.flush(FlushOptions.EXTRA, recurse=True)

    return guide


def mk_tvac_statistics(**kwargs):
    """
    Create a dummy Statistics instance with valid values for attributes
    required by the schema. Utilized by the model maker utilities below.

    Returns
    -------
    roman_datamodels.stnode.TvacStatistics
    """
    from roman_datamodels.nodes import TvacStatistics

    stats = TvacStatistics(kwargs)
    stats.flush(FlushOptions.EXTRA, recurse=True)

    return stats


def mk_tvac_wfi_mode(**kwargs):
    """
    Create a dummy WFI mode instance with valid values for attributes
    required by the schema. Utilized by the model maker utilities below.

    Returns
    -------
    roman_datamodels.stnode.TvacWfiMode
    """
    from roman_datamodels.nodes import TvacWfiMode

    mode = TvacWfiMode(kwargs)
    mode.flush(FlushOptions.EXTRA, recurse=True)

    return mode


def mk_tvac_cal_step(**kwargs):
    """
    Create a dummy Level 2 Cal Step instance with valid values for attributes
    required by the schema. Utilized by the model maker utilities below.

    Returns
    -------
    roman_datamodels.stnode.TvacCalStep
    """
    from roman_datamodels.nodes import TvacCalStep

    cal_step = TvacCalStep(kwargs)
    cal_step.flush(FlushOptions.EXTRA, recurse=True)

    return cal_step


def mk_tvac_ref_file(**kwargs):
    """
    Create a dummy RefFile instance with valid values for attributes
    required by the schema. Utilized by the model maker utilities below.

    Returns
    -------
    roman_datamodels.stnode.TvacRefFile
    """
    from roman_datamodels.nodes import TvacRefFile

    ref_file = TvacRefFile(kwargs)
    ref_file.flush(FlushOptions.EXTRA, recurse=True)

    return ref_file
