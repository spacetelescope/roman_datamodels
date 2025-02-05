from roman_datamodels.stnode import FlushOptions


def mk_photometry(**kwargs):
    """
    Create a dummy Photometry instance with valid values for attributes
    required by the schema. Utilized by the model maker utilities below.

    Returns
    -------
    roman_datamodels.stnode.Photometry
    """
    from roman_datamodels.nodes import Photometry

    phot = Photometry(kwargs)
    phot.flush(FlushOptions.EXTRA, recurse=True)

    return phot


def mk_resample(**kwargs):
    """
    Create a dummy Resample instance with valid values for attributes
    required by the schema. Utilized by the model maker utilities below.

    Returns
    -------
    roman_datamodels.stnode.Resample
    """
    from roman_datamodels.nodes import Resample

    res = Resample(kwargs)
    res.flush(FlushOptions.EXTRA, recurse=True)

    return res


def mk_cal_logs(**kwargs):
    """
    Create a dummy CalLogs instance with valid values for attributes
    required by the schema.

    Returns
    -------
    roman_datamodels.stnode.CalLogs
    """
    from roman_datamodels.nodes import CalLogs

    if "cal_logs" in kwargs:
        return CalLogs(kwargs["cal_logs"])
    return CalLogs.default()


def mk_source_catalog(**kwargs):
    """
    Create a dummy Source Catalog instance with valid values for attributes
    required by the schema. Utilized by the model maker utilities below.

    Returns
    -------
    roman_datamodels.stnode.SourceCatalog
    """
    from roman_datamodels.nodes import SourceCatalog

    sd = SourceCatalog(kwargs)
    sd.flush(FlushOptions.EXTRA, recurse=True)

    return sd
