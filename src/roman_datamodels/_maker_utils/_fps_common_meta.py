from roman_datamodels.stnode import FlushOptions


def mk_fps_exposure(**kwargs):
    """
    Create a dummy BaseExposure instance with valid values for attributes
    required by the schema. Utilized by the model maker utilities below.

    Returns
    -------
    roman_datamodels.nodes.FpsExposure
    """
    from roman_datamodels.nodes import FpsExposure

    exp = FpsExposure(kwargs)
    exp.flush(FlushOptions.EXTRA, recurse=True)

    return exp


def mk_fps_guidestar(**kwargs):
    """
    Create a dummy BaseGuidestar instance with valid values for attributes
    required by the schema. Utilized by the model maker utilities below.

    Returns
    -------
    roman_datamodels.nodes.FpsGuidestar
    """
    from roman_datamodels.nodes import FpsGuidestar

    guide = FpsGuidestar(kwargs)
    guide.flush(FlushOptions.EXTRA, recurse=True)

    return guide


def mk_fps_statistics(**kwargs):
    """
    Create a dummy Statistics instance with valid values for attributes
    required by the schema. Utilized by the model maker utilities below.

    Returns
    -------
    roman_datamodels.nodes.FpsStatistics
    """
    from roman_datamodels.nodes import FpsStatistics

    stats = FpsStatistics(kwargs)
    stats.flush(FlushOptions.EXTRA, recurse=True)

    return stats


def mk_fps_wfi_mode(**kwargs):
    """
    Create a dummy WFI mode instance with valid values for attributes
    required by the schema. Utilized by the model maker utilities below.

    Returns
    -------
    roman_datamodels.nodes.FpsWfiMode
    """
    from roman_datamodels.nodes import FpsWfiMode

    mode = FpsWfiMode(kwargs)
    mode.flush(FlushOptions.EXTRA, recurse=True)

    return mode


def mk_fps_cal_step(**kwargs):
    """
    Create a dummy Level 2 Cal Step instance with valid values for attributes
    required by the schema. Utilized by the model maker utilities below.

    Returns
    -------
    roman_datamodels.nodes.FpsCalStep
    """
    from roman_datamodels.nodes import FpsCalStep

    calstep = FpsCalStep(kwargs)
    calstep.flush(FlushOptions.EXTRA, recurse=True)
    return calstep


def mk_fps_ref_file(**kwargs):
    """
    Create a dummy RefFile instance with valid values for attributes
    required by the schema. Utilized by the model maker utilities below.

    Returns
    -------
    roman_datamodels.nodes.FpsRefFile
    """
    from roman_datamodels.nodes import FpsRefFile

    ref_file = FpsRefFile(kwargs)
    ref_file.flush(FlushOptions.EXTRA, recurse=True)

    return ref_file
