from astropy import time

from roman_datamodels import stnode

from ._base import NONUM, NOSTR


def mk_ground_exposure(**kwargs):
    """
    Create a dummy GroundExposure instance with valid values for attributes
    required by the schema. Utilized by the model maker utilities below.

    Returns
    -------
    roman_datamodels.stnode.Exposure
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
