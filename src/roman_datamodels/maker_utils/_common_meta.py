from astropy import time
from astropy import units as u

from roman_datamodels import stnode

from ._base import NONUM, NOSTR
from ._basic_meta import mk_basic_meta
from ._tagged_nodes import mk_photometry, mk_resample


def mk_exposure(**kwargs):
    """
    Create a dummy Exposure instance with valid values for attributes
    required by the schema. Utilized by the model maker utilities below.

    Returns
    -------
    roman_datamodels.stnode.Exposure
    """
    exp = stnode.Exposure()
    exp["id"] = kwargs.get("id", NONUM)
    exp["type"] = kwargs.get("type", "WFI_IMAGE")
    exp["start_time"] = kwargs.get("start_time", time.Time("2020-01-01T00:00:00.0", format="isot", scale="utc"))
    exp["mid_time"] = kwargs.get("mid_time", time.Time("2020-01-01T00:00:00.0", format="isot", scale="utc"))
    exp["end_time"] = kwargs.get("end_time", time.Time("2020-01-01T00:00:00.0", format="isot", scale="utc"))
    exp["start_time_mjd"] = kwargs.get("start_time_mjd", NONUM)
    exp["mid_time_mjd"] = kwargs.get("mid_time_mjd", NONUM)
    exp["end_time_mjd"] = kwargs.get("end_time_mjd", NONUM)
    exp["start_time_tdb"] = kwargs.get("start_time_tdb", NONUM)
    exp["mid_time_tdb"] = kwargs.get("mid_time_tdb", NONUM)
    exp["end_time_tdb"] = kwargs.get("end_time_tdb", NONUM)
    exp["ngroups"] = kwargs.get("ngroups", 6)
    exp["nframes"] = kwargs.get("nframes", 8)
    exp["data_problem"] = kwargs.get("data_problem", False)
    exp["sca_number"] = kwargs.get("sca_number", NONUM)
    exp["gain_factor"] = kwargs.get("gain_factor", NONUM)
    exp["integration_time"] = kwargs.get("integration_time", NONUM)
    exp["elapsed_exposure_time"] = kwargs.get("elapsed_exposure_time", NONUM)
    exp["frame_divisor"] = kwargs.get("frame_divisor", NONUM)
    exp["groupgap"] = kwargs.get("groupgap", 0)
    exp["frame_time"] = kwargs.get("frame_time", NONUM)
    exp["group_time"] = kwargs.get("group_time", NONUM)
    exp["exposure_time"] = kwargs.get("exposure_time", NONUM)
    exp["effective_exposure_time"] = kwargs.get("effective_exposure_time", NONUM)
    exp["duration"] = kwargs.get("duration", NONUM)
    exp["ma_table_name"] = kwargs.get("ma_table_name", NOSTR)
    exp["ma_table_number"] = kwargs.get("ma_table_number", NONUM)
    exp["level0_compressed"] = kwargs.get("level0_compressed", True)
    exp["read_pattern"] = kwargs.get("read_pattern", [[1], [2, 3], [4], [5, 6, 7, 8], [9, 10], [11]])

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
    prog["pi_name"] = kwargs.get("pi_name", NOSTR)
    prog["category"] = kwargs.get("category", NOSTR)
    prog["subcategory"] = kwargs.get("subcategory", NOSTR)
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
    obs["obs_id"] = kwargs.get("obs_id", NOSTR)
    obs["visit_id"] = kwargs.get("visit_id", NOSTR)
    obs["program"] = kwargs.get("program", str(NONUM))
    obs["execution_plan"] = kwargs.get("execution_plan", NONUM)
    obs["pass"] = kwargs.get("pass", NONUM)
    obs["segment"] = kwargs.get("segment", NONUM)
    obs["observation"] = kwargs.get("observation", NONUM)
    obs["visit"] = kwargs.get("visit", NONUM)
    obs["visit_file_group"] = kwargs.get("visit_file_group", NONUM)
    obs["visit_file_sequence"] = kwargs.get("visit_file_sequence", NONUM)
    obs["visit_file_activity"] = kwargs.get("visit_file_activity", NOSTR)
    obs["exposure"] = kwargs.get("exposure", NONUM)
    obs["template"] = kwargs.get("template", NOSTR)
    obs["observation_label"] = kwargs.get("observation_label", NOSTR)
    obs["survey"] = kwargs.get("survey", "N/A")

    return obs


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
    visit["engineering_quality"] = kwargs.get("engineering_quality", "OK")
    visit["pointing_engdb_quality"] = kwargs.get("pointing_engdb_quality", "CALCULATED")
    visit["type"] = kwargs.get("type", NOSTR)
    visit["start_time"] = kwargs.get("start_time", time.Time("2020-01-01T00:00:00.0", format="isot", scale="utc"))
    visit["end_time"] = kwargs.get("end_time", time.Time("2020-01-01T00:00:00.0", format="isot", scale="utc"))
    visit["status"] = kwargs.get("status", NOSTR)
    visit["total_exposures"] = kwargs.get("total_exposures", NONUM)
    visit["internal_target"] = kwargs.get("internal_target", False)
    visit["target_of_opportunity"] = kwargs.get("target_of_opportunity", False)

    return visit


def mk_source_detection(**kwargs):
    """
    Create a dummy Source Detection instance with valid values for attributes
    required by the schema. Utilized by the model maker utilities below

    Returns
    -------
    roman_datamodels.stnode.SourceDetection
    """
    sd = stnode.SourceDetection()
    sd["tweakreg_catalog_name"] = kwargs.get("tweakreg_catalog_name", "filename_tweakreg_catalog.asdf")

    return sd


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


def mk_aperture(**kwargs):
    """
    Create a dummy Aperture instance with valid values for attributes
    required by the schema. Utilized by the model maker utilities below.

    Returns
    -------
    roman_datamodels.stnode.Aperture
    """
    aper = stnode.Aperture()
    aper["name"] = kwargs.get("name", f"WFI_{5 + 1:02d}_FULL")
    aper["position_angle"] = kwargs.get("position_angle", 30.0)

    return aper


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

    return point


def mk_target(**kwargs):
    """
    Create a dummy Target instance with valid values for attributes
    required by the schema. Utilized by the model maker utilities below.

    Returns
    -------
    roman_datamodels.stnode.Target
    """
    targ = stnode.Target()
    targ["proposer_name"] = kwargs.get("proposer_name", NOSTR)
    targ["catalog_name"] = kwargs.get("catalog_name", NOSTR)
    targ["type"] = kwargs.get("type", "FIXED")
    targ["ra"] = kwargs.get("ra", NONUM)
    targ["dec"] = kwargs.get("dec", NONUM)
    targ["ra_uncertainty"] = kwargs.get("ra_uncertainty", NONUM)
    targ["dec_uncertainty"] = kwargs.get("dec_uncertainty", NONUM)
    targ["proper_motion_ra"] = kwargs.get("proper_motion_ra", NONUM)
    targ["proper_motion_dec"] = kwargs.get("proper_motion_dec", NONUM)
    targ["proper_motion_epoch"] = kwargs.get("proper_motion_epoch", NOSTR)
    targ["proposer_ra"] = kwargs.get("proposer_ra", NONUM)
    targ["proposer_dec"] = kwargs.get("proposer_dec", NONUM)
    targ["source_type"] = kwargs.get("source_type", "POINT")

    return targ


def mk_velocity_aberration(**kwargs):
    """
    Create a dummy Velocity Aberration instance with valid values for attributes
    required by the schema. Utilized by the model maker utilities below.

    Returns
    -------
    roman_datamodels.stnode.VelocityAberration
    """
    vab = stnode.VelocityAberration()
    vab["ra_offset"] = kwargs.get("ra_offset", NONUM)
    vab["dec_offset"] = kwargs.get("dec_offset", NONUM)
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
    wcsi["v2_ref"] = kwargs.get("v2_ref", NONUM)
    wcsi["v3_ref"] = kwargs.get("v3_ref", NONUM)
    wcsi["vparity"] = kwargs.get("vparity", NONUM)
    wcsi["v3yangle"] = kwargs.get("v3yangle", NONUM)
    wcsi["ra_ref"] = kwargs.get("ra_ref", NONUM)
    wcsi["dec_ref"] = kwargs.get("dec_ref", NONUM)
    wcsi["roll_ref"] = kwargs.get("roll_ref", NONUM)
    wcsi["s_region"] = kwargs.get("s_region", NOSTR)

    return wcsi


def mk_cal_step(**kwargs):
    """
    Create a dummy Cal Step instance with valid values for attributes
    required by the schema. Utilized by the model maker utilities below.

    Returns
    -------
    roman_datamodels.stnode.CalStep
    """
    calstep = stnode.CalStep()
    calstep["assign_wcs"] = kwargs.get("assign_wcs", "INCOMPLETE")
    calstep["dark"] = kwargs.get("dark", "INCOMPLETE")
    calstep["dq_init"] = kwargs.get("dq_init", "INCOMPLETE")
    calstep["flat_field"] = kwargs.get("flat_field", "INCOMPLETE")
    calstep["jump"] = kwargs.get("jump", "INCOMPLETE")
    calstep["linearity"] = kwargs.get("linearity", "INCOMPLETE")
    calstep["photom"] = kwargs.get("photom", "INCOMPLETE")
    calstep["source_detection"] = kwargs.get("source_detection", "INCOMPLETE")
    calstep["outlier_detection"] = kwargs.get("outlier_detection", "INCOMPLETE")
    calstep["ramp_fit"] = kwargs.get("ramp_fit", "INCOMPLETE")
    calstep["refpix"] = kwargs.get("refpix", "INCOMPLETE")
    calstep["saturation"] = kwargs.get("saturation", "INCOMPLETE")
    calstep["skymatch"] = kwargs.get("skymatch", "INCOMPLETE")
    calstep["tweakreg"] = kwargs.get("tweakreg", "INCOMPLETE")
    calstep["resample"] = kwargs.get("resample", "INCOMPLETE")

    return calstep


def mk_guidestar(**kwargs):
    """
    Create a dummy Guide Star instance with valid values for attributes
    required by the schema. Utilized by the model maker utilities below.

    Returns
    -------
    roman_datamodels.stnode.Guidestar
    """
    guide = stnode.Guidestar()
    guide["gw_id"] = kwargs.get("gw_id", NOSTR)
    guide["gs_ra"] = kwargs.get("gs_ra", NONUM)
    guide["gs_dec"] = kwargs.get("gs_dec", NONUM)
    guide["gs_ura"] = kwargs.get("gs_ura", NONUM)
    guide["gs_udec"] = kwargs.get("gs_udec", NONUM)
    guide["gs_mag"] = kwargs.get("gs_mag", NONUM)
    guide["gs_umag"] = kwargs.get("gs_umag", NONUM)
    guide["gw_fgs_mode"] = kwargs.get("gw_fgs_mode", "WSM-ACQ-2")
    guide["gs_id"] = kwargs.get("gs_id", NOSTR)
    guide["gs_catalog_version"] = kwargs.get("gs_catalog_version", NOSTR)
    guide["data_start"] = kwargs.get("data_start", NONUM)
    guide["data_end"] = kwargs.get("data_end", NONUM)
    guide["gs_ctd_x"] = kwargs.get("gs_ctd_x", NONUM)
    guide["gs_ctd_y"] = kwargs.get("gs_ctd_y", NONUM)
    guide["gs_ctd_ux"] = kwargs.get("gs_ctd_ux", NONUM)
    guide["gs_ctd_uy"] = kwargs.get("gs_ctd_uy", NONUM)
    guide["gs_epoch"] = kwargs.get("gs_epoch", NOSTR)
    guide["gs_mura"] = kwargs.get("gs_mura", NONUM)
    guide["gs_mudec"] = kwargs.get("gs_mudec", NONUM)
    guide["gs_para"] = kwargs.get("gs_para", NONUM)
    guide["gs_pattern_error"] = kwargs.get("gs_pattern_error", NONUM)
    guide["gw_window_xstart"] = kwargs.get("gw_window_xstart", NONUM)
    guide["gw_window_ystart"] = kwargs.get("gw_window_ystart", NONUM)
    guide["gw_window_xstop"] = kwargs.get("gw_window_xstop", guide["gw_window_xstart"] + 170)
    guide["gw_window_ystop"] = kwargs.get("gw_window_ystop", guide["gw_window_ystart"] + 24)
    guide["gw_window_xsize"] = kwargs.get("gw_window_xsize", 170)
    guide["gw_window_ysize"] = kwargs.get("gw_window_ysize", 24)

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
    ref_file["saturation"] = kwargs.get("saturation", "N/A")
    ref_file["photom"] = kwargs.get("photom", "N/A")
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
    meta["aperture"] = mk_aperture(**kwargs.get("aperture", {}))
    meta["cal_step"] = mk_cal_step(**kwargs.get("cal_step", {}))
    meta["coordinates"] = mk_coordinates(**kwargs.get("coordinates", {}))
    meta["ephemeris"] = mk_ephemeris(**kwargs.get("ephemeris", {}))
    meta["exposure"] = mk_exposure(**kwargs.get("exposure", {}))
    meta["guidestar"] = mk_guidestar(**kwargs.get("guidestar", {}))
    meta["instrument"] = mk_wfi_mode(**kwargs.get("instrument", {}))
    meta["observation"] = mk_observation(**kwargs.get("observation", {}))
    meta["pointing"] = mk_pointing(**kwargs.get("pointing", {}))
    meta["program"] = mk_program(**kwargs.get("program", {}))
    meta["ref_file"] = mk_ref_file(**kwargs.get("ref_file", {}))
    meta["target"] = mk_target(**kwargs.get("target", {}))
    meta["velocity_aberration"] = mk_velocity_aberration(**kwargs.get("velocity_aberration", {}))
    meta["visit"] = mk_visit(**kwargs.get("visit", {}))
    meta["wcsinfo"] = mk_wcsinfo(**kwargs.get("wcsinfo", {}))

    return meta


def mk_photometry_meta(**kwargs):
    """
    Create a dummy common metadata dictionary with valid values for attributes and add
    the additional photometry metadata

    Returns
    -------
    dict (defined by the common-1.0.0 schema with additional photometry metadata)
    """

    meta = mk_common_meta(**kwargs)
    meta["photometry"] = mk_photometry(**kwargs.get("photometry", {}))

    return meta


def mk_resample_meta(**kwargs):
    """
    Create a dummy common metadata dictionary with valid values for attributes and add
    the additional photometry AND resample metadata

    Returns
    -------
    dict (defined by the common-1.0.0 schema with additional photometry and resample metadata)
    """

    meta = mk_photometry_meta(**kwargs)
    meta["resample"] = mk_resample(**kwargs.get("resample", {}))

    return meta


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
