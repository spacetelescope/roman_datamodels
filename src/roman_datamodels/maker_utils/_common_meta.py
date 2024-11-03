import numpy as np
from astropy import coordinates, time
from astropy import units as u
from astropy.modeling import models
from astropy.table import QTable
from gwcs import coordinate_frames
from gwcs.wcs import WCS

from roman_datamodels import stnode

from ._base import NONUM, NOSTR
from ._basic_meta import mk_basic_meta
from ._tagged_nodes import mk_cal_logs, mk_photometry, mk_resample, mk_source_detection


def mk_exposure(**kwargs):
    """
    Create a dummy Exposure instance with valid values for attributes
    required by the schema. Utilized by the model maker utilities below.

    Returns
    -------
    roman_datamodels.stnode.Exposure
    """
    exp = stnode.Exposure()

    exp["type"] = kwargs.get("type", "WFI_IMAGE")
    exp["nresultants"] = kwargs.get("nresultants", 6)
    exp["start_time"] = kwargs.get("start_time", time.Time("2020-01-01T00:00:00.0", format="isot", scale="utc"))
    exp["mid_time"] = kwargs.get("mid_time", time.Time("2020-01-01T01:00:00.0", format="isot", scale="utc"))
    exp["end_time"] = kwargs.get("end_time", time.Time("2020-01-01T02:00:00.0", format="isot", scale="utc"))
    # exp["ngroups"] = kwargs.get("ngroups", 6)
    # exp["nframes"] = kwargs.get("nframes", 8)
    exp["data_problem"] = kwargs.get("data_problem", False)
    # exp["frame_divisor"] = kwargs.get("frame_divisor", NONUM)
    # exp["groupgap"] = kwargs.get("groupgap", 0)
    exp["frame_time"] = kwargs.get("frame_time", NONUM)
    exp["exposure_time"] = kwargs.get("exposure_time", NONUM)
    exp["ma_table_name"] = kwargs.get("ma_table_name", NOSTR)
    exp["ma_table_number"] = kwargs.get("ma_table_number", NONUM)
    exp["read_pattern"] = kwargs.get("read_pattern", [[1], [2, 3], [4], [5, 6, 7, 8], [9, 10], [11]])
    # exp["start_time_mjd"] = kwargs.get("start_time_mjd", NONUM)
    # exp["mid_time_mjd"] = kwargs.get("mid_time_mjd", NONUM)
    # exp["end_time_mjd"] = kwargs.get("end_time_mjd", NONUM)
    # exp["start_time_tdb"] = kwargs.get("start_time_tdb", NONUM)
    # exp["mid_time_tdb"] = kwargs.get("mid_time_tdb", NONUM)
    # exp["end_time_tdb"] = kwargs.get("end_time_tdb", NONUM)
    # exp["sca_number"] = kwargs.get("sca_number", NONUM)
    # exp["gain_factor"] = kwargs.get("gain_factor", NONUM)
    # exp["integration_time"] = kwargs.get("integration_time", NONUM)
    # exp["elapsed_exposure_time"] = kwargs.get("elapsed_exposure_time", NONUM)
    exp["effective_exposure_time"] = kwargs.get("effective_exposure_time", NONUM)
    # exp["duration"] = kwargs.get("duration", NONUM)
    # exp["level0_compressed"] = kwargs.get("level0_compressed", True)
    exp["truncated"] = kwargs.get("truncated", False)

    return exp


def mk_wfi_mode(**kwargs):
    """
    Create a dummy WFI mode instance with valid values for attributes
    required by the schema. Utilized by the model maker utilities below.

    Returns
    -------
    roman_datamodels.stnode.WfiMode
    """
    mode = stnode.WfiMode()
    mode["name"] = kwargs.get("name", "WFI")
    mode["detector"] = kwargs.get("detector", "WFI01")
    mode["optical_element"] = kwargs.get("optical_element", "F158")

    return mode


def mk_program(**kwargs):
    """
    Create a dummy Program instance with valid values for attributes
    required by the schema. Utilized by the model maker utilities below.

    Returns
    -------
    roman_datamodels.stnode.Program
    """
    prog = stnode.Program()
    prog["title"] = kwargs.get("title", NOSTR)
    prog["investigator_name"] = kwargs.get("investigator_name", NOSTR)
    prog["category"] = kwargs.get("category", NOSTR)
    prog["subcategory"] = kwargs.get("subcategory", "None")
    prog["science_category"] = kwargs.get("science_category", NOSTR)
    prog["continuation_id"] = kwargs.get("continuation_id", NONUM)

    return prog


def mk_observation(**kwargs):
    """
    Create a dummy Observation instance with valid values for attributes
    required by the schema. Utilized by the model maker utilities below.

    Returns
    -------
    roman_datamodels.stnode.Observation
    """
    obs = stnode.Observation()
    obs["observation_id"] = kwargs.get("observation_id", NOSTR)
    obs["visit_id"] = kwargs.get("visit_id", NOSTR)
    obs["program"] = kwargs.get("program", 1)
    obs["execution_plan"] = kwargs.get("execution_plan", 1)
    obs["pass"] = kwargs.get("pass", 1)
    obs["segment"] = kwargs.get("segment", 1)
    obs["observation"] = kwargs.get("observation", 1)
    obs["visit"] = kwargs.get("visit", 1)
    obs["visit_file_group"] = kwargs.get("visit_file_group", 1)
    obs["visit_file_sequence"] = kwargs.get("visit_file_sequence", 1)
    obs["visit_file_activity"] = kwargs.get("visit_file_activity", "01")
    obs["exposure"] = kwargs.get("exposure", 1)
    # obs["template"] = kwargs.get("template", NOSTR)
    # obs["observation_label"] = kwargs.get("observation_label", NOSTR)
    # obs["survey"] = kwargs.get("survey", "N/A")

    return obs


def mk_outlier_detection(**kwargs):
    """
    Create a dummy Outlier Detection instance with valid values for attributes
    required by the schema. Utilized by the model maker utilities below.

    Returns
    -------
    roman_datamodels.stnode.OutlierDetection
    """
    od = stnode.OutlierDetection()
    od["good_bits"] = kwargs.get("good_bits", "NA")

    return od


def mk_sky_background(**kwargs):
    """
    Create a dummy Sky Background instance with valid values for attributes
    required by the schema. Utilized by the model maker utilities below.

    Returns
    -------
    roman_datamodels.stnode.SkyBackground
    """
    sb = stnode.SkyBackground()
    sb["level"] = kwargs.get("level", NONUM)
    sb["method"] = kwargs.get("method", "None")
    sb["subtracted"] = kwargs.get("subtracted", False)

    return sb


def mk_ephemeris(**kwargs):
    """
    Create a dummy Ephemeris instance with valid values for attributes
    required by the schema. Utilized by the model maker utilities below.

    Returns
    -------
    roman_datamodels.stnode.Ephemeris
    """
    ephem = stnode.Ephemeris()
    ephem["earth_angle"] = kwargs.get("earth_angle", NONUM)
    ephem["moon_angle"] = kwargs.get("moon_angle", NONUM)
    ephem["ephemeris_reference_frame"] = kwargs.get("ephemeris_reference_frame", NOSTR)
    ephem["sun_angle"] = kwargs.get("sun_angle", NONUM)
    ephem["type"] = kwargs.get("type", "DEFINITIVE")
    ephem["time"] = kwargs.get("time", NONUM)
    ephem["spatial_x"] = kwargs.get("spatial_x", NONUM)
    ephem["spatial_y"] = kwargs.get("spatial_y", NONUM)
    ephem["spatial_z"] = kwargs.get("spatial_z", NONUM)
    ephem["velocity_x"] = kwargs.get("velocity_x", NONUM)
    ephem["velocity_y"] = kwargs.get("velocity_y", NONUM)
    ephem["velocity_z"] = kwargs.get("velocity_z", NONUM)

    return ephem


def mk_visit(**kwargs):
    """
    Create a dummy Visit instance with valid values for attributes
    required by the schema. Utilized by the model maker utilities below.

    Returns
    -------
    roman_datamodels.stnode.Visit
    """
    visit = stnode.Visit()
    visit["dither"] = kwargs.get(
        "dither", {"primary_name": None, "subpixel_name": None, "executed_pattern": np.arange(1, 10).tolist()}
    )
    visit["engineering_quality"] = kwargs.get("engineering_quality", "OK")
    visit["pointing_engineering_source"] = kwargs.get("pointing_engineering_source", "CALCULATED")
    visit["type"] = kwargs.get("type", "PRIME_TARGETED_FIXED")
    visit["start_time"] = kwargs.get("start_time", time.Time("2020-01-01T00:00:00.0", format="isot", scale="utc"))
    visit["end_time"] = kwargs.get("end_time", time.Time("2020-01-01T00:00:00.0", format="isot", scale="utc"))
    visit["status"] = kwargs.get("status", "UNSUCCESSFUL")
    visit["nexposures"] = kwargs.get("nexposures", NONUM)
    visit["internal_target"] = kwargs.get("internal_target", False)
    # visit["target_of_opportunity"] = kwargs.get("target_of_opportunity", False)

    return visit


def mk_coordinates(**kwargs):
    """
    Create a dummy Coordinates instance with valid values for attributes
    required by the schema. Utilized by the model maker utilities below.

    Returns
    -------
    roman_datamodels.stnode.Coordinates
    """
    coord = stnode.Coordinates()
    coord["reference_frame"] = kwargs.get("reference_frame", "ICRS")

    return coord


def mk_pointing(**kwargs):
    """
    Create a dummy Pointing instance with valid values for attributes
    required by the schema. Utilized by the model maker utilities below.

    Returns
    -------
    roman_datamodels.stnode.Pointing
    """
    point = stnode.Pointing()
    point["ra_v1"] = kwargs.get("ra_v1", NONUM)
    point["dec_v1"] = kwargs.get("dec_v1", NONUM)
    point["pa_v3"] = kwargs.get("pa_v3", NONUM)
    point["target_aperture"] = kwargs.get("target_aperture", NOSTR)
    point["target_ra"] = kwargs.get("target_ra", NONUM)
    point["target_dec"] = kwargs.get("target_dec", NONUM)

    return point


def mk_velocity_aberration(**kwargs):
    """
    Create a dummy Velocity Aberration instance with valid values for attributes
    required by the schema. Utilized by the model maker utilities below.

    Returns
    -------
    roman_datamodels.stnode.VelocityAberration
    """
    vab = stnode.VelocityAberration()
    vab["ra_reference"] = kwargs.get("ra_reference", NONUM)
    vab["dec_reference"] = kwargs.get("dec_reference", NONUM)
    vab["scale_factor"] = kwargs.get("scale_factor", NONUM)

    return vab


def mk_wcsinfo(**kwargs):
    """
    Create a dummy WCS Info instance with valid values for attributes
    required by the schema. Utilized by the model maker utilities below.

    Returns
    -------
    roman_datamodels.stnode.Wcsinfo
    """
    wcsi = stnode.Wcsinfo()
    wcsi["aperture_name"] = kwargs.get("aperture_name", "WFI01_FULL")
    wcsi["pa_aperture"] = kwargs.get("pa_aperture", NONUM)
    wcsi["v2_ref"] = kwargs.get("v2_ref", NONUM)
    wcsi["v3_ref"] = kwargs.get("v3_ref", NONUM)
    wcsi["vparity"] = kwargs.get("vparity", -1)
    wcsi["v3yangle"] = kwargs.get("v3yangle", NONUM)
    wcsi["ra_ref"] = kwargs.get("ra_ref", NONUM)
    wcsi["dec_ref"] = kwargs.get("dec_ref", NONUM)
    wcsi["roll_ref"] = kwargs.get("roll_ref", NONUM)
    wcsi["s_region"] = kwargs.get("s_region", NOSTR)

    return wcsi


def mk_l2_cal_step(**kwargs):
    """
    Create a dummy Level 2 Cal Step instance with valid values for attributes
    required by the schema. Utilized by the model maker utilities below.

    Returns
    -------
    roman_datamodels.stnode.L2CalStep
    """
    l2calstep = stnode.L2CalStep()
    l2calstep["assign_wcs"] = kwargs.get("assign_wcs", "INCOMPLETE")
    l2calstep["dark"] = kwargs.get("dark", "INCOMPLETE")
    l2calstep["dq_init"] = kwargs.get("dq_init", "INCOMPLETE")
    l2calstep["flat_field"] = kwargs.get("flat_field", "INCOMPLETE")
    l2calstep["flux"] = kwargs.get("flux", "INCOMPLETE")
    l2calstep["linearity"] = kwargs.get("linearity", "INCOMPLETE")
    l2calstep["outlier_detection"] = kwargs.get("outlier_detection", "INCOMPLETE")
    l2calstep["photom"] = kwargs.get("photom", "INCOMPLETE")
    l2calstep["source_detection"] = kwargs.get("source_detection", "INCOMPLETE")
    l2calstep["ramp_fit"] = kwargs.get("ramp_fit", "INCOMPLETE")
    l2calstep["refpix"] = kwargs.get("refpix", "INCOMPLETE")
    l2calstep["saturation"] = kwargs.get("saturation", "INCOMPLETE")
    l2calstep["skymatch"] = kwargs.get("skymatch", "INCOMPLETE")
    l2calstep["tweakreg"] = kwargs.get("tweakreg", "INCOMPLETE")

    return l2calstep


def mk_l3_cal_step(**kwargs):
    """
    Create a dummy Level 3 Cal Step instance with valid values for attributes
    required by the schema. Utilized by the model maker utilities below.

    Returns
    -------
    roman_datamodels.stnode.L3CalStep
    """
    l3calstep = stnode.L3CalStep()
    l3calstep["flux"] = kwargs.get("flux", "INCOMPLETE")
    l3calstep["outlier_detection"] = kwargs.get("outlier_detection", "INCOMPLETE")
    l3calstep["skymatch"] = kwargs.get("skymatch", "INCOMPLETE")
    l3calstep["resample"] = kwargs.get("resample", "INCOMPLETE")

    return l3calstep


def mk_guidestar(**kwargs):
    """
    Create a dummy Guidestar instance with valid values for attributes
    required by the schema. Utilized by the model maker utilities below.

    Returns
    -------
    roman_datamodels.stnode.Guidestar
    """
    guide = stnode.Guidestar()

    guide["guide_window_id"] = kwargs.get("guide_window_id", NOSTR)
    guide["guide_mode"] = kwargs.get("guide_mode", "WSM-ACQ-2")
    guide["data_start"] = kwargs.get("data_start", time.Time("2020-01-01T00:00:00.0", format="isot", scale="utc"))
    guide["data_end"] = kwargs.get("data_end", time.Time("2020-01-01T01:00:00.0", format="isot", scale="utc"))
    guide["window_xstart"] = kwargs.get("window_xstart", NONUM)
    guide["window_ystart"] = kwargs.get("window_ystart", NONUM)
    guide["window_xstop"] = kwargs.get("window_xstop", guide["window_xstart"] + 170)
    guide["window_ystop"] = kwargs.get("window_ystop", guide["window_ystart"] + 24)
    guide["window_xsize"] = kwargs.get("window_xsize", 170)
    guide["window_ysize"] = kwargs.get("window_ysize", 24)

    guide["ra"] = kwargs.get("ra", NONUM)
    guide["dec"] = kwargs.get("dec", NONUM)
    guide["ra_uncertainty"] = kwargs.get("ra_uncertainty", NONUM)
    guide["dec_uncertainty"] = kwargs.get("dec_uncertainty", NONUM)
    guide["fgs_magnitude"] = kwargs.get("fgs_magnitude", NONUM)
    guide["fgs_magnitude_uncertainty"] = kwargs.get("fgs_magnitude_uncertainty", NONUM)
    guide["guide_star_id"] = kwargs.get("guide_star_id", NOSTR)
    guide["gsc_version"] = kwargs.get("gsc_version", NOSTR)
    guide["centroid_x"] = kwargs.get("centroid_x", NONUM)
    guide["centroid_y"] = kwargs.get("centroid_y", NONUM)
    guide["centroid_x_uncertainty"] = kwargs.get("centroid_x_uncertainty", NONUM)
    guide["centroid_y_uncertainty"] = kwargs.get("centroid_y_uncertainty", NONUM)
    guide["epoch"] = kwargs.get("epoch", NOSTR)
    guide["proper_motion_ra"] = kwargs.get("proper_motion_ra", NONUM)
    guide["proper_motion_dec"] = kwargs.get("proper_motion_dec", NONUM)
    guide["parallax"] = kwargs.get("parallax", NONUM)
    guide["centroid_rms"] = kwargs.get("centroid_rms", NONUM)

    return guide


def mk_ref_file(**kwargs):
    """
    Create a dummy RefFile instance with valid values for attributes
    required by the schema. Utilized by the model maker utilities below.

    Returns
    -------
    roman_datamodels.stnode.RefFile
    """
    ref_file = stnode.RefFile()
    ref_file["dark"] = kwargs.get("dark", "N/A")
    ref_file["distortion"] = kwargs.get("distortion", "N/A")
    ref_file["flat"] = kwargs.get("flat", "N/A")
    ref_file["gain"] = kwargs.get("gain", "N/A")
    ref_file["linearity"] = kwargs.get("linearity", "N/A")
    ref_file["mask"] = kwargs.get("mask", "N/A")
    ref_file["readnoise"] = kwargs.get("readnoise", "N/A")
    ref_file["refpix"] = kwargs.get("refpix", "N/A")
    ref_file["saturation"] = kwargs.get("saturation", "N/A")
    ref_file["inverse_linearity"] = kwargs.get("inverse_linearity", "N/A")
    ref_file["photom"] = kwargs.get("photom", "N/A")
    ref_file["area"] = kwargs.get("area", "N/A")
    ref_file["crds"] = kwargs.get("crds", {"sw_version": "12.3.1", "context_used": "roman_0815.pmap"})

    return ref_file


def mk_common_meta(**kwargs):
    """
    Create a dummy common metadata dictionary with valid values for attributes

    Returns
    -------
    dict (defined by the common-1.0.0 schema)
    """
    meta = mk_basic_meta(**kwargs)
    meta["coordinates"] = mk_coordinates(**kwargs.get("coordinates", {}))
    meta["ephemeris"] = mk_ephemeris(**kwargs.get("ephemeris", {}))
    meta["exposure"] = mk_exposure(**kwargs.get("exposure", {}))
    meta["guide_star"] = mk_guidestar(**kwargs.get("guide_star", {}))
    meta["instrument"] = mk_wfi_mode(**kwargs.get("instrument", {}))
    meta["observation"] = mk_observation(**kwargs.get("observation", {}))
    meta["pointing"] = mk_pointing(**kwargs.get("pointing", {}))
    meta["program"] = mk_program(**kwargs.get("program", {}))
    meta["rcs"] = mk_rcs(**kwargs.get("rcs", {}))
    meta["ref_file"] = mk_ref_file(**kwargs.get("ref_file", {}))
    meta["velocity_aberration"] = mk_velocity_aberration(**kwargs.get("velocity_aberration", {}))
    meta["visit"] = mk_visit(**kwargs.get("visit", {}))
    meta["wcsinfo"] = mk_wcsinfo(**kwargs.get("wcsinfo", {}))

    return meta


def mk_l2_meta(**kwargs):
    """
    Create a dummy common metadata dictionary with valid values for attributes and add
    the additional photometry metadata

    Returns
    -------
    dict (defined by the common-1.0.0 schema with additional photometry metadata)
    """

    meta = mk_common_meta(**kwargs)

    meta["cal_step"] = mk_l2_cal_step(**kwargs.get("cal_step", {}))
    meta["photometry"] = mk_photometry(**kwargs.get("photometry", {}))
    meta["outlier_detection"] = mk_outlier_detection(**kwargs.get("outlier_detection", {}))
    meta["background"] = mk_sky_background(**kwargs.get("background", {}))
    meta["source_detection"] = mk_source_detection(**kwargs.get("source_detection", {}))
    meta["cal_logs"] = mk_cal_logs(**kwargs)

    return meta


def mk_ramp_meta(**kwargs):
    """
    Create a dummy common metadata dictionary with valid values for attributes and add
    the additional photometry metadata

    Returns
    -------
    dict (defined by the common-1.0.0 schema with additional photometry metadata)
    """

    meta = mk_common_meta(**kwargs)

    meta["cal_step"] = mk_l2_cal_step(**kwargs.get("cal_step", {}))

    return meta


def mk_mosaic_meta(**kwargs):
    """
    Create a dummy metadata dictionary with valid values for mosaic attributes.

    Returns
    -------
    dict (defined by the wfi_mosaic-1.0.0 schema)
    """

    meta = mk_basic_meta(**kwargs)
    meta["basic"] = mk_mosaic_basic(**kwargs.get("basic", {}))
    meta["asn"] = mk_mosaic_associations(**kwargs.get("asn", {}))
    meta["cal_step"] = mk_l3_cal_step(**kwargs.get("cal_step", {}))
    meta["coordinates"] = mk_coordinates(**kwargs.get("coordinates", {}))
    meta["individual_image_meta"] = mk_individual_image_meta(**kwargs.get("individual_image_meta", {}))
    meta["photometry"] = mk_photometry(**kwargs.get("photometry", {}))
    meta["program"] = mk_program(**kwargs.get("program", {}))
    meta["ref_file"] = mk_ref_file(**kwargs.get("ref_file", {}))
    meta["resample"] = mk_resample(**kwargs.get("resample", {}))
    meta["wcsinfo"] = mk_mosaic_wcsinfo(**kwargs.get("wcsinfo", {}))

    return meta


def mk_mosaic_associations(**kwargs):
    """
    Create a dummy mosaic associations instance with valid values for
    mosaic associations attributes. Utilized by the model maker utilities.

    Returns
    -------
    roman_datamodels.stnode.MosaicAssociations
    """

    mosass = stnode.MosaicAssociations()
    mosass["pool_name"] = kwargs.get("pool_name", NOSTR)
    mosass["table_name"] = kwargs.get("table_name", NOSTR)

    return mosass


def mk_guidewindow_meta(**kwargs):
    """
    Create a dummy common metadata dictionary with valid values for attributes and add
    the additional guidewindow metadata

    Returns
    -------
    dict (defined by the common-1.0.0 schema with additional guidewindow metadata)
    """

    meta = mk_common_meta(**kwargs)

    meta["file_creation_time"] = kwargs.get("file_creation_time", time.Time("2020-01-01T20:00:00.0", format="isot", scale="utc"))
    meta["gw_start_time"] = kwargs.get("gw_start_time", time.Time("2020-01-01T00:00:00.0", format="isot", scale="utc"))
    meta["gw_end_time"] = kwargs.get("gw_end_time", time.Time("2020-01-01T10:00:00.0", format="isot", scale="utc"))
    meta["gw_function_start_time"] = kwargs.get(
        "gw_function_start_time", time.Time("2020-01-01T00:00:00.0", format="isot", scale="utc")
    )
    meta["gw_function_end_time"] = kwargs.get(
        "gw_function_end_time", time.Time("2020-01-01T00:00:00.0", format="isot", scale="utc")
    )
    meta["gw_frame_readout_time"] = kwargs.get("gw_frame_readout_time", NONUM)
    meta["pedestal_resultant_exp_time"] = kwargs.get("pedestal_resultant_exp_time", NONUM)
    meta["signal_resultant_exp_time"] = kwargs.get("signal_resultant_exp_time", NONUM)
    meta["gw_acq_number"] = kwargs.get("gw_acq_number", NONUM)
    meta["gw_science_file_source"] = kwargs.get("gw_science_file_source", NOSTR)
    meta["gw_mode"] = kwargs.get("gw_mode", "WIM-ACQ")
    meta["gw_window_xstart"] = kwargs.get("gw_window_xstart", NONUM)
    meta["gw_window_ystart"] = kwargs.get("gw_window_ystart", NONUM)
    meta["gw_window_xstop"] = kwargs.get("gw_window_xstop", meta["gw_window_xstart"] + 170)
    meta["gw_window_ystop"] = kwargs.get("gw_window_ystop", meta["gw_window_ystart"] + 24)
    meta["gw_window_xsize"] = kwargs.get("gw_window_xsize", 170)
    meta["gw_window_ysize"] = kwargs.get("gw_window_ysize", 24)

    meta["gw_function_start_time"] = kwargs.get(
        "gw_function_start_time", time.Time("2020-01-01T00:00:00.0", format="isot", scale="utc")
    )
    meta["gw_function_end_time"] = kwargs.get(
        "gw_function_end_time", time.Time("2020-01-01T00:00:00.0", format="isot", scale="utc")
    )
    meta["data_start"] = kwargs.get("data_start", NONUM)
    meta["data_end"] = kwargs.get("data_end", NONUM)
    meta["gw_acq_exec_stat"] = kwargs.get("gw_acq_exec_stat", "StatusRMTest619")

    return meta


def mk_msos_stack_meta(**kwargs):
    """
    Create a dummy common metadata dictionary with valid values for attributes and add
    the additional msos_stack metadata

    Returns
    -------
    dict (defined by the common-1.0.0 schema with additional guidewindow metadata)
    """

    meta = mk_common_meta(**kwargs)
    meta["image_list"] = kwargs.get("image_list", NOSTR)

    return meta


def mk_rcs(**kwargs):
    """
    Create a dummy Relative Calibration System instance with valid values for attributes
    required by the schema. Utilized by the model maker utilities below.

    Returns
    -------
    roman_datamodels.stnode.Rcs
    """
    rcs = stnode.Rcs()
    rcs["active"] = kwargs.get("active", False)
    rcs["electronics"] = kwargs.get("electronics", "A")
    rcs["bank"] = kwargs.get("bank", "1")
    rcs["led"] = kwargs.get("led", "1")
    rcs["counts"] = kwargs.get("counts", NONUM)

    return rcs


def mk_statistics(**kwargs):
    """
    Create a dummy Statistical instance with valid values for attributes
    required by the schema. Utilized by the model maker utilities below.

    Returns
    -------
    roman_datamodels.stnode.Statistics
    """
    stats = stnode.Statistics()
    stats["zodiacal_light"] = kwargs.get("zodiacal_light", NONUM)
    stats["image_median"] = kwargs.get("image_median", NONUM)
    stats["image_rms"] = kwargs.get("image_rms", NONUM)
    stats["good_pixel_fraction"] = kwargs.get("good_pixel_fraction", NONUM)

    return stats


def mk_ref_common(reftype_, **kwargs):
    """
    Create dummy metadata for reference file instances.

    Returns
    -------
    dict (follows reference_file/ref_common-1.0.0 schema)
    """
    meta = {}
    meta["telescope"] = kwargs.get("telescope", "ROMAN")
    meta["instrument"] = kwargs.get("instrument", {"name": "WFI", "detector": "WFI01", "optical_element": "F158"})
    meta["origin"] = kwargs.get("origin", "STSCI")
    meta["pedigree"] = kwargs.get("pedigree", "GROUND")
    meta["author"] = kwargs.get("author", "test system")
    meta["description"] = kwargs.get("description", "blah blah blah")
    meta["useafter"] = kwargs.get("useafter", time.Time("2020-01-01T00:00:00.0", format="isot", scale="utc"))
    meta["reftype"] = kwargs.get("reftype", reftype_)

    return meta


def _mk_ref_exposure(**kwargs):
    """
    Create the general exposure meta data
    """
    exposure = {}
    exposure["type"] = kwargs.get("type", "WFI_IMAGE")
    exposure["p_exptype"] = kwargs.get("p_exptype", "WFI_IMAGE|WFI_GRISM|WFI_PRISM|")

    return exposure


def _mk_ref_dark_exposure(**kwargs):
    """
    Create the dark exposure meta data
    """
    exposure = _mk_ref_exposure(**kwargs)
    exposure["ngroups"] = kwargs.get("ngroups", 6)
    exposure["nframes"] = kwargs.get("nframes", 8)
    exposure["groupgap"] = kwargs.get("groupgap", 0)
    exposure["ma_table_name"] = kwargs.get("ma_table_name", NOSTR)
    exposure["ma_table_number"] = kwargs.get("ma_table_number", NONUM)

    return exposure


def mk_ref_dark_meta(**kwargs):
    """
    Create dummy metadata for dark reference file instances.

    Returns
    -------
    dict (follows reference_file/ref_common-1.0.0 schema + dark reference file metadata)
    """
    meta = mk_ref_common("DARK", **kwargs)
    meta["exposure"] = _mk_ref_dark_exposure(**kwargs.get("exposure", {}))

    return meta


def mk_ref_epsf_meta(**kwargs):
    """
    Create dummy metadata for ePSF reference file instances.

    Returns
    -------
    dict (follows reference_file/ref_common-1.0.0 schema + ePSF reference file metadata)
    """
    meta = mk_ref_common("EPSF", **kwargs)
    meta["oversample"] = kwargs.get("oversample", NONUM)
    meta["effective_temperature"] = kwargs.get("effective_temperature", np.arange(1, 10).tolist())
    meta["defocus"] = kwargs.get("defocus", np.arange(1, 10).tolist())
    meta["pixel_x"] = kwargs.get("pixel_x", np.arange(1, 10, dtype=np.float32).tolist())
    meta["pixel_y"] = kwargs.get("pixel_y", np.arange(1, 10, dtype=np.float32).tolist())

    return meta


def mk_ref_distoriton_meta(**kwargs):
    """
    Create dummy metadata for distortion reference file instances.

    Returns
    -------
    dict (follows reference_file/ref_common-1.0.0 schema + distortion reference file metadata)
    """
    meta = mk_ref_common("DISTORTION", **kwargs)

    meta["input_units"] = kwargs.get("input_units", u.pixel)
    meta["output_units"] = kwargs.get("output_units", u.arcsec)

    return meta


def _mk_ref_photometry_meta(**kwargs):
    """
    Create the photometry meta data for pixelarea reference files
    """
    meta = {}
    meta["pixelarea_steradians"] = kwargs.get("pixelarea_steradians", float(NONUM) * u.sr)
    meta["pixelarea_arcsecsq"] = kwargs.get("pixelarea_arcsecsq", float(NONUM) * u.arcsec**2)

    return meta


def mk_ref_pixelarea_meta(**kwargs):
    """
    Create dummy metadata for pixelarea reference file instances.

    Returns
    -------
    dict (follows reference_file/ref_common-1.0.0 schema + pixelarea reference file metadata)
    """
    meta = mk_ref_common("AREA", **kwargs)
    meta["photometry"] = _mk_ref_photometry_meta(**kwargs.get("photometry", {}))

    return meta


def mk_ref_units_dn_meta(reftype_, **kwargs):
    """
    Create dummy metadata for reference file instances which specify DN as input/output units.

    Returns
    -------
    dict (follows reference_file/ref_common-1.0.0 schema + DN input/output metadata)
    """
    meta = mk_ref_common(reftype_, **kwargs)

    meta["input_units"] = kwargs.get("input_units", u.DN)
    meta["output_units"] = kwargs.get("output_units", u.DN)

    return meta


def mk_ref_readnoise_meta(**kwargs):
    """
    Create dummy metadata for readnoise reference file instances.

    Returns
    -------
    dict (follows reference_file/ref_common-1.0.0 schema + readnoise reference file metadata)
    """
    meta = mk_ref_common("READNOISE", **kwargs)
    meta["exposure"] = _mk_ref_exposure(**kwargs.get("exposure", {}))

    return meta


def mk_mosaic_basic(**kwargs):
    """
    Create a dummy mosaic basic instance with valid values for attributes
    required by the schema. Utilized by the model maker utilities.

    Returns
    -------
    roman_datamodels.stnode.MosaicBasic
    """

    mosbasic = stnode.MosaicBasic()
    mosbasic["time_first_mjd"] = kwargs.get("time_first_mjd", NONUM)
    mosbasic["time_last_mjd"] = kwargs.get("time_last_mjd", NONUM)
    mosbasic["time_mean_mjd"] = kwargs.get("time_mean_mjd", NONUM)
    mosbasic["max_exposure_time"] = kwargs.get("max_exposure_time", NONUM)
    mosbasic["mean_exposure_time"] = kwargs.get("mean_exposure_time", NONUM)
    mosbasic["visit"] = kwargs.get("visit", NONUM)
    mosbasic["segment"] = kwargs.get("segment", NONUM)
    mosbasic["pass"] = kwargs.get("pass", NONUM)
    mosbasic["program"] = kwargs.get("program", NONUM)
    mosbasic["survey"] = kwargs.get("survey", NOSTR)
    mosbasic["optical_element"] = kwargs.get("optical_element", "F158")
    mosbasic["instrument"] = kwargs.get("instrument", "WFI")
    mosbasic["location_name"] = kwargs.get("location_name", NOSTR)
    mosbasic["product_type"] = kwargs.get("product_type", NOSTR)

    return mosbasic


def mk_mosaic_wcsinfo(**kwargs):
    """
    Create a dummy mosaic WCS Info instance with valid values for attributes
    required by the schema. Utilized by the model maker utilities.

    Returns
    -------
    roman_datamodels.stnode.MosaicWcsinfo
    """

    moswcsi = stnode.MosaicWcsinfo()
    moswcsi["ra_ref"] = kwargs.get("ra_ref", NONUM)
    moswcsi["dec_ref"] = kwargs.get("dec_ref", NONUM)
    moswcsi["x_ref"] = kwargs.get("x_ref", NONUM)
    moswcsi["y_ref"] = kwargs.get("y_ref", NONUM)
    moswcsi["rotation_matrix"] = kwargs.get("rotation_matrix", [[NONUM, NONUM], [NONUM, NONUM]])
    moswcsi["pixel_scale"] = kwargs.get("pixel_scale", NONUM)
    moswcsi["pixel_scale_local"] = kwargs.get("pixel_scale_local", NONUM)
    moswcsi["pixel_shape"] = kwargs.get("pixel_shape", [NONUM, NONUM])
    moswcsi["ra_center"] = kwargs.get("ra_center", NONUM)
    moswcsi["dec_center"] = kwargs.get("dec_center", NONUM)
    moswcsi["ra_corn1"] = kwargs.get("ra_corn1", NONUM)
    moswcsi["dec_corn1"] = kwargs.get("dec_corn1", NONUM)
    moswcsi["ra_corn2"] = kwargs.get("ra_corn2", NONUM)
    moswcsi["dec_corn2"] = kwargs.get("dec_corn2", NONUM)
    moswcsi["ra_corn3"] = kwargs.get("ra_corn3", NONUM)
    moswcsi["dec_corn3"] = kwargs.get("dec_corn3", NONUM)
    moswcsi["ra_corn4"] = kwargs.get("ra_corn4", NONUM)
    moswcsi["dec_corn4"] = kwargs.get("dec_corn4", NONUM)
    moswcsi["orientat_local"] = kwargs.get("orientat_local", NONUM)
    moswcsi["orientat"] = kwargs.get("orientat", NONUM)
    moswcsi["projection"] = kwargs.get("projection", "TAN")
    moswcsi["s_region"] = kwargs.get("s_region", NOSTR)

    return moswcsi


def mk_individual_image_meta(**kwargs):
    """
    Create a dummy component image metadata storage instance for mosaics
    with valid values for attributes required by the schema.
    Utilized by the model maker utilities.

    Returns
    -------
    roman_datamodels.stnode.IndividualImageMeta
    """

    imm = stnode.IndividualImageMeta()

    table_dct = {"dummy": [NONUM]}

    imm["basic"] = kwargs.get("basic", QTable(table_dct))
    # imm["background"] = kwargs.get("background", QTable(table_dct))
    # imm["cal_logs"] = kwargs.get("cal_logs", QTable(table_dct))
    # imm["cal_step"] = kwargs.get("cal_step", QTable(table_dct))
    # imm["coordinates"] = kwargs.get("coordinates", QTable(table_dct))
    # imm["ephemeris"] = kwargs.get("ephemeris", QTable(table_dct))
    # imm["exposure"] = kwargs.get("exposure", QTable(table_dct))
    # imm["guide_star"] = kwargs.get("guide_star", QTable(table_dct))
    # imm["instrument"] = kwargs.get("instrument", QTable(table_dct))
    # imm["observation"] = kwargs.get("observation", QTable(table_dct))
    # imm["outlier_detection"] = kwargs.get("outlier_detection", QTable(table_dct))
    # imm["photometry"] = kwargs.get("photometry", QTable(table_dct))
    # imm["pointing"] = kwargs.get("pointing", QTable(table_dct))
    # imm["program"] = kwargs.get("program", QTable(table_dct))
    # imm["rcs"] = kwargs.get("rcs", QTable(table_dct))
    # imm["ref_file"] = kwargs.get("ref_file", QTable(table_dct))
    # imm["source_detection"] = kwargs.get("source_detection", QTable(table_dct))
    # imm["velocity_aberration"] = kwargs.get("velocity_aberration", QTable(table_dct))
    # imm["visit"] = kwargs.get("visit", QTable(table_dct))
    # imm["wcsinfo"] = kwargs.get("wcsinfo", QTable(table_dct))

    return imm


def mk_wcs():
    pixelshift = models.Shift(-500) & models.Shift(-500)
    pixelscale = models.Scale(0.1 / 3600.0) & models.Scale(0.1 / 3600.0)  # 0.1 arcsec/pixel
    tangent_projection = models.Pix2Sky_TAN()
    celestial_rotation = models.RotateNative2Celestial(30.0, 45.0, 180.0)

    det2sky = pixelshift | pixelscale | tangent_projection | celestial_rotation

    detector_frame = coordinate_frames.Frame2D(name="detector", axes_names=("x", "y"), unit=(u.pix, u.pix))
    sky_frame = coordinate_frames.CelestialFrame(reference_frame=coordinates.ICRS(), name="icrs", unit=(u.deg, u.deg))
    return WCS(
        [
            (detector_frame, det2sky),
            (sky_frame, None),
        ]
    )


def mk_mosaic_catalog_meta(**kwargs):
    """
    Create a dummy metadata dictionary with valid values for mosaic catalog.

    Returns
    -------
    dict (defined by the wfi_mosaic-1.0.0 schema)
    """

    meta = mk_basic_meta(**kwargs)
    meta["basic"] = mk_mosaic_basic(**kwargs.get("basic", {}))
    meta["photometry"] = mk_photometry(**kwargs.get("photometry", {}))
    meta["program"] = mk_program(**kwargs.get("program", {}))

    return meta


def mk_catalog_meta(**kwargs):
    """
    Create a dummy metadata dictionary with valid values for
    source catalog from Level 2 data.

    Returns
    -------
    dict (defined by the wfi_mosaic-1.0.0 schema)
    """

    meta = mk_basic_meta(**kwargs)
    meta["program"] = mk_program(**kwargs.get("program", {}))
    meta["photometry"] = mk_photometry(**kwargs.get("photometry", {}))
    meta["visit"] = mk_visit(**kwargs.get("visit", {}))
    meta["optical_element"] = kwargs.get("optical_element", "F158")
    meta["exposure"] = mk_exposure(**kwargs.get("exposure", {}))

    return meta
