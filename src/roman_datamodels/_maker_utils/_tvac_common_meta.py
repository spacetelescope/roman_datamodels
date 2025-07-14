import numpy as np
from astropy import time
from astropy import units as u

from roman_datamodels import stnode

from ._base import NONUM, NOSTR


def mk_tvac_exposure(**kwargs):
    """
    Create a dummy BaseExposure instance with valid values for attributes
    required by the schema. Utilized by the model maker utilities below.

    Returns
    -------
    roman_datamodels.stnode.TvacExposure
    """
    exp = stnode.TvacExposure()
    exp["type"] = kwargs.get("type", "WFI_IMAGE")
    exp["start_time"] = kwargs.get("start_time", time.Time("2020-01-01T00:00:00.0", format="isot", scale="utc"))
    exp["ngroups"] = kwargs.get("ngroups", 6)
    exp["nframes"] = kwargs.get("nframes", 8)
    exp["data_problem"] = kwargs.get("data_problem", False)
    exp["frame_divisor"] = kwargs.get("frame_divisor", NONUM)
    exp["groupgap"] = kwargs.get("groupgap", 0)
    exp["frame_time"] = kwargs.get("frame_time", NONUM)
    exp["group_time"] = kwargs.get("group_time", NONUM)
    exp["exposure_time"] = kwargs.get("exposure_time", NONUM)
    exp["ma_table_name"] = kwargs.get("ma_table_name", NOSTR)
    exp["ma_table_number"] = kwargs.get("ma_table_number", NONUM)
    exp["read_pattern"] = kwargs.get("read_pattern", np.arange(1, 56).reshape((-1, 1)).tolist())

    return exp


def mk_tvac_guidestar(**kwargs):
    """
    Create a dummy Guidestar instance with valid values for attributes
    required by the schema. Utilized by the model maker utilities below.

    Returns
    -------
    roman_datamodels.stnode.TvacGuidestar
    """
    guide = stnode.TvacGuidestar()
    guide["gw_id"] = kwargs.get("gw_id", NOSTR)
    guide["gw_fgs_mode"] = kwargs.get("gw_fgs_mode", "WSM-ACQ-2")
    guide["data_start"] = kwargs.get("data_start", NONUM)
    guide["data_end"] = kwargs.get("data_end", NONUM)
    guide["gw_window_xstart"] = kwargs.get("gw_window_xstart", NONUM)
    guide["gw_window_ystart"] = kwargs.get("gw_window_ystart", NONUM)
    guide["gw_window_xstop"] = kwargs.get("gw_window_xstop", guide["gw_window_xstart"] + 170)
    guide["gw_window_ystop"] = kwargs.get("gw_window_ystop", guide["gw_window_ystart"] + 24)
    guide["gw_window_xsize"] = kwargs.get("gw_window_xsize", 170)
    guide["gw_window_ysize"] = kwargs.get("gw_window_ysize", 24)

    return guide


def mk_tvac_statistics(**kwargs):
    """
    Create a dummy Statistics instance with valid values for attributes
    required by the schema. Utilized by the model maker utilities below.

    Returns
    -------
    roman_datamodels.stnode.TvacStatistics
    """
    stats = stnode.TvacStatistics()
    stats["mean_counts_per_sec"] = kwargs.get("mean_counts_per_sec", NONUM * (u.DN / u.s))
    stats["median_counts_per_sec"] = kwargs.get("median_counts_per_sec", NONUM * (u.DN / u.s))
    stats["min_counts"] = kwargs.get("min_counts", u.Quantity(NONUM, u.DN, dtype=np.int32))
    stats["max_counts"] = kwargs.get("max_counts", u.Quantity(NONUM, u.DN, dtype=np.int32))

    return stats


def mk_tvac_wfi_mode(**kwargs):
    """
    Create a dummy WFI mode instance with valid values for attributes
    required by the schema. Utilized by the model maker utilities below.

    Returns
    -------
    roman_datamodels.stnode.TvacWfiMode
    """
    mode = stnode.TvacWfiMode()
    mode["name"] = kwargs.get("name", "WFI")
    mode["detector"] = kwargs.get("detector", "WFI01")
    mode["optical_element"] = kwargs.get("optical_element", "F158")

    return mode


def mk_tvac_cal_step(**kwargs):
    """
    Create a dummy Level 2 Cal Step instance with valid values for attributes
    required by the schema. Utilized by the model maker utilities below.

    Returns
    -------
    roman_datamodels.stnode.TvacCalStep
    """
    l2calstep = stnode.TvacCalStep()
    l2calstep["assign_wcs"] = kwargs.get("assign_wcs", "INCOMPLETE")
    l2calstep["dark"] = kwargs.get("dark", "INCOMPLETE")
    l2calstep["dq_init"] = kwargs.get("dq_init", "INCOMPLETE")
    l2calstep["flat_field"] = kwargs.get("flat_field", "INCOMPLETE")
    l2calstep["flux"] = kwargs.get("flux", "INCOMPLETE")
    l2calstep["jump"] = kwargs.get("jump", "INCOMPLETE")
    l2calstep["linearity"] = kwargs.get("linearity", "INCOMPLETE")
    l2calstep["photom"] = kwargs.get("photom", "INCOMPLETE")
    l2calstep["source_detection"] = kwargs.get("source_detection", "INCOMPLETE")
    l2calstep["outlier_detection"] = kwargs.get("outlier_detection", "INCOMPLETE")
    l2calstep["ramp_fit"] = kwargs.get("ramp_fit", "INCOMPLETE")
    l2calstep["refpix"] = kwargs.get("refpix", "INCOMPLETE")
    l2calstep["saturation"] = kwargs.get("saturation", "INCOMPLETE")
    l2calstep["skymatch"] = kwargs.get("skymatch", "INCOMPLETE")
    l2calstep["tweakreg"] = kwargs.get("tweakreg", "INCOMPLETE")

    return l2calstep


def mk_tvac_ref_file(**kwargs):
    """
    Create a dummy RefFile instance with valid values for attributes
    required by the schema. Utilized by the model maker utilities below.

    Returns
    -------
    roman_datamodels.stnode.TvacRefFile
    """
    ref_file = stnode.TvacRefFile()
    ref_file["dark"] = kwargs.get("dark", "N/A")
    ref_file["distortion"] = kwargs.get("distortion", "N/A")
    ref_file["flat"] = kwargs.get("flat", "N/A")
    ref_file["gain"] = kwargs.get("gain", "N/A")
    ref_file["linearity"] = kwargs.get("linearity", "N/A")
    ref_file["mask"] = kwargs.get("mask", "N/A")
    ref_file["readnoise"] = kwargs.get("readnoise", "N/A")
    ref_file["saturation"] = kwargs.get("saturation", "N/A")
    ref_file["photom"] = kwargs.get("photom", "N/A")
    ref_file["crds"] = kwargs.get("crds", {"sw_version": "12.3.1", "context_used": "roman_0815.pmap"})

    return ref_file
