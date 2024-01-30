import astropy.units as u
import numpy as np
from astropy import time

from roman_datamodels import stnode

from ._base import NONUM, NOSTR


def mk_ground_exposure(**kwargs):
    """
    Create a dummy GroundExposure instance with valid values for attributes
    required by the schema. Utilized by the model maker utilities below.

    Returns
    -------
    roman_datamodels.stnode.GroundExposure
    """
    exp = stnode.GroundExposure()
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
    exp["read_pattern"] = kwargs.get("read_pattern", [[1], [2, 3], [4], [5, 6, 7, 8], [9, 10], [11]])

    return exp


def mk_ground_guidestar(**kwargs):
    """
    Create a dummy GroundGuidestar instance with valid values for attributes
    required by the schema. Utilized by the model maker utilities below.

    Returns
    -------
    roman_datamodels.stnode.GroundGuidestar
    """
    guide = stnode.GroundGuidestar()
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


def mk_ground_groundtest(**kwargs):
    """
    Create a dummy GroundGroundtest instance with valid values for attributes
    required by the schema. Utilized by the model maker utilities below.

    Returns
    -------
    roman_datamodels.stnode.GroundGroundtest
    """

    ground = stnode.GroundGroundtest()
    ground["test_name"] = kwargs.get("test_name", NOSTR)
    ground["test_phase"] = kwargs.get("test_phase", NOSTR)
    ground["test_environment"] = kwargs.get("test_environment", NOSTR)
    ground["test_script"] = kwargs.get("test_script", NOSTR)
    ground["product_date"] = kwargs.get("product_date", time.Time("2020-01-01T00:00:00.0", format="isot", scale="utc"))
    ground["product_version"] = kwargs.get("product_version", NOSTR)
    ground["conversion_date"] = kwargs.get("conversion_date", time.Time("2020-01-01T00:00:00.0", format="isot", scale="utc"))
    ground["conversion_version"] = kwargs.get("conversion_version", NOSTR)
    ground["filename_pnt5"] = kwargs.get("filename_pnt5", NOSTR)
    ground["filepath_level_pnt5"] = kwargs.get("filepath_level_pnt5", NOSTR)
    ground["filename_l1a"] = kwargs.get("filename_l1a", NOSTR)
    ground["detector_id"] = kwargs.get("detector_id", NOSTR)
    ground["detector_temp"] = kwargs.get("detector_temp", NONUM)
    ground["frames_temp"] = kwargs.get("frames_temp", np.zeros(6, dtype=np.float32))
    ground["ota_temp"] = kwargs.get("ota_temp", NONUM)
    ground["rcs_on"] = kwargs.get("rcs_on", False)
    ground["readout_col_num"] = kwargs.get("readout_col_num", NONUM)
    ground["detector_pixel_size"] = kwargs.get(
        "detector_pixel_size", u.Quantity(np.zeros(6, dtype=np.float32), unit=u.cm, dtype=np.float32)
    )
    ground["sensor_error"] = kwargs.get("sensor_error", np.zeros(6, dtype=np.float32))

    return ground
