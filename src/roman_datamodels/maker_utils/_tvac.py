import warnings

import astropy.units as u
import numpy as np
from astropy import time

from roman_datamodels import stnode

from ._base import NONUM, NOSTR, save_node
from ._tvac_basic_meta import mk_tvac_basic_meta


def mk_tvac_groundtest(**kwargs):
    """
    Create a dummy GroundGroundtest instance with valid values for attributes
    required by the schema. Utilized by the model maker utilities below.

    This adds the tvac fields

    Returns
    -------
    roman_datamodels.stnode.TvacGroundtest
    """

    ground = stnode.TvacGroundtest()

    ground["activity_number"] = kwargs.get("activity_number", NONUM)
    ground["led_bank1_band_number_on"] = kwargs.get("led_bank1_band_number_on", [NONUM])
    ground["led_bank1_approx_wlen"] = kwargs.get(
        "led_bank1_approx_wlen", u.Quantity(np.zeros(6, dtype=np.float64), unit=u.nm, dtype=np.float64)
    )
    ground["led_bank2_approx_wlen"] = kwargs.get(
        "led_bank2_approx_wlen", u.Quantity(np.zeros(6, dtype=np.float64), unit=u.nm, dtype=np.float64)
    )
    ground["srcs_pd_voltage"] = kwargs.get("srcs_pd_voltage", NONUM)
    ground["srcs_led_flux"] = kwargs.get("srcs_led_flux", NONUM)
    ground["wfi_mce_srcs_bank1_led_i"] = kwargs.get(
        "wfi_mce_srcs_bank1_led_i", u.Quantity(np.zeros(6, dtype=np.uint32), unit=u.A, dtype=np.uint32)
    )
    ground["wfi_mce_srcs_bank1_led_range"] = kwargs.get("wfi_mce_srcs_bank1_led_range", NOSTR)
    ground["wfi_mce_srcs_bank2_led_i"] = kwargs.get(
        "wfi_mce_srcs_bank2_led_i", u.Quantity(np.zeros(6, dtype=np.uint32), unit=u.A, dtype=np.uint32)
    )
    ground["wfi_mce_srcs_bank2_led_range"] = kwargs.get("wfi_mce_srcs_bank2_led_range", NOSTR)
    ground["srcs_led_current"] = kwargs.get("srcs_led_current", NONUM)
    ground["wfi_opt_targettype"] = kwargs.get("wfi_opt_targettype", "FLAT-sRCS")
    ground["analysis_tag"] = kwargs.get("analysis_tag", NOSTR)
    ground["gsorc_pose_mode"] = kwargs.get("gsorc_pose_mode", NOSTR)
    ground["gsorc_pose_target"] = kwargs.get("gsorc_pose_target", NOSTR)
    ground["gsorc_sds_active_atten"] = kwargs.get("gsorc_sds_active_atten", NONUM)
    ground["gsorc_sds_lltfir_wave"] = kwargs.get("gsorc_sds_lltfir_wave", NONUM)
    ground["gsorc_sds_sorc_on"] = kwargs.get("gsorc_sds_sorc_on", False)
    ground["gsorc_sds_sorc_wlen"] = kwargs.get("gsorc_sds_sorc_wlen", NONUM)
    ground["gsorc_sds_active_source"] = kwargs.get("gsorc_sds_active_source", NOSTR)
    ground["gsorc_sds_dq_pulse"] = kwargs.get("gsorc_sds_dq_pulse", "pulse")
    ground["gsorc_sds_daq_pw"] = kwargs.get("gsorc_sds_daq_pw", u.Quantity(NONUM, u.ms))
    ground["gsorc_heater1_setpt"] = kwargs.get("gsorc_heater1_setpt", NONUM)
    ground["wfi_otp_wfi_ewa"] = kwargs.get("wfi_otp_wfi_ewa", NOSTR)
    ground["sca_temp"] = kwargs.get("sca_temp", u.Quantity(NONUM, u.K))
    ground["mpa_temp"] = kwargs.get("mpa_temp", u.Quantity(NONUM, u.K))
    ground["ewa_temp"] = kwargs.get("ewa_temp", u.Quantity(NONUM, u.K))
    ground["ewta_outer_heater_temp"] = kwargs.get("ewta_outer_heater_temp", u.Quantity(NONUM, u.K))
    ground["ewta_inner_heater_temp"] = kwargs.get("ewta_inner_heater_temp", u.Quantity(NONUM, u.K))
    ground["coba_temp_near_ewta"] = kwargs.get("coba_temp_near_ewta", u.Quantity(NONUM, u.K))
    ground["scea_temp"] = kwargs.get("scea_temp", u.Quantity(NONUM, u.K))
    ground["wfi_sce_1_vbiasgate_v"] = kwargs.get("wfi_sce_1_vbiasgate_v", u.Quantity(NONUM, u.V))
    ground["wfi_sce_1_vbiaspwr_i"] = kwargs.get("wfi_sce_1_vbiaspwr_i", u.Quantity(NONUM, u.A))
    ground["wfi_sce_1_vbiaspwr_v"] = kwargs.get("wfi_sce_1_vbiaspwr_v", u.Quantity(NONUM, u.V))
    ground["wfi_sce_1_vreset_v"] = kwargs.get("wfi_sce_1_vreset_v", u.Quantity(NONUM, u.V))
    ground["wfi_sce_1_vreset_i"] = kwargs.get("wfi_sce_1_vreset_i", u.Quantity(NONUM, u.A))
    ground["wfi_mcu_a_offs_csense_fpssen"] = kwargs.get("wfi_mcu_a_offs_csense_fpssen", u.Quantity(NONUM, u.K))

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
    ground["frames_temp"] = kwargs.get("frames_temp", np.zeros(6, dtype=np.float64))
    ground["ota_temp"] = kwargs.get("ota_temp", NONUM)
    ground["rcs_on"] = kwargs.get("rcs_on", False)
    ground["readout_col_num"] = kwargs.get("readout_col_num", NONUM)
    ground["detector_pixel_size"] = kwargs.get(
        "detector_pixel_size", u.Quantity(np.zeros(6, dtype=np.float64), unit=u.cm, dtype=np.float64)
    )
    ground["sensor_error"] = kwargs.get("sensor_error", np.zeros(6, dtype=np.float64))

    return ground


def mk_tvac_common_meta(**kwargs):
    """
    Create a dummy common metadata dictionary with valid values for attributes

    Returns
    -------
    dict (defined by the ground_common-1.0.0 schema)
    """
    # prevent circular import
    from ._tvac_common_meta import (
        mk_tvac_cal_step,
        mk_tvac_exposure,
        mk_tvac_guidestar,
        mk_tvac_ref_file,
        mk_tvac_statistics,
        mk_tvac_wfi_mode,
    )

    meta = mk_tvac_basic_meta(**kwargs)
    meta["cal_step"] = mk_tvac_cal_step(**kwargs.get("cal_step", {}))
    meta["exposure"] = mk_tvac_exposure(**kwargs.get("exposure", {}))
    meta["guidestar"] = mk_tvac_guidestar(**kwargs.get("guidestar", {}))
    meta["instrument"] = mk_tvac_wfi_mode(**kwargs.get("instrument", {}))
    meta["ref_file"] = mk_tvac_ref_file(**kwargs.get("ref_file", {}))
    meta["statistics"] = mk_tvac_statistics(**kwargs.get("statistics", {}))
    meta["hdf5_meta"] = kwargs.get("hdf5_meta", {"test": NOSTR})
    meta["hdf5_telemetry"] = kwargs.get("hdf5_telemetry", NOSTR)
    meta["gw_meta"] = kwargs.get("gw_meta", {"test": NOSTR})

    return meta


def mk_tvac_meta(**kwargs):
    """
    Create a dummy tvac metadata dictionary with valid values for attributes

    Returns
    -------
    dict (defined by the tvac-1.0.0.meta schema)
    """

    meta = mk_tvac_common_meta(**kwargs)
    meta["groundtest"] = mk_tvac_groundtest(**kwargs.get("groundtest", {}))

    return meta


def mk_tvac(*, shape=(8, 4096, 4096), filepath=None, **kwargs):
    """
    Create a dummy Tvac instance (or file) with arrays and valid
    values for attributes required by the schema.

    Parameters
    ----------
    shape : tuple, int
        (optional, keyword-only) (z, y, x) Shape of data array. This includes a
        four-pixel border representing the reference pixels. Default is
            (8, 4096, 4096)
        (8 integrations, 4088 x 4088 represent the science pixels, with the
        additional being the border reference pixels).

    filepath : str
        (optional, keyword-only) File name and path to write model to.

    Returns
    -------
    roman_datamodels.stnode.Tvac
    """

    if len(shape) != 3:
        shape = (8, 4096, 4096)
        warnings.warn("Input shape must be 3D. Defaulting to (8, 4096, 4096)", UserWarning, stacklevel=2)

    tvac = stnode.Tvac()
    tvac["meta"] = mk_tvac_meta(**kwargs.get("meta", {}))

    n_groups = shape[0]

    tvac["data"] = kwargs.get("data", u.Quantity(np.zeros(shape, dtype=np.uint16), u.DN, dtype=np.uint16))

    # add amp 33 ref pix
    tvac["amp33"] = kwargs.get("amp33", u.Quantity(np.zeros((n_groups, 4096, 128), dtype=np.uint16), u.DN, dtype=np.uint16))
    tvac["amp33_reset_reads"] = kwargs.get(
        "amp33_reset_reads", u.Quantity(np.zeros((n_groups, 4096, 128), dtype=np.uint16), u.DN, dtype=np.uint16)
    )
    tvac["amp33_reference_read"] = kwargs.get(
        "amp33_reference_read", u.Quantity(np.zeros((n_groups, 4096, 128), dtype=np.uint16), u.DN, dtype=np.uint16)
    )

    # add guidewindow and reference
    tvac["guidewindow"] = kwargs.get(
        "guidewindow", u.Quantity(np.zeros((n_groups, 4096, 128), dtype=np.uint16), u.DN, dtype=np.uint16)
    )
    tvac["reference_read"] = kwargs.get(
        "reference_read", u.Quantity(np.zeros((n_groups, 4096, 128), dtype=np.uint16), u.DN, dtype=np.uint16)
    )
    tvac["reset_reads"] = kwargs.get(
        "reset_reads", u.Quantity(np.zeros((n_groups, 4096, 128), dtype=np.uint16), u.DN, dtype=np.uint16)
    )

    return save_node(tvac, filepath=filepath)
