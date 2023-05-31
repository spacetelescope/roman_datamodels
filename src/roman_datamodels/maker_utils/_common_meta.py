from astropy import time

from roman_datamodels import stnode
from roman_datamodels.random_utils import generate_positive_int

from ._base import NONUM, NOSTR
from ._basic_meta import mk_basic_meta


def mk_exposure():
    """
    Create a dummy Exposure instance with valid values for attributes
    required by the schema. Utilized by the model maker utilities below.

    Returns
    -------
    roman_datamodels.stnode.Exposure
    """
    exp = stnode.Exposure()
    exp["id"] = NONUM
    exp["type"] = "WFI_IMAGE"
    exp["start_time"] = time.Time("2020-01-01T00:00:00.0", format="isot", scale="utc")
    exp["mid_time"] = time.Time("2020-01-01T00:00:00.0", format="isot", scale="utc")
    exp["end_time"] = time.Time("2020-01-01T00:00:00.0", format="isot", scale="utc")
    exp["start_time_mjd"] = NONUM
    exp["mid_time_mjd"] = NONUM
    exp["end_time_mjd"] = NONUM
    exp["start_time_tdb"] = NONUM
    exp["mid_time_tdb"] = NONUM
    exp["end_time_tdb"] = NONUM
    exp["ngroups"] = 6
    exp["nframes"] = 8
    exp["data_problem"] = False
    exp["sca_number"] = NONUM
    exp["gain_factor"] = NONUM
    exp["integration_time"] = NONUM
    exp["elapsed_exposure_time"] = NONUM
    exp["frame_divisor"] = NONUM
    exp["groupgap"] = 0
    exp["frame_time"] = NONUM
    exp["group_time"] = NONUM
    exp["exposure_time"] = NONUM
    exp["effective_exposure_time"] = NONUM
    exp["duration"] = NONUM
    exp["ma_table_name"] = NOSTR
    exp["ma_table_number"] = NONUM
    exp["level0_compressed"] = True
    exp["read_pattern"] = [[1], [2, 3], [4], [5, 6, 7, 8], [9, 10], [11]]

    return exp


def mk_wfi_mode():
    """
    Create a dummy WFI mode instance with valid values for attributes
    required by the schema. Utilized by the model maker utilities below.

    Returns
    -------
    roman_datamodels.stnode.WfiMode
    """
    mode = stnode.WfiMode()
    mode["name"] = "WFI"
    mode["detector"] = "WFI01"
    mode["optical_element"] = "F062"

    return mode


def mk_program():
    """
    Create a dummy Program instance with valid values for attributes
    required by the schema. Utilized by the model maker utilities below.

    Returns
    -------
    roman_datamodels.stnode.Program
    """
    prog = stnode.Program()
    prog["title"] = NOSTR
    prog["pi_name"] = NOSTR
    prog["category"] = NOSTR
    prog["subcategory"] = NOSTR
    prog["science_category"] = NOSTR
    prog["continuation_id"] = NONUM

    return prog


def mk_observation():
    """
    Create a dummy Observation instance with valid values for attributes
    required by the schema. Utilized by the model maker utilities below.

    Returns
    -------
    roman_datamodels.stnode.Observation
    """
    obs = stnode.Observation()
    obs["obs_id"] = NOSTR
    obs["visit_id"] = NOSTR
    obs["program"] = str(NONUM)
    obs["execution_plan"] = NONUM
    obs["pass"] = NONUM
    obs["segment"] = NONUM
    obs["observation"] = NONUM
    obs["visit"] = NONUM
    obs["visit_file_group"] = NONUM
    obs["visit_file_sequence"] = NONUM
    obs["visit_file_activity"] = NOSTR
    obs["exposure"] = NONUM
    obs["template"] = NOSTR
    obs["observation_label"] = NOSTR
    obs["survey"] = "N/A"

    return obs


def mk_ephemeris():
    """
    Create a dummy Ephemeris instance with valid values for attributes
    required by the schema. Utilized by the model maker utilities below.

    Returns
    -------
    roman_datamodels.stnode.Ephemeris
    """
    ephem = stnode.Ephemeris()
    ephem["earth_angle"] = NONUM
    ephem["moon_angle"] = NONUM
    ephem["ephemeris_reference_frame"] = NOSTR
    ephem["sun_angle"] = NONUM
    ephem["type"] = "DEFINITIVE"
    ephem["time"] = NONUM
    ephem["spatial_x"] = NONUM
    ephem["spatial_y"] = NONUM
    ephem["spatial_z"] = NONUM
    ephem["velocity_x"] = NONUM
    ephem["velocity_y"] = NONUM
    ephem["velocity_z"] = NONUM

    return ephem


def mk_visit():
    """
    Create a dummy Visit instance with valid values for attributes
    required by the schema. Utilized by the model maker utilities below.

    Returns
    -------
    roman_datamodels.stnode.Visit
    """
    visit = stnode.Visit()
    visit["engineering_quality"] = "OK"  # qqqq
    visit["pointing_engdb_quality"] = "CALCULATED"  # qqqq
    visit["type"] = NOSTR
    visit["start_time"] = time.Time("2020-01-01T00:00:00.0", format="isot", scale="utc")
    visit["end_time"] = time.Time("2020-01-01T00:00:00.0", format="isot", scale="utc")
    visit["status"] = NOSTR
    visit["total_exposures"] = NONUM
    visit["internal_target"] = False
    visit["target_of_opportunity"] = False

    return visit


def mk_source_detection():
    """
    Create a dummy Source Detection instance with valid values for attributes
    required by the schema. Utilized by the model maker utilities below

    Returns
    -------
    roman_datamodels.stnode.SourceDetection
    """
    sd = stnode.SourceDetection()
    sd["tweakreg_catalog_name"] = "filename_tweakreg_catalog.asdf"

    return sd


def mk_coordinates():
    """
    Create a dummy Coordinates instance with valid values for attributes
    required by the schema. Utilized by the model maker utilities below.

    Returns
    -------
    roman_datamodels.stnode.Coordinates
    """
    coord = stnode.Coordinates()
    coord["reference_frame"] = "ICRS"

    return coord


def mk_aperture():
    """
    Create a dummy Aperture instance with valid values for attributes
    required by the schema. Utilized by the model maker utilities below.

    Returns
    -------
    roman_datamodels.stnode.Aperture
    """
    aper = stnode.Aperture()
    aper_number = generate_positive_int(17) + 1
    aper["name"] = f"WFI_{aper_number:02d}_FULL"
    aper["position_angle"] = 30.0

    return aper


def mk_pointing():
    """
    Create a dummy Pointing instance with valid values for attributes
    required by the schema. Utilized by the model maker utilities below.

    Returns
    -------
    roman_datamodels.stnode.Pointing
    """
    point = stnode.Pointing()
    point["ra_v1"] = NONUM
    point["dec_v1"] = NONUM
    point["pa_v3"] = NONUM

    return point


def mk_target():
    """
    Create a dummy Target instance with valid values for attributes
    required by the schema. Utilized by the model maker utilities below.

    Returns
    -------
    roman_datamodels.stnode.Target
    """
    targ = stnode.Target()
    targ["proposer_name"] = NOSTR
    targ["catalog_name"] = NOSTR
    targ["type"] = "FIXED"
    targ["ra"] = NONUM
    targ["dec"] = NONUM
    targ["ra_uncertainty"] = NONUM
    targ["dec_uncertainty"] = NONUM
    targ["proper_motion_ra"] = NONUM
    targ["proper_motion_dec"] = NONUM
    targ["proper_motion_epoch"] = NOSTR
    targ["proposer_ra"] = NONUM
    targ["proposer_dec"] = NONUM
    targ["source_type"] = "POINT"

    return targ


def mk_velocity_aberration():
    """
    Create a dummy Velocity Aberration instance with valid values for attributes
    required by the schema. Utilized by the model maker utilities below.

    Returns
    -------
    roman_datamodels.stnode.VelocityAberration
    """
    vab = stnode.VelocityAberration()
    vab["ra_offset"] = NONUM
    vab["dec_offset"] = NONUM
    vab["scale_factor"] = NONUM

    return vab


def mk_wcsinfo():
    """
    Create a dummy WCS Info instance with valid values for attributes
    required by the schema. Utilized by the model maker utilities below.

    Returns
    -------
    roman_datamodels.stnode.Wcsinfo
    """
    wcsi = stnode.Wcsinfo()
    wcsi["v2_ref"] = NONUM
    wcsi["v3_ref"] = NONUM
    wcsi["vparity"] = NONUM
    wcsi["v3yangle"] = NONUM
    wcsi["ra_ref"] = NONUM
    wcsi["dec_ref"] = NONUM
    wcsi["roll_ref"] = NONUM
    wcsi["s_region"] = NOSTR

    return wcsi


def mk_cal_step():
    """
    Create a dummy Cal Step instance with valid values for attributes
    required by the schema. Utilized by the model maker utilities below.

    Returns
    -------
    roman_datamodels.stnode.CalStep
    """
    calstep = stnode.CalStep()
    calstep["flat_field"] = "INCOMPLETE"
    calstep["dq_init"] = "INCOMPLETE"
    calstep["assign_wcs"] = "INCOMPLETE"
    calstep["dark"] = "INCOMPLETE"
    calstep["jump"] = "INCOMPLETE"
    calstep["linearity"] = "INCOMPLETE"
    calstep["photom"] = "INCOMPLETE"
    calstep["source_detection"] = "INCOMPLETE"
    calstep["ramp_fit"] = "INCOMPLETE"
    calstep["saturation"] = "INCOMPLETE"

    return calstep


def mk_guidestar():
    """
    Create a dummy Guide Star instance with valid values for attributes
    required by the schema. Utilized by the model maker utilities below.

    Returns
    -------
    roman_datamodels.stnode.Guidestar
    """
    guide = stnode.Guidestar()
    guide["gw_id"] = NOSTR
    guide["gs_ra"] = NONUM
    guide["gs_dec"] = NONUM
    guide["gs_ura"] = NONUM
    guide["gs_udec"] = NONUM
    guide["gs_mag"] = NONUM
    guide["gs_umag"] = NONUM
    guide["gw_fgs_mode"] = "WSM-ACQ-2"
    guide["gs_id"] = NOSTR
    guide["gs_catalog_version"] = NOSTR
    guide["data_start"] = NONUM
    guide["data_end"] = NONUM
    guide["gs_ctd_x"] = NONUM
    guide["gs_ctd_y"] = NONUM
    guide["gs_ctd_ux"] = NONUM
    guide["gs_ctd_uy"] = NONUM
    guide["gs_epoch"] = NOSTR
    guide["gs_mura"] = NONUM
    guide["gs_mudec"] = NONUM
    guide["gs_para"] = NONUM
    guide["gs_pattern_error"] = NONUM
    guide["gw_window_xstart"] = NONUM
    guide["gw_window_ystart"] = NONUM
    guide["gw_window_xstop"] = guide["gw_window_xstart"] + 170
    guide["gw_window_ystop"] = guide["gw_window_ystart"] + 24
    guide["gw_window_xsize"] = 170
    guide["gw_window_ysize"] = 24

    return guide


def mk_ref_file():
    """
    Create a dummy RefFile instance with valid values for attributes
    required by the schema. Utilized by the model maker utilities below.

    Returns
    -------
    roman_datamodels.stnode.RefFile
    """
    ref_file = stnode.RefFile()
    ref_file["dark"] = "N/A"
    ref_file["distortion"] = "N/A"
    ref_file["flat"] = "N/A"
    ref_file["gain"] = "N/A"
    ref_file["linearity"] = "N/A"
    ref_file["mask"] = "N/A"
    ref_file["readnoise"] = "N/A"
    ref_file["saturation"] = "N/A"
    ref_file["photom"] = "N/A"
    ref_file["crds"] = {"sw_version": "12.3.1", "context_used": "roman_0815.pmap"}

    return ref_file


def mk_common_meta():
    """
    Create a dummy common metadata dictionary with valid values for attributes

    Returns
    -------
    dict (defined by the common-1.0.0 schema)
    """
    meta = mk_basic_meta()
    meta["aperture"] = mk_aperture()
    meta["cal_step"] = mk_cal_step()
    meta["coordinates"] = mk_coordinates()
    meta["ephemeris"] = mk_ephemeris()
    meta["exposure"] = mk_exposure()
    meta["guidestar"] = mk_guidestar()
    meta["instrument"] = mk_wfi_mode()
    meta["observation"] = mk_observation()
    meta["pointing"] = mk_pointing()
    meta["program"] = mk_program()
    meta["ref_file"] = mk_ref_file()
    meta["target"] = mk_target()
    meta["velocity_aberration"] = mk_velocity_aberration()
    meta["visit"] = mk_visit()
    meta["wcsinfo"] = mk_wcsinfo()

    return meta
