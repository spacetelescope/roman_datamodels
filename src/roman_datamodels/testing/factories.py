"""
Factory methods that create (not necessarily realistic) nodes
that validate against their schemas.
"""
from datetime import datetime
import math
import random
import re
import secrets
import sys

from astropy.time import Time
from astropy import units as u
from astropy.modeling import models
import numpy as np

from .. import stnode
# from .. import table_definitions


__all__ = [
    "create_aperture",
    "create_cal_step",
    "create_coordinates",
    "create_ephemeris",
    "create_exposure",
    "create_flat_ref",
    "create_guidestar",
    "create_file_date",
    "create_calibration_software_version",
    "create_filename",
    "create_model_type",
    "create_origin",
    "create_prd_software_version",
    "create_sdf_software_version",
    "create_telescope",
    "create_meta",
    "create_node",
    "create_observation",
    "create_photometry",
    "create_pixelarea",
    "create_pointing",
    "create_program",
    "create_ref_meta",
    "create_target",
    "create_velocity_aberration",
    "create_visit",
    "create_wcsinfo",
    "create_wfi_image",
    "create_wfi_mode",
    "create_wfi_science_raw",
]


def _random_float(min=None, max=None):
    if min is None:
        min = sys.float_info.max * -1.0
    if max is None:
        max = sys.float_info.max
    value = random.random()
    return min + max * value - min * value


def _random_positive_float(max=None):
    return _random_float(min=0.0, max=max)


def _random_angle_radians():
    return _random_float(0.0, 2.0 * math.pi)


def _random_angle_degrees():
    return _random_float(0.0, 360.0)


def _random_mjd_timestamp():
    # Random timestamp between 2020-01-01 and 2030-01-01
    return _random_float(58849.0, 62502.0)


def _random_utc_timestamp():
    # Random timestamp between 2020-01-01 and 2030-01-01
    return _random_float(1577836800.0, 1893456000.0)


def _random_string_timestamp():
    return datetime.utcfromtimestamp(_random_utc_timestamp()).strftime("%Y-%m-%dT%H:%M:%S.%f")[0:23]


def _random_string_date():
    return datetime.utcfromtimestamp(_random_utc_timestamp()).strftime("%Y-%m-%d")


def _random_string_time():
    return datetime.utcfromtimestamp(_random_utc_timestamp()).strftime("%H:%M:%S.%f")[0:12]


def _random_astropy_time(time_format='unix'):
    timeobj =  Time(_random_utc_timestamp(), format="unix")

    if time_format == 'unix':
        return timeobj
    else:
        time_str = timeobj.to_value(format=time_format)
        timeobj = Time(time_str, format=time_format)
        return timeobj


def _random_int(min=None, max=None):
    # Assume 32-bit signed integers for now
    if min is None:
        min = -1 * 2 ** 31
    if max is None:
        max = 2 ** 31 - 1
    return random.randint(min, max)


def _random_positive_int(max=None):
    return _random_int(0, max)


def _random_choice(*args):
    return random.choice(args)


def _random_string(prefix="", max_length=None):
    if max_length is not None:
        random_length = min(16, max_length - len(prefix))
    else:
        random_length = 16

    return prefix + secrets.token_hex(random_length)


def _random_bool():
    return _random_choice(*[True, False])


def _random_array_float32(size=(4096, 4096), min=None, max=None):
    if min is None:
        min = np.finfo("float32").min
    if max is None:
        max = np.finfo("float32").max
    array = np.random.default_rng().random(size=size, dtype=np.float32)
    return min + max * array - min * array

def _random_array_uint8(size=(4096, 4096), min=None, max=None):
    if min is None:
        min = np.iinfo("uint8").min
    if max is None:
        max = np.iinfo("uint8").max
    return np.random.randint(min, high=max, size=size, dtype=np.uint8)

def _random_array_uint16(size=(4096, 4096), min=None, max=None):
    if min is None:
        min = np.iinfo("uint16").min
    if max is None:
        max = np.iinfo("uint16").max
    return np.random.randint(min, high=max, size=size, dtype=np.uint16)


def _random_array_uint32(size=(4096, 4096), min=None, max=None):
    if min is None:
        min = np.iinfo("uint32").min
    if max is None:
        max = np.iinfo("uint32").max
    return np.random.randint(min, high=max, size=size, dtype=np.uint32)


def _random_exposure_type():
    return _random_choice(
        "WFI_DARK",
        "WFI_FLAT",
        "WFI_GRISM",
        "WFI_IMAGE",
        "WFI_PRISM",
        "WFI_WFSC",
    )


def _random_detector():
    return _random_choice(
        "WFI01",
        "WFI02",
        "WFI03",
        "WFI04",
        "WFI05",
        "WFI06",
        "WFI07",
        "WFI08",
        "WFI09",
        "WFI10",
        "WFI11",
        "WFI12",
        "WFI13",
        "WFI14",
        "WFI15",
        "WFI16",
        "WFI17",
        "WFI18",
    )


def _random_optical_element():
    return _random_choice(
        "F062",
        "F087",
        "F106",
        "F129",
        "F146",
        "F158",
        "F184",
        "F213",
        "GRISM",
        "PRISM",
        "DARK",
    )


def _random_software_version():
    return "{}.{}.{}".format(
        _random_positive_int(100),
        _random_positive_int(100),
        _random_positive_int(100),
    )


def create_aperture(**kwargs):
    """
    Create a dummy Aperture instance with valid values for attributes
    required by the schema.

    Parameters
    ----------
    **kwargs
        Additional or overridden attributes.

    Returns
    -------
    roman_datamodels.stnode.Aperture
    """
    aper_number = _random_positive_int(17) + 1
    raw = {
        "name": f"WFI_{aper_number:02d}_FULL",
        "position_angle": _random_angle_degrees(),

    }
    raw.update(kwargs)

    return stnode.Aperture(raw)


def create_cal_step(**kwargs):
    """
    Create a dummy CalStep instance with valid values for attributes
    required by the schema.

    Parameters
    ----------
    **kwargs
        Additional or overridden attributes.

    Returns
    -------
    roman_datamodels.stnode.CalStep
    """
    raw = {
        "flat_field": _random_choice("N/A", "COMPLETE", "SKIPPED", "INCOMPLETE"),
        "dq_init": _random_choice("N/A", "COMPLETE", "SKIPPED", "INCOMPLETE"),
        "assign_wcs" : _random_choice("N/A", "COMPLETE", "SKIPPED", "INCOMPLETE"),
        "dark" : _random_choice("N/A", "COMPLETE", "SKIPPED", "INCOMPLETE"),
        "jump" : _random_choice("N/A", "COMPLETE", "SKIPPED", "INCOMPLETE"),
        "linearity" : _random_choice("N/A", "COMPLETE", "SKIPPED", "INCOMPLETE"),
        "photom": _random_choice("N/A", "COMPLETE", "SKIPPED", "INCOMPLETE"),
        "ramp_fit" : _random_choice("N/A", "COMPLETE", "SKIPPED", "INCOMPLETE"),
        "saturation" : _random_choice("N/A", "COMPLETE", "SKIPPED", "INCOMPLETE"),
    }
    raw.update(kwargs)

    return stnode.CalStep(raw)


def create_coordinates(**kwargs):
    """
    Create a dummy Coordinates instance with valid values for attributes
    required by the schema.

    Parameters
    ----------
    **kwargs
        Additional or overridden attributes.

    Returns
    -------
    roman_datamodels.stnode.Coordinates
    """
    raw = {
        "reference_frame": "ICRS",
    }
    raw.update(kwargs)

    return stnode.Coordinates(raw)


def create_ephemeris(**kwargs):
    """
    Create a dummy Ephemeris instance with valid values for attributes
    required by the schema.

    Parameters
    ----------
    **kwargs
        Additional or overridden attributes.

    Returns
    -------
    roman_datamodels.stnode.Ephemeris
    """
    raw = {
        "earth_angle": _random_angle_radians(),
        "ephemeris_reference_frame": _random_string("Frame ", 10),
        "moon_angle": _random_angle_radians(),
        "time": _random_mjd_timestamp(),
        "type": _random_choice("DEFINITIVE", "PREDICTED"),
        "spatial_x": _random_float(),
        "spatial_y": _random_float(),
        "spatial_z": _random_float(),
        "sun_angle": _random_angle_radians(),
        "velocity_x": _random_float(),
        "velocity_y": _random_float(),
        "velocity_z": _random_float(),
    }
    raw.update(kwargs)

    return stnode.Ephemeris(raw)


def create_exposure(**kwargs):
    """
    Create a dummy Exposure instance with valid values for attributes
    required by the schema.

    Parameters
    ----------
    **kwargs
        Additional or overridden attributes.

    Returns
    -------
    roman_datamodels.stnode.Exposure
    """
    raw = {
        "data_problem": _random_bool(),
        "duration": _random_positive_float(),
        "effective_exposure_time": _random_positive_float(),
        "elapsed_exposure_time": _random_positive_float(),
        "end_time": _random_astropy_time(time_format='isot'),
        "end_time_mjd": _random_mjd_timestamp(),
        "end_time_tdb": _random_mjd_timestamp(),
        "exposure_time": _random_positive_float(),
        "frame_divisor": _random_positive_int(),
        "frame_time": _random_positive_float(),
        "gain_factor": _random_positive_float(),
        "group_time": _random_positive_float(),
        "groupgap": 0,
        "id": _random_positive_int(),
        "integration_time": _random_positive_float(),
        "mid_time": _random_astropy_time(time_format='isot'),
        "mid_time_mjd": _random_mjd_timestamp(),
        "mid_time_tdb": _random_mjd_timestamp(),
        "nframes": 8,
        "ngroups": 6,
        "sca_number": _random_positive_int(),
        "start_time": _random_astropy_time(time_format='isot'),
        "start_time_mjd": _random_mjd_timestamp(),
        "start_time_tdb": _random_mjd_timestamp(),
        "type": _random_exposure_type(),
        "ma_table_name": _random_string("MA table "),
        "ma_table_number": _random_positive_int(max=998) + 1,
        "level0_compressed": True,
    }
    raw.update(kwargs)

    return stnode.Exposure(raw)


def create_ref_meta(**kwargs):
    """
    Create a dummy reference file metadata dictionary with valid
    values for attributes required by the schema (ref_common-1.0.0).

    Parameters
    ----------
    **kwargs
        Additional or overridden attributes.

    Returns
    -------
    dict
    """
    raw = {
        "author": _random_string("Reference author "),
        "description": _random_string("Reference description "),
        "exposure": {
            "type" : "WFI_IMAGE",
            "ngroups" : 6,
            "nframes" : 8,
            "groupgap" : 0,
            "ma_table_name": _random_string("MA table "),
            "ma_table_number": _random_positive_int(max=998) + 1,
        },
        "instrument": {
            "name": "WFI",
            "detector": _random_detector(),
            "optical_element": _random_optical_element(),
        },
        "origin": "STScI",
        "pedigree": "DUMMY",
        "telescope": create_telescope(**kwargs),
        "useafter": _random_astropy_time(),
    }
    raw.update(kwargs)

    return raw


def create_flat_ref(**kwargs):
    """
    Create a dummy FlatRef instance with valid values for attributes
    required by the schema.

    Parameters
    ----------
    **kwargs
        Additional or overridden attributes.

    Returns
    -------
    roman_datamodels.stnode.FlatRef
    """
    raw = {
        "data": _random_array_float32(min=0.0),
        "dq": _random_array_uint32(),
        "err": _random_array_float32(min=0.0),
        "meta": create_ref_meta(reftype="FLAT"),
    }
    raw.update(kwargs)

    return stnode.FlatRef(raw)


def create_dark_ref(**kwargs):
    """
    Create a dummy DarkRef instance with valid values for attributes
    required by the schema.

    Parameters
    ----------
    **kwargs
        Additional or overridden attributes.

    Returns
    -------
    roman_datamodels.stnode.DarkRef
    """
    raw = {
        "data": _random_array_float32((2, 4096, 4096)),
        "dq": _random_array_uint32(),
        "err": _random_array_float32((2, 4096, 4096)),
        "meta": create_ref_meta(reftype="DARK")
    }
    raw.update(kwargs)
    raw['meta']['exposure']['p_exptype'] = "WFI_IMAGE|WFI_GRISM|WFI_PRISM|"

    return stnode.DarkRef(raw)


def create_distortion_ref(**kwargs):
    """
    Create a dummy DistortionRef instance with valid values for attributes
    required by the schema.

    Parameters
    ----------
    **kwargs
        Additional or overridden attributes.

    Returns
    -------
    roman_datamodels.stnode.DistortionRef
    """
    m = models.Shift(1) & models.Shift(2)
    raw = {
        "coordinate_distortion_transform": m,
        "meta": create_ref_meta(reftype="DISTORTION")
    }
    raw.update(kwargs)

    raw['meta']['input_units'] = u.pixel
    raw['meta']['output_units'] = u.arcsec

    return stnode.DistortionRef(raw)


def create_gain_ref(**kwargs):
    """
    Create a dummy GainRef instance with valid values for attributes
    required by the schema.

    Parameters
    ----------
    **kwargs
        Additional or overridden attributes.

    Returns
    -------
    roman_datamodels.stnode.GainRef
    """
    raw = {
        "data": _random_array_float32((4096, 4096)),
        "meta": create_ref_meta(reftype="GAIN"),
    }
    raw.update(kwargs)

    return stnode.GainRef(raw)

def create_linearity_ref(**kwargs):
    """
    Create a dummy LinearityRef instance with valid values for attributes
    required by the schema.

    Parameters
    ----------
    **kwargs
        Additional or overridden attributes.

    Returns
    -------
    roman_datamodels.stnode.LinearityRef
    """
    raw = {
        "coeffs": _random_array_float32((2, 4096, 4096)),
        "dq": _random_array_uint32((4096, 4096)),
        "meta": create_ref_meta(reftype="LINEARITY"),
    }
    raw.update(kwargs)

    return stnode.LinearityRef(raw)


def create_mask_ref(**kwargs):
    """
    Create a dummy MaskRef instance with valid values for attributes
    required by the schema.

    Parameters
    ----------
    **kwargs
        Additional or overridden attributes.

    Returns
    -------
    roman_datamodels.stnode.MaskRef
    """
    raw = {
        "meta": create_ref_meta(reftype="MASK"),
        "dq": _random_array_uint32(),
    }
    raw.update(kwargs)

    return stnode.MaskRef(raw)

def create_pixelarea_ref(**kwargs):
    """
    Create a dummy PixelareaRef instance with valid values for attributes
    required by the schema.

    Parameters
    ----------
    **kwargs
        Additional or overridden attributes.

    Returns
    -------
    roman_datamodels.stnode.PixelareaRef
    """
    raw = {
        "data": _random_array_float32((4096, 4096)),
        "meta": create_ref_meta(reftype="AREA"),
    }
    raw['meta']['photometry'] = {
        'pixelarea_steradians': _random_positive_float() * u.sr,
        'pixelarea_arcsecsq': _random_positive_float() * u.arcsec ** 2,
    }
    raw.update(kwargs)

    return stnode.PixelareaRef(raw)

def create_readnoise_ref(**kwargs):
    """
    Create a dummy ReadnoiseRef instance with valid values for attributes
    required by the schema.

    Parameters
    ----------
    **kwargs
        Additional or overridden attributes.

    Returns
    -------
    roman_datamodels.stnode.ReadnoiseRef
    """
    raw = {
        "data": _random_array_float32((4096, 4096)),
        "meta": create_ref_meta(reftype="READNOISE"),
    }
    raw.update(kwargs)
    raw['meta']['exposure']['p_exptype'] = "WFI_IMAGE|WFI_GRISM|WFI_PRISM|"

    return stnode.ReadnoiseRef(raw)

def create_saturation_ref(**kwargs):
    """
    Create a dummy SaturationRef instance with valid values for attributes
    required by the schema.

    Parameters
    ----------
    **kwargs
        Additional or overridden attributes.

    Returns
    -------
    roman_datamodels.stnode.SaturationRef
    """
    raw = {
        "data": _random_array_float32((4096, 4096)),
        "dq": _random_array_uint32((4096, 4096)),
        "meta": create_ref_meta(reftype="SATURATION"),
    }
    raw.update(kwargs)

    return stnode.SaturationRef(raw)

def create_superbias_ref(**kwargs):
    """
    Create a dummy SuperbiasRef instance with valid values for attributes
    required by the schema.

    Parameters
    ----------
    **kwargs
        Additional or overridden attributes.

    Returns
    -------
    roman_datamodels.stnode.SuperbiasRef
    """
    raw = {
        "data": _random_array_float32((4096, 4096)),
        "dq": _random_array_uint32((4096, 4096)),
        "err": _random_array_float32((4096, 4096)),
        "meta": create_ref_meta(reftype="BIAS"),
    }
    raw.update(kwargs)

    return stnode.SuperbiasRef(raw)

def create_wfi_img_photom_ref(**kwargs):
    """
    Create a dummy WfiImgPhotomRef instance with valid values for attributes
    required by the schema.

    Parameters
    ----------
    **kwargs
        Additional or overridden attributes.

    Returns
    -------
    roman_datamodels.stnode.WfiImgPhotomRef
    """
    raw_dict = {
        "F062":
            {"photmjsr": (1.0e-15  * np.random.random() * u.megajansky / u.steradian),
             "uncertainty": (1.0e-16  * np.random.random() * u.megajansky / u.steradian),
             "pixelareasr": 1.0e-13 * u.steradian},
        "F087":
            {"photmjsr": (1.0e-15  * np.random.random() * u.megajansky / u.steradian),
             "uncertainty": (1.0e-16  * np.random.random() * u.megajansky / u.steradian),
             "pixelareasr": 1.0e-13 * u.steradian},
        "F106":
            {"photmjsr": (1.0e-15  * np.random.random() * u.megajansky / u.steradian),
             "uncertainty": (1.0e-16  * np.random.random() * u.megajansky / u.steradian),
             "pixelareasr": 1.0e-13 * u.steradian},
        "F129":
            {"photmjsr": (1.0e-15  * np.random.random() * u.megajansky / u.steradian),
             "uncertainty": (1.0e-16  * np.random.random() * u.megajansky / u.steradian),
             "pixelareasr": 1.0e-13 * u.steradian},
        "F146":
            {"photmjsr": (1.0e-15  * np.random.random() * u.megajansky / u.steradian),
             "uncertainty": (1.0e-16  * np.random.random() * u.megajansky / u.steradian),
             "pixelareasr": 1.0e-13 * u.steradian},
        "F158":
            {"photmjsr": (1.0e-15  * np.random.random() * u.megajansky / u.steradian),
             "uncertainty": (1.0e-16  * np.random.random() * u.megajansky / u.steradian),
             "pixelareasr": 1.0e-13 * u.steradian},
        "F184":
            {"photmjsr": (1.0e-15  * np.random.random() * u.megajansky / u.steradian),
             "uncertainty": (1.0e-16  * np.random.random() * u.megajansky / u.steradian),
             "pixelareasr": 1.0e-13 * u.steradian},
        "F213":
            {"photmjsr": (1.0e-15  * np.random.random() * u.megajansky / u.steradian),
             "uncertainty": (1.0e-16  * np.random.random() * u.megajansky / u.steradian),
             "pixelareasr": 1.0e-13 * u.steradian},
        "GRISM":
            {"photmjsr": None,
             "uncertainty": None,
             "pixelareasr": 1.0e-13 * u.steradian},
        "PRISM":
            {"photmjsr": None,
             "uncertainty": None,
             "pixelareasr": 1.0e-13 * u.steradian},
        "DARK":
            {"photmjsr": None,
             "uncertainty": None,
             "pixelareasr": 1.0e-13 * u.steradian},
    }

    raw = {
        "phot_table": raw_dict,
        "meta": create_ref_meta(reftype="PHOTOM"),
    }
    raw.update(kwargs)

    return stnode.WfiImgPhotomRef(raw)


def create_guidestar(**kwargs):
    """
    Create a dummy Guidestar instance with valid values for attributes
    required by the schema.

    Parameters
    ----------
    **kwargs
        Additional or overridden attributes.

    Returns
    -------
    roman_datamodels.stnode.Guidestar
    """
    raw = {
        "data_end": _random_mjd_timestamp(),
        "data_start": _random_mjd_timestamp(),
        "gs_ctd_ux": _random_positive_float(),
        "gs_ctd_uy": _random_positive_float(),
        "gs_ctd_x": _random_positive_float(),
        "gs_ctd_y": _random_positive_float(),
        "gs_dec": _random_float(math.pi / -2.0, math.pi / 2.0),
        "gs_epoch": _random_string("Epoch ", 10),
        "gs_mag": _random_float(),
        "gs_mudec": _random_float(),
        "gs_mura": _random_float(),
        "gs_para": _random_float(),
        "gs_ra": _random_angle_radians(),
        "gs_udec": _random_positive_float(),
        "gs_umag": _random_positive_float(),
        "gs_ura": _random_positive_float(),
        "gw_id": _random_string("ID ", 20),
        "gw_fgs_mode": "WSM-ACQ-2",
        "gw_window_xsize": 16.0,
        "gw_window_xstart": _random_positive_float(),
        "gw_window_ysize": 16.0,
        "gw_window_ystart": _random_positive_float(),
        "gs_pattern_error": _random_positive_float(),
    }
    raw["gw_window_xstop"] = raw["gw_window_xstart"] + 16.0
    raw["gw_window_ystop"] = raw["gw_window_ystart"] + 16.0
    raw.update(kwargs)

    return stnode.Guidestar(raw)

def create_file_date(**kwargs):
    return stnode.FileDate(kwargs.get("file_date", _random_astropy_time()))


def create_calibration_software_version(**kwargs):
    return stnode.CalibrationSoftwareVersion(kwargs.get("calibration_sofware_version", _random_string("Version ", 120)))


def create_filename(**kwargs):
    return stnode.Filename(kwargs.get("filename", _random_string("Filename ", 120)))


def create_model_type(**kwargs):
    return stnode.ModelType(kwargs.get("model_type", _random_string("Model type ", 50)))


def create_origin(**kwargs):
    return stnode.Origin(kwargs.get("origin", "STSCI"))


def create_prd_software_version(**kwargs):
    return stnode.PrdSoftwareVersion(kwargs.get("prd_software_version", _random_string("S&OC PRD ", 120)))


def create_sdf_software_version(**kwargs):
    return stnode.SdfSoftwareVersion(kwargs.get("sdf_software_version", _random_software_version()))


def create_telescope(**kwargs):
    return stnode.Telescope(kwargs.get("telescope", "ROMAN"))


def _create_basic_meta(**kwargs):
    """
    Create the metadata from the basic-1.0.0 schema, which is shared
    between references and datasets.

    Returns
    -------
    dict
    """

    return {
        "calibration_software_version": create_calibration_software_version(**kwargs),
        "crds_context_used": "roman_{:04d}.pmap".format(_random_positive_int(9999)),
        "crds_software_version": _random_software_version(),
        "filename": create_filename(**kwargs),
        "file_date": create_file_date(**kwargs),
        "model_type": create_model_type(**kwargs),
        "origin": create_origin(**kwargs),
        "prd_software_version": create_prd_software_version(**kwargs),
        "sdf_software_version": create_sdf_software_version(**kwargs),
        "telescope": create_telescope(**kwargs),
    }


def create_meta(**kwargs):
    """
    Create a dummy metadata dictionary with valid values for attributes
    required by the schema (common-1.0.0).

    Parameters
    ----------
    **kwargs
        Additional or overridden attributes.

    Returns
    -------
    dict
    """
    raw = {
        "aperture": create_aperture(),
        "cal_step": create_cal_step(),
        "coordinates": create_coordinates(),
        "ephemeris": create_ephemeris(),
        "exposure": create_exposure(),
        "guidestar": create_guidestar(),
        "instrument": create_wfi_mode(),
        "observation": create_observation(),
        "pointing": create_pointing(),
        "program": create_program(),
        "ref_file": create_ref_file(),
        "target": create_target(),
        "velocity_aberration": create_velocity_aberration(),
        "visit": create_visit(),
        "wcsinfo": create_wcsinfo(),
    }
    raw.update(_create_basic_meta(**kwargs))
    raw.update(kwargs)

    return raw


def create_observation(**kwargs):
    """
    Create a dummy Observation instance with valid values for attributes
    required by the schema.

    Parameters
    ----------
    **kwargs
        Additional or overridden attributes.

    Returns
    -------
    roman_datamodels.stnode.Observation
    """
    raw = {
        "execution_plan": _random_positive_int(),
        "exposure": _random_positive_int(),
        "obs_id": _random_string("Obs ID ", 26),
        "observation": _random_positive_int(),
        "observation_label": _random_string("Observation label "),
        "pass": _random_positive_int(),
        "program": _random_positive_int(),
        "segment": _random_positive_int(),
        "survey": _random_choice("HLS", "EMS", "SN", "N/A"),
        "template": _random_string("Template ", 50),
        "visit": _random_positive_int(),
        "visit_file_activity": _random_string(max_length=2),
        "visit_file_group": _random_positive_int(),
        "visit_file_sequence": _random_positive_int(),
        "visit_id": _random_string("Visit ID ", 19),
    }
    raw.update(kwargs)

    return stnode.Observation(raw)


def create_photometry(**kwargs):
    """
    Create a dummy Photometry instance with valid values for attributes
    required by the schema.

    Parameters
    ----------
    **kwargs
        Additional or overridden attributes.

    Returns
    -------
    roman_datamodels.stnode.Photometry
    """
    raw = {
        "conversion_megajanskys": _random_positive_float() * u.MJy / u.sr,
        "conversion_microjanskys": _random_positive_float() * u.uJy / u.sr,
        "pixelarea_arcsecsq": _random_positive_float() * u.arcsec ** 2,
        "pixelarea_steradians": _random_positive_float() * u.sr,
        "conversion_megajanskys_uncertainty": _random_positive_float() * u.MJy / u.sr,
        "conversion_microjanskys_uncertainty": _random_positive_float() * u.uJy / u.sr
    }
    raw.update(kwargs)

    return stnode.Photometry(raw)


def create_pixelarea(**kwargs):
    """
    Create a dummy Pixelarea instance with valid values for attributes
    required by the schema.

    Parameters
    ----------
    **kwargs
        Additional or overridden attributes.

    Returns
    -------
    roman_datamodels.stnode.Pixelarea
    """
    raw = {
        "area": _random_array_float32(min=0.0),
    }
    raw.update(kwargs)
    raw["meta"] = {}
    raw["meta"]["photometry"] = {'pixelarea_steradians': .3 * u.sr,
                                 'pixelarea_arcsecsq': .3 * u.arcsec ** 2}

    return stnode.Pixelarea(raw)


def create_pointing(**kwargs):
    """
    Create a dummy Pointing instance with valid values for attributes
    required by the schema.

    Parameters
    ----------
    **kwargs
        Additional or overridden attributes.

    Returns
    -------
    roman_datamodels.stnode.Pointing
    """
    raw = {
        "dec_v1": _random_float(-90.0, 90.0),
        "pa_v3": _random_angle_degrees(),
        "ra_v1": _random_angle_degrees(),
    }
    raw.update(kwargs)

    return stnode.Pointing(raw)


def create_program(**kwargs):
    """
    Create a dummy Program instance with valid values for attributes
    required by the schema.

    Parameters
    ----------
    **kwargs
        Additional or overridden attributes.

    Returns
    -------
    roman_datamodels.stnode.Program
    """
    raw = {
        "category": _random_string("Cat ", 6),
        "continuation_id": _random_positive_int(),
        "pi_name": _random_string("PI name ", 100),
        "science_category": _random_string("Science category ", 100),
        "subcategory": _random_string("Subcategory ", 15),
        "title": _random_string("Proposal title ", 100),
    }
    raw.update(kwargs)

    return stnode.Program(raw)


def create_ramp(**kwargs):
    """
    Create a dummy Ramp instance with valid values for attributes
    required by the schema.

    Parameters
    ----------
    **kwargs
        Additional or overridden attributes.

    Returns
    -------
    roman_datamodels.stnode.Ramp
    """

    raw = {
        "meta": create_meta(),
        "data": _random_array_float32((2, 4096, 4096)),
        "pixeldq": _random_array_uint32((4096, 4096)),
        "groupdq": _random_array_uint8((2, 4096, 4096)),
        "err": _random_array_float32(size=(2, 4096, 4096),min=0.0),
        "amp33": _random_array_uint16((2, 4096, 128)),
        "border_ref_pix_right": _random_array_float32((2, 4096, 4)),
        "border_ref_pix_left": _random_array_float32((2, 4096, 4)),
        "border_ref_pix_top": _random_array_float32((2, 4, 4096)),
        "border_ref_pix_bottom": _random_array_float32((2, 4, 4096)),
        "dq_border_ref_pix_right": _random_array_uint32((4096, 4)),
        "dq_border_ref_pix_left": _random_array_uint32((4096, 4)),
        "dq_border_ref_pix_top": _random_array_uint32((4, 4096)),
        "dq_border_ref_pix_bottom": _random_array_uint32((4, 4096))
    }
    raw.update(kwargs)

    return stnode.Ramp(raw)

def create_ramp_fit_output(**kwargs):
    """
    Create a dummy RampFitOutput instance with valid values for attributes
    required by the schema.

    Parameters
    ----------
    **kwargs
        Additional or overridden attributes.

    Returns
    -------
    roman_datamodels.stnode.RampFitOutput
    """

    seg_shape = (2, 4096, 4096)

    raw = {
        "meta": create_meta(),
        "slope": _random_array_float32(seg_shape),
        "sigslope": _random_array_float32(seg_shape),
        "yint": _random_array_float32(seg_shape),
        "sigyint": _random_array_float32(seg_shape),
        "pedestal": _random_array_float32(seg_shape[1:]),
        "weights": _random_array_float32(seg_shape),
        "crmag": _random_array_float32(seg_shape),
        "var_poisson": _random_array_float32(seg_shape),
        "var_rnoise": _random_array_float32(seg_shape),
    }
    raw.update(kwargs)

    return stnode.RampFitOutput(raw)


def create_guidewindow(**kwargs):
    """
    Create a dummy Guide Window instance with valid values for attributes
    required by the schema.

    Parameters
    ----------
    **kwargs
        Additional or overridden attributes.

    Returns
    -------
    roman_datamodels.stnode.Guidewindow
    """

    seg_shape = (2, 8, 16, 32, 32)

    raw = {
        "meta": create_meta(),
        "pedestal_frames": _random_array_uint16(seg_shape),
        "signal_frames": _random_array_uint16(seg_shape),
        "amp33": _random_array_uint16(seg_shape),
    }
    raw.update(kwargs)

    raw["meta"]["file_creation_time"] = _random_astropy_time()
    raw["meta"]["gw_start_time"] = _random_astropy_time()
    raw["meta"]["gw_end_time"] = _random_astropy_time()
    raw["meta"]["gw_function_start_time"] = _random_astropy_time()
    raw["meta"]["gw_function_end_time"] = _random_astropy_time()
    raw['meta']['gw_frame_readout_time'] = _random_float()
    raw['meta']['pedestal_resultant_exp_time'] = _random_float()
    raw['meta']['signal_resultant_exp_time'] = _random_float()
    raw['meta']['gw_acq_number'] = _random_int()
    raw['meta']['gw_mode'] = 'WIM-ACQ'
    raw['meta']['gw_window_xstart'] = _random_float()
    raw['meta']['gw_window_ystart'] = _random_float()
    raw['meta']['gw_window_xstop'] = raw['meta']["gw_window_xstart"] + 16.0
    raw['meta']['gw_window_ystop'] = raw['meta']["gw_window_ystart"] + 16.0
    raw['meta']['gw_window_xsize'] = 16.0
    raw['meta']['gw_window_ysize'] = 16.0
    raw['meta']['gw_acq_exec_stat'] = _random_string("Status ", 15)

    raw['meta']["gw_acq_exec_stat"] = _random_string("Status ", 15)
    raw['meta']["gw_function_end_time"] = _random_astropy_time()
    raw['meta']["gw_function_start_time"] = _random_astropy_time()

    return stnode.Guidewindow(raw)


def create_target(**kwargs):
    """
    Create a dummy Target instance with valid values for attributes
    required by the schema.

    Parameters
    ----------
    **kwargs
        Additional or overridden attributes.

    Returns
    -------
    roman_datamodels.stnode.Target
    """
    raw = {
        "catalog_name": _random_string("Catalog name ", 256),
        "dec": _random_float(-90.0, 90.0),
        "dec_uncertainty": _random_positive_float(),
        "proper_motion_dec": _random_float(),
        "proper_motion_epoch": _random_string_timestamp(),
        "proper_motion_ra": _random_float(),
        "proposer_dec": _random_float(-90.0, 90.0),
        "proposer_name": _random_string("Proposer name ", 100),
        "proposer_ra": _random_angle_degrees(),
        "ra": _random_angle_degrees(),
        "ra_uncertainty": _random_positive_float(),
        "source_type": _random_choice("EXTENDED", "POINT", "UNKNOWN"),
        "source_type_apt": _random_choice("EXTENDED", "POINT", "UNKNOWN"),
        "type": _random_choice("FIXED", "MOVING", "GENERIC"),
    }
    raw.update(kwargs)

    return stnode.Target(raw)


def create_velocity_aberration(**kwargs):
    """
    Create a dummy VelocityAberration instance with valid values for attributes
    required by the schema.

    Parameters
    ----------
    **kwargs
        Additional or overridden attributes.

    Returns
    -------
    roman_datamodels.stnode.VelocityAberration
    """
    raw = {
        # TODO: Select reasonable min and max values for these
        "ra_offset": _random_float(),
        "dec_offset": _random_float(),
        "scale_factor": _random_float(),
    }
    raw.update(kwargs)

    return stnode.VelocityAberration(raw)


def create_visit(**kwargs):
    """
    Create a dummy Visit instance with valid values for attributes
    required by the schema.

    Parameters
    ----------
    **kwargs
        Additional or overridden attributes.

    Returns
    -------
    roman_datamodels.stnode.Visit
    """
    raw = {
        "engineering_quality": _random_choice("OK", "SUSPECT"),
        "pointing_engdb_quality": _random_choice("CALCULATED", "PLANNED"),
        "type": _random_string("Visit type ", 30),
        "start_time": _random_astropy_time(),
        "end_time": _random_astropy_time(),
        "status": _random_string("Status ", 15),
        "total_exposures": _random_positive_int(),
        "internal_target": _random_bool(),
        "target_of_opportunity": _random_bool(),
    }
    raw.update(kwargs)

    return stnode.Visit(raw)


def create_wcsinfo(**kwargs):
    """
    Create a dummy Wcsinfo instance with valid values for attributes
    required by the schema.

    Parameters
    ----------
    **kwargs
        Additional or overridden attributes.

    Returns
    -------
    roman_datamodels.stnode.Wcsinfo
    """
    raw = {
        "dec_ref": _random_float(-90.0, 90.0),
        "ra_ref": _random_positive_float(360.0),
        "roll_ref": _random_float(),
        "s_region": _random_string("Spatial extent "),
        "v2_ref": _random_float(),
        "v3_ref": _random_float(),
        "v3yangle": _random_float(),
        "vparity": _random_int(),
    }
    raw.update(kwargs)

    return stnode.Wcsinfo(raw)


def create_cal_logs():
    """
    Create a dummy CalLogs instance with valid values for attributes
    required by the schema.

    Returns
    -------
    roman_datamodels.stnode.CalLogs
    """
    return stnode.CalLogs(
        [
            "2021-11-15T09:15:07.12Z :: FlatFieldStep :: INFO :: Completed",
            "2021-11-15T10:22.55.55Z :: RampFittingStep :: WARNING :: Wow, lots of Cosmic Rays detected",
        ]
    )


def create_wfi_image(**kwargs):
    """
    Create a dummy WfiImage instance with valid values for attributes
    required by the schema.

    Parameters
    ----------
    **kwargs
        Additional or overridden attributes.

    Returns
    -------
    roman_datamodels.stnode.WfiImage
    """

    raw = {
        "data": _random_array_float32((4088, 4088)),
        "dq": _random_array_uint32((4088, 4088)),
        "err": _random_array_float32((4088, 4088), min=0.0),
        "meta": create_meta(),
        "var_flat": _random_array_float32((4088, 4088)),
        "var_poisson": _random_array_float32((4088, 4088)),
        "var_rnoise": _random_array_float32((4088, 4088)),
        "amp33": _random_array_uint16((2, 4096, 128)),
        "border_ref_pix_right": _random_array_float32((2, 4096, 4)),
        "border_ref_pix_left": _random_array_float32((2, 4096, 4)),
        "border_ref_pix_top": _random_array_float32((2, 4, 4096)),
        "border_ref_pix_bottom": _random_array_float32((2, 4, 4096)),
        "dq_border_ref_pix_right": _random_array_uint32((4096, 4)),
        "dq_border_ref_pix_left": _random_array_uint32((4096, 4)),
        "dq_border_ref_pix_top": _random_array_uint32((4, 4096)),
        "dq_border_ref_pix_bottom": _random_array_uint32((4, 4096)),
        "cal_logs": create_cal_logs(),
    }
    raw.update(kwargs)
    raw["meta"]["photometry"] = create_photometry()

    return stnode.WfiImage(raw)


def create_wfi_mode(**kwargs):
    """
    Create a dummy WfiMode instance with valid values for attributes
    required by the schema.

    Parameters
    ----------
    **kwargs
        Additional or overridden attributes.

    Returns
    -------
    roman_datamodels.stnode.WfiMode
    """
    raw = {
        "detector": _random_detector(),
        "name": "WFI",
        "optical_element": _random_optical_element(),
    }
    raw.update(kwargs)

    return stnode.WfiMode(raw)


def create_wfi_science_raw(**kwargs):
    """
    Create a dummy WfiScienceRaw instance with valid values for attributes
    required by the schema.

    Parameters
    ----------
    **kwargs
        Additional or overridden attributes.

    Returns
    -------
    roman_datamodels.stnode.WfiScienceRaw
    """
    raw = {
        # TODO: What should this shape be?
        "data": _random_array_uint16((2, 4096, 4096)),
        "amp33": _random_array_uint16((2, 4096, 128)),
        "meta": create_meta(),
    }
    raw.update(kwargs)

    return stnode.WfiScienceRaw(raw)


def _camel_case_to_snake_case(value):
    # Courtesy of https://stackoverflow.com/a/1176023
    return re.sub(r"(?<!^)(?=[A-Z])", "_", value).lower()


def create_node(node_class, **kwargs):
    """
    Create a dummy node of the specified class with valid values
    for attributes required by the schema.

    Parameters
    ----------
    node_class : type
        Node class.
    **kwargs
        Additional or overridden attributes.

    Returns
    -------
    roman_datamodels.stnode.TaggedObjectNode
    """
    method_name = "create_" + _camel_case_to_snake_case(node_class.__name__)
    if not method_name in globals():
        raise ValueError(f"Factory method not implemented for class {node_class.__name__}")
    return globals()[method_name](**kwargs)


def create_ref_file(**kwargs):
    """
    Create a dummy ref_file instance with valid values for attributes
    required by the schema.

    Parameters
    ----------
    **kwargs
        Additional or overridden attributes.

    Returns
    -------
    roman_datamodels.stnode.RefFileName
    """
    reftypes = ["dark", "distortion", "flat", "gain", "linearity", "mask", "readnoise",
                "saturation", "photom" ]
    val = "N/A"
    raw = dict(zip(reftypes, [val] * len(reftypes)))
    raw["crds"] = {"sw_version": "12.1", "context_used": "781"}
    raw.update(kwargs)

    return stnode.RefFile(raw)
