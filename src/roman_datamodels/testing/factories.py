"""
Factory methods that create (not necessarily realistic) nodes
that validate against their schemas.
"""
import math
import re

import numpy as np
from astropy import units as u
from astropy.modeling import models

from roman_datamodels import random_utils

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
    "create_source_detection",
    "create_target",
    "create_velocity_aberration",
    "create_visit",
    "create_wcsinfo",
    "create_wfi_image",
    "create_wfi_mode",
    "create_wfi_science_raw",
]


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
    aper_number = random_utils.generate_positive_int(17) + 1
    raw = {
        "name": f"WFI_{aper_number:02d}_FULL",
        "position_angle": random_utils.generate_angle_degrees(),
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
        "flat_field": random_utils.generate_choice("N/A", "COMPLETE", "SKIPPED", "INCOMPLETE"),
        "dq_init": random_utils.generate_choice("N/A", "COMPLETE", "SKIPPED", "INCOMPLETE"),
        "assign_wcs": random_utils.generate_choice("N/A", "COMPLETE", "SKIPPED", "INCOMPLETE"),
        "dark": random_utils.generate_choice("N/A", "COMPLETE", "SKIPPED", "INCOMPLETE"),
        "jump": random_utils.generate_choice("N/A", "COMPLETE", "SKIPPED", "INCOMPLETE"),
        "linearity": random_utils.generate_choice("N/A", "COMPLETE", "SKIPPED", "INCOMPLETE"),
        "photom": random_utils.generate_choice("N/A", "COMPLETE", "SKIPPED", "INCOMPLETE"),
        "source_detection": random_utils.generate_choice("N/A", "COMPLETE", "SKIPPED", "INCOMPLETE"),
        "ramp_fit": random_utils.generate_choice("N/A", "COMPLETE", "SKIPPED", "INCOMPLETE"),
        "saturation": random_utils.generate_choice("N/A", "COMPLETE", "SKIPPED", "INCOMPLETE"),
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
        "earth_angle": random_utils.generate_angle_radians(),
        "ephemeris_reference_frame": random_utils.generate_string("Frame ", 10),
        "moon_angle": random_utils.generate_angle_radians(),
        "time": random_utils.generate_mjd_timestamp(),
        "type": random_utils.generate_choice("DEFINITIVE", "PREDICTED"),
        "spatial_x": random_utils.generate_float(),
        "spatial_y": random_utils.generate_float(),
        "spatial_z": random_utils.generate_float(),
        "sun_angle": random_utils.generate_angle_radians(),
        "velocity_x": random_utils.generate_float(),
        "velocity_y": random_utils.generate_float(),
        "velocity_z": random_utils.generate_float(),
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
        "data_problem": random_utils.generate_bool(),
        "duration": random_utils.generate_positive_float(),
        "effective_exposure_time": random_utils.generate_positive_float(),
        "elapsed_exposure_time": random_utils.generate_positive_float(),
        "end_time": random_utils.generate_astropy_time(time_format="isot"),
        "end_time_mjd": random_utils.generate_mjd_timestamp(),
        "end_time_tdb": random_utils.generate_mjd_timestamp(),
        "exposure_time": random_utils.generate_positive_float(),
        "frame_divisor": random_utils.generate_positive_int(),
        "frame_time": random_utils.generate_positive_float(),
        "gain_factor": random_utils.generate_positive_float(),
        "group_time": random_utils.generate_positive_float(),
        "groupgap": 0,
        "id": random_utils.generate_positive_int(),
        "integration_time": random_utils.generate_positive_float(),
        "mid_time": random_utils.generate_astropy_time(time_format="isot"),
        "mid_time_mjd": random_utils.generate_mjd_timestamp(),
        "mid_time_tdb": random_utils.generate_mjd_timestamp(),
        "nframes": 8,
        "ngroups": 6,
        "sca_number": random_utils.generate_positive_int(),
        "start_time": random_utils.generate_astropy_time(time_format="isot"),
        "start_time_mjd": random_utils.generate_mjd_timestamp(),
        "start_time_tdb": random_utils.generate_mjd_timestamp(),
        "type": random_utils.generate_exposure_type(),
        "ma_table_name": random_utils.generate_string("MA table "),
        "ma_table_number": random_utils.generate_positive_int(max=998) + 1,
        "level0_compressed": True,
        "read_pattern": [[1, 2, 3], [4], [5, 6]],
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
        "author": random_utils.generate_string("Reference author "),
        "description": random_utils.generate_string("Reference description "),
        "exposure": {
            "type": "WFI_IMAGE",
            "ngroups": 6,
            "nframes": 8,
            "groupgap": 0,
            "ma_table_name": random_utils.generate_string("MA table "),
            "ma_table_number": random_utils.generate_positive_int(max=998) + 1,
        },
        "instrument": {
            "name": "WFI",
            "detector": random_utils.generate_detector(),
            "optical_element": random_utils.generate_optical_element(),
        },
        "origin": "STScI",
        "pedigree": "DUMMY",
        "telescope": create_telescope(**kwargs),
        "useafter": random_utils.generate_astropy_time(),
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
        "data": random_utils.generate_array_float32(min=0.0),
        "dq": random_utils.generate_array_uint32(),
        "err": random_utils.generate_array_float32(min=0.0),
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
        "data": random_utils.generate_array_float32((2, 4096, 4096), units=u.DN),
        "dq": random_utils.generate_array_uint32(),
        "err": random_utils.generate_array_float32((2, 4096, 4096), units=u.DN),
        "meta": create_ref_meta(reftype="DARK"),
    }
    raw.update(kwargs)
    raw["meta"]["exposure"]["p_exptype"] = "WFI_IMAGE|WFI_GRISM|WFI_PRISM|"

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
    raw = {"coordinate_distortion_transform": m, "meta": create_ref_meta(reftype="DISTORTION")}
    raw.update(kwargs)

    raw["meta"]["input_units"] = u.pixel
    raw["meta"]["output_units"] = u.arcsec

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
        "data": random_utils.generate_array_float32((4096, 4096), units=u.electron / u.DN),
        "meta": create_ref_meta(reftype="GAIN"),
    }
    raw.update(kwargs)

    return stnode.GainRef(raw)


def create_ipc_ref(**kwargs):
    """
    Create a dummy IpcRef instance with valid values for attributes
    required by the schema.

    Parameters
    ----------
    **kwargs
        Additional or overridden attributes.

    Returns
    -------
    roman_datamodels.stnode.IpcRef
    """
    kernel = random_utils.generate_array_float32((3, 3), min=0, max=1e5)
    kernel /= np.sum(kernel)
    raw = {
        "data": kernel,
        "meta": create_ref_meta(reftype="IPC"),
    }
    raw.update(kwargs)

    return stnode.IpcRef(raw)


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
        "coeffs": random_utils.generate_array_float32((2, 4096, 4096)),
        "dq": random_utils.generate_array_uint32((4096, 4096)),
        "meta": create_ref_meta(reftype="LINEARITY"),
    }
    raw.update(kwargs)

    raw["meta"]["input_units"] = u.DN
    raw["meta"]["output_units"] = u.DN

    return stnode.LinearityRef(raw)


def create_inverse_linearity_ref(**kwargs):
    """
    Create a dummy InverseLinearityRef instance with valid values for attributes
    required by the schema.

    Parameters
    ----------
    **kwargs
        Additional or overridden attributes.

    Returns
    -------
    roman_datamodels.stnode.InverseLinearityRef
    """
    raw = {
        "coeffs": random_utils.generate_array_float32((2, 4096, 4096)),
        "dq": random_utils.generate_array_uint32((4096, 4096)),
        "meta": create_ref_meta(reftype="INVERSE_LINEARITY"),
    }
    raw.update(kwargs)

    raw["meta"]["input_units"] = u.DN
    raw["meta"]["output_units"] = u.DN

    return stnode.InverseLinearityRef(raw)


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
        "dq": random_utils.generate_array_uint32(),
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
        "data": random_utils.generate_array_float32((4096, 4096)),
        "meta": create_ref_meta(reftype="AREA"),
    }
    raw["meta"]["photometry"] = {
        "pixelarea_steradians": random_utils.generate_positive_float() * u.sr,
        "pixelarea_arcsecsq": random_utils.generate_positive_float() * u.arcsec**2,
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
        "data": random_utils.generate_array_float32((4096, 4096), units=u.DN),
        "meta": create_ref_meta(reftype="READNOISE"),
    }
    raw.update(kwargs)
    raw["meta"]["exposure"]["p_exptype"] = "WFI_IMAGE|WFI_GRISM|WFI_PRISM|"

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
        "data": random_utils.generate_array_float32((4096, 4096), units=u.DN),
        "dq": random_utils.generate_array_uint32((4096, 4096)),
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
        "data": random_utils.generate_array_float32((4096, 4096)),
        "dq": random_utils.generate_array_uint32((4096, 4096)),
        "err": random_utils.generate_array_float32((4096, 4096)),
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
        "F062": {
            "photmjsr": (1.0e-15 * np.random.random() * u.megajansky / u.steradian),
            "uncertainty": (1.0e-16 * np.random.random() * u.megajansky / u.steradian),
            "pixelareasr": 1.0e-13 * u.steradian,
        },
        "F087": {
            "photmjsr": (1.0e-15 * np.random.random() * u.megajansky / u.steradian),
            "uncertainty": (1.0e-16 * np.random.random() * u.megajansky / u.steradian),
            "pixelareasr": 1.0e-13 * u.steradian,
        },
        "F106": {
            "photmjsr": (1.0e-15 * np.random.random() * u.megajansky / u.steradian),
            "uncertainty": (1.0e-16 * np.random.random() * u.megajansky / u.steradian),
            "pixelareasr": 1.0e-13 * u.steradian,
        },
        "F129": {
            "photmjsr": (1.0e-15 * np.random.random() * u.megajansky / u.steradian),
            "uncertainty": (1.0e-16 * np.random.random() * u.megajansky / u.steradian),
            "pixelareasr": 1.0e-13 * u.steradian,
        },
        "F146": {
            "photmjsr": (1.0e-15 * np.random.random() * u.megajansky / u.steradian),
            "uncertainty": (1.0e-16 * np.random.random() * u.megajansky / u.steradian),
            "pixelareasr": 1.0e-13 * u.steradian,
        },
        "F158": {
            "photmjsr": (1.0e-15 * np.random.random() * u.megajansky / u.steradian),
            "uncertainty": (1.0e-16 * np.random.random() * u.megajansky / u.steradian),
            "pixelareasr": 1.0e-13 * u.steradian,
        },
        "F184": {
            "photmjsr": (1.0e-15 * np.random.random() * u.megajansky / u.steradian),
            "uncertainty": (1.0e-16 * np.random.random() * u.megajansky / u.steradian),
            "pixelareasr": 1.0e-13 * u.steradian,
        },
        "F213": {
            "photmjsr": (1.0e-15 * np.random.random() * u.megajansky / u.steradian),
            "uncertainty": (1.0e-16 * np.random.random() * u.megajansky / u.steradian),
            "pixelareasr": 1.0e-13 * u.steradian,
        },
        "GRISM": {"photmjsr": None, "uncertainty": None, "pixelareasr": 1.0e-13 * u.steradian},
        "PRISM": {"photmjsr": None, "uncertainty": None, "pixelareasr": 1.0e-13 * u.steradian},
        "DARK": {"photmjsr": None, "uncertainty": None, "pixelareasr": 1.0e-13 * u.steradian},
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
        "data_end": random_utils.generate_mjd_timestamp(),
        "data_start": random_utils.generate_mjd_timestamp(),
        "gs_ctd_ux": random_utils.generate_positive_float(),
        "gs_ctd_uy": random_utils.generate_positive_float(),
        "gs_ctd_x": random_utils.generate_positive_float(),
        "gs_ctd_y": random_utils.generate_positive_float(),
        "gs_dec": random_utils.generate_float(math.pi / -2.0, math.pi / 2.0),
        "gs_epoch": random_utils.generate_string("Epoch ", 10),
        "gs_mag": random_utils.generate_float(),
        "gs_mudec": random_utils.generate_float(),
        "gs_mura": random_utils.generate_float(),
        "gs_para": random_utils.generate_float(),
        "gs_ra": random_utils.generate_angle_radians(),
        "gs_udec": random_utils.generate_positive_float(),
        "gs_umag": random_utils.generate_positive_float(),
        "gs_ura": random_utils.generate_positive_float(),
        "gw_id": random_utils.generate_string("ID ", 20),
        "gw_fgs_mode": "WSM-ACQ-2",
        "gs_id": random_utils.generate_string("GS ", 20),
        "gs_catalog_version": random_utils.generate_string("GSC", 20),
        "gw_window_xsize": 16,
        "gw_window_xstart": random_utils.generate_positive_int(4000),
        "gw_window_ysize": 16,
        "gw_window_ystart": random_utils.generate_positive_int(4000),
        "gs_pattern_error": random_utils.generate_positive_float(),
    }
    raw["gw_window_xstop"] = raw["gw_window_xstart"] + 16
    raw["gw_window_ystop"] = raw["gw_window_ystart"] + 16
    raw.update(kwargs)

    return stnode.Guidestar(raw)


def create_file_date(**kwargs):
    return stnode.FileDate(kwargs.get("file_date", random_utils.generate_astropy_time()))


def create_calibration_software_version(**kwargs):
    return stnode.CalibrationSoftwareVersion(
        kwargs.get("calibration_sofware_version", random_utils.generate_string("Version ", 120))
    )


def create_filename(**kwargs):
    return stnode.Filename(kwargs.get("filename", random_utils.generate_string("Filename ", 120)))


def create_model_type(**kwargs):
    return stnode.ModelType(kwargs.get("model_type", random_utils.generate_string("Model type ", 50)))


def create_origin(**kwargs):
    return stnode.Origin(kwargs.get("origin", "STSCI"))


def create_prd_software_version(**kwargs):
    return stnode.PrdSoftwareVersion(kwargs.get("prd_software_version", random_utils.generate_string("S&OC PRD ", 120)))


def create_sdf_software_version(**kwargs):
    return stnode.SdfSoftwareVersion(kwargs.get("sdf_software_version", random_utils.generate_software_version()))


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
        "crds_context_used": f"roman_{random_utils.generate_positive_int(9999):04d}.pmap",
        "crds_software_version": random_utils.generate_software_version(),
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
        "execution_plan": random_utils.generate_positive_int(),
        "exposure": random_utils.generate_positive_int(),
        "obs_id": random_utils.generate_string("Obs ID ", 26),
        "observation": random_utils.generate_positive_int(),
        "observation_label": random_utils.generate_string("Observation label "),
        "pass": random_utils.generate_positive_int(),
        "program": str(random_utils.generate_positive_int()),
        "segment": random_utils.generate_positive_int(),
        "survey": random_utils.generate_choice("HLS", "EMS", "SN", "N/A"),
        "template": random_utils.generate_string("Template ", 50),
        "visit": random_utils.generate_positive_int(),
        "visit_file_activity": random_utils.generate_string(max_length=2),
        "visit_file_group": random_utils.generate_positive_int(),
        "visit_file_sequence": random_utils.generate_positive_int(),
        "visit_id": random_utils.generate_string("Visit ID ", 19),
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
        "conversion_megajanskys": random_utils.generate_positive_float() * u.MJy / u.sr,
        "conversion_microjanskys": random_utils.generate_positive_float() * u.uJy / u.sr,
        "pixelarea_arcsecsq": random_utils.generate_positive_float() * u.arcsec**2,
        "pixelarea_steradians": random_utils.generate_positive_float() * u.sr,
        "conversion_megajanskys_uncertainty": random_utils.generate_positive_float() * u.MJy / u.sr,
        "conversion_microjanskys_uncertainty": random_utils.generate_positive_float() * u.uJy / u.sr,
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
        "area": random_utils.generate_array_float32(min=0.0),
    }
    raw.update(kwargs)
    raw["meta"] = {}
    raw["meta"]["photometry"] = {"pixelarea_steradians": 0.3 * u.sr, "pixelarea_arcsecsq": 0.3 * u.arcsec**2}

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
        "dec_v1": random_utils.generate_float(-90.0, 90.0),
        "pa_v3": random_utils.generate_angle_degrees(),
        "ra_v1": random_utils.generate_angle_degrees(),
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
        "category": random_utils.generate_string("Cat ", 6),
        "continuation_id": random_utils.generate_positive_int(),
        "pi_name": random_utils.generate_string("PI name ", 100),
        "science_category": random_utils.generate_string("Science category ", 100),
        "subcategory": random_utils.generate_string("Subcategory ", 15),
        "title": random_utils.generate_string("Proposal title ", 100),
    }
    raw.update(kwargs)

    return stnode.Program(raw)


def create_resample(**kwargs):
    """
    Create a dummy Resample instance with valid values for attributes
    required by the schema.

    Parameters
    ----------
    **kwargs
        Additional or overridden attributes.

    Returns
    -------
    roman_datamodels.stnode.Resample
    """
    raw = {
        "pixel_scale_ratio": random_utils.generate_positive_float(),
        "pixfrac": random_utils.generate_positive_float(),
        "pointings": random_utils.generate_positive_int(),
        "product_exposure_time": random_utils.generate_positive_float(),
        "weight_type": random_utils.generate_choice("exptime", "ivm"),
    }
    raw.update(kwargs)

    return stnode.Resample(raw)


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
        "data": random_utils.generate_array_float32((2, 4096, 4096), units=u.electron),
        "pixeldq": random_utils.generate_array_uint32((4096, 4096)),
        "groupdq": random_utils.generate_array_uint8((2, 4096, 4096)),
        "err": random_utils.generate_array_float32(size=(2, 4096, 4096), min=0.0, units=u.electron),
        "amp33": random_utils.generate_array_uint16((2, 4096, 128), units=u.DN),
        "border_ref_pix_right": random_utils.generate_array_float32((2, 4096, 4), units=u.DN),
        "border_ref_pix_left": random_utils.generate_array_float32((2, 4096, 4), units=u.DN),
        "border_ref_pix_top": random_utils.generate_array_float32((2, 4, 4096), units=u.DN),
        "border_ref_pix_bottom": random_utils.generate_array_float32((2, 4, 4096), units=u.DN),
        "dq_border_ref_pix_right": random_utils.generate_array_uint32((4096, 4)),
        "dq_border_ref_pix_left": random_utils.generate_array_uint32((4096, 4)),
        "dq_border_ref_pix_top": random_utils.generate_array_uint32((4, 4096)),
        "dq_border_ref_pix_bottom": random_utils.generate_array_uint32((4, 4096)),
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
        "slope": random_utils.generate_array_float32(seg_shape, units=u.electron / u.s),
        "sigslope": random_utils.generate_array_float32(seg_shape, units=u.electron / u.s),
        "yint": random_utils.generate_array_float32(seg_shape, units=u.electron),
        "sigyint": random_utils.generate_array_float32(seg_shape, units=u.electron),
        "pedestal": random_utils.generate_array_float32(seg_shape[1:], units=u.electron),
        "weights": random_utils.generate_array_float32(seg_shape),
        "crmag": random_utils.generate_array_float32(seg_shape, units=u.electron),
        "var_poisson": random_utils.generate_array_float32(seg_shape, units=u.electron**2 / u.s**2),
        "var_rnoise": random_utils.generate_array_float32(seg_shape, units=u.electron**2 / u.s**2),
    }
    raw.update(kwargs)

    return stnode.RampFitOutput(raw)


def create_source_detection(**kwargs):
    """
    Create a dummy SourceDetection instance with valid values for attributes
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
        "tweakreg_catalog_name": "filename_catalog.asdf",
    }
    raw.update(kwargs)

    return stnode.SourceDetection(raw)


def create_associations(**kwargs):
    """
    Create a dummy Association table instance (or file) with table and valid values for attributes
    required by the schema.
    Parameters
    ----------
    **kwargs
        Additional or overridden attributes.
    Returns
    -------
    roman_datamodels.stnode.Associations
    """

    raw = {
        #        "meta": create_meta(),
    }
    raw.update(kwargs)

    raw["asn_type"] = "image"
    raw["asn_rule"] = "candidate_Asn_Lv2Image_i2d"
    raw["version_id"] = "null"
    raw["code_version"] = "0.16.2.dev16+g640b0b79"
    raw["degraded_status"] = "No known degraded exposures in association."
    raw["program"] = 1
    raw["constraints"] = (
        "DMSAttrConstraint({'name': 'program', 'sources': ['program'], "
        "'value': '001'})\nConstraint_TargetAcq({'name': 'target_acq', 'value': "
        "'target_acquisition'})\nDMSAttrConstraint({'name': 'science', "
        "'DMSAttrConstraint({'name': 'asn_candidate','sources': "
        "['asn_candidate'], 'value': \"\\\\('o036',\\\\ 'observation'\\\\)\"})"
    )
    raw["asn_id"] = "o036"
    raw["asn_pool"] = "r00001_20200530t023154_pool"
    raw["target"] = 16

    length = 7

    exptypes = random_utils.generate_choices(["SCIENCE", "CALIBRATION", "ENGINEERING"], k=length)
    exposerr = ["null"] * length
    expname = ["file_" + str(x) + ".asdf" for x in range(length)]

    raw["products"] = []
    raw["products"].append(
        {
            "name": "product0",
            "members": [
                {"expname": expname[0], "exposerr": exposerr[0], "exptype": exptypes[0]},
                {"expname": expname[1], "exposerr": exposerr[1], "exptype": exptypes[1]},
            ],
        }
    )
    raw["products"].append(
        {"name": "product1", "members": [{"expname": expname[2], "exposerr": exposerr[2], "exptype": exptypes[2]}]}
    )
    raw["products"].append(
        {
            "name": "product1",
            "members": [
                {"expname": expname[3], "exposerr": exposerr[3], "exptype": exptypes[3]},
                {"expname": expname[4], "exposerr": exposerr[4], "exptype": exptypes[4]},
                {"expname": expname[5], "exposerr": exposerr[5], "exptype": exptypes[5]},
            ],
        }
    )

    return stnode.Associations(raw)


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
        "pedestal_frames": random_utils.generate_array_uint16(seg_shape, units=u.DN),
        "signal_frames": random_utils.generate_array_uint16(seg_shape, units=u.DN),
        "amp33": random_utils.generate_array_uint16(seg_shape, units=u.DN),
    }
    raw.update(kwargs)

    raw["meta"]["file_creation_time"] = random_utils.generate_astropy_time()
    raw["meta"]["gw_start_time"] = random_utils.generate_astropy_time()
    raw["meta"]["gw_end_time"] = random_utils.generate_astropy_time()
    raw["meta"]["gw_function_start_time"] = random_utils.generate_astropy_time()
    raw["meta"]["gw_function_end_time"] = random_utils.generate_astropy_time()
    raw["meta"]["gw_frame_readout_time"] = random_utils.generate_float()
    raw["meta"]["pedestal_resultant_exp_time"] = random_utils.generate_float()
    raw["meta"]["signal_resultant_exp_time"] = random_utils.generate_float()
    raw["meta"]["gw_acq_number"] = random_utils.generate_int()
    raw["meta"]["gw_science_file_source"] = "filename"
    raw["meta"]["gw_mode"] = "WIM-ACQ"
    raw["meta"]["gw_window_xstart"] = random_utils.generate_positive_int(4000)
    raw["meta"]["gw_window_ystart"] = random_utils.generate_positive_int(4000)
    raw["meta"]["gw_window_xstop"] = raw["meta"]["gw_window_xstart"] + 16
    raw["meta"]["gw_window_ystop"] = raw["meta"]["gw_window_ystart"] + 16
    raw["meta"]["gw_window_xsize"] = 16
    raw["meta"]["gw_window_ysize"] = 16
    raw["meta"]["gw_acq_exec_stat"] = random_utils.generate_string("Status ", 15)

    raw["meta"]["gw_acq_exec_stat"] = random_utils.generate_string("Status ", 15)
    raw["meta"]["gw_function_end_time"] = random_utils.generate_astropy_time()
    raw["meta"]["gw_function_start_time"] = random_utils.generate_astropy_time()

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
        "catalog_name": random_utils.generate_string("Catalog name ", 256),
        "dec": random_utils.generate_float(-90.0, 90.0),
        "dec_uncertainty": random_utils.generate_positive_float(),
        "proper_motion_dec": random_utils.generate_float(),
        "proper_motion_epoch": random_utils.generate_string_timestamp(),
        "proper_motion_ra": random_utils.generate_float(),
        "proposer_dec": random_utils.generate_float(-90.0, 90.0),
        "proposer_name": random_utils.generate_string("Proposer name ", 100),
        "proposer_ra": random_utils.generate_angle_degrees(),
        "ra": random_utils.generate_angle_degrees(),
        "ra_uncertainty": random_utils.generate_positive_float(),
        "source_type": random_utils.generate_choice("EXTENDED", "POINT", "UNKNOWN"),
        "type": random_utils.generate_choice("FIXED", "MOVING", "GENERIC"),
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
        "ra_offset": random_utils.generate_float(),
        "dec_offset": random_utils.generate_float(),
        "scale_factor": random_utils.generate_float(),
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
        "engineering_quality": random_utils.generate_choice("OK", "SUSPECT"),
        "pointing_engdb_quality": random_utils.generate_choice("CALCULATED", "PLANNED"),
        "type": random_utils.generate_string("Visit type ", 30),
        "start_time": random_utils.generate_astropy_time(),
        "end_time": random_utils.generate_astropy_time(),
        "status": random_utils.generate_string("Status ", 15),
        "total_exposures": random_utils.generate_positive_int(),
        "internal_target": random_utils.generate_bool(),
        "target_of_opportunity": random_utils.generate_bool(),
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
        "dec_ref": random_utils.generate_float(-90.0, 90.0),
        "ra_ref": random_utils.generate_positive_float(360.0),
        "roll_ref": random_utils.generate_float(),
        "s_region": random_utils.generate_string("Spatial extent "),
        "v2_ref": random_utils.generate_float(),
        "v3_ref": random_utils.generate_float(),
        "v3yangle": random_utils.generate_float(),
        "vparity": random_utils.generate_int(),
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
        "data": random_utils.generate_array_float32((4088, 4088), units=u.electron / u.s),
        "dq": random_utils.generate_array_uint32((4088, 4088)),
        "err": random_utils.generate_array_float32((4088, 4088), min=0.0, units=u.electron / u.s),
        "meta": create_meta(),
        "var_flat": random_utils.generate_array_float32((4088, 4088), units=u.electron**2 / u.s**2),
        "var_poisson": random_utils.generate_array_float32((4088, 4088), units=u.electron**2 / u.s**2),
        "var_rnoise": random_utils.generate_array_float32((4088, 4088), units=u.electron**2 / u.s**2),
        "amp33": random_utils.generate_array_uint16((2, 4096, 128), units=u.DN),
        "border_ref_pix_right": random_utils.generate_array_float32((2, 4096, 4), units=u.DN),
        "border_ref_pix_left": random_utils.generate_array_float32((2, 4096, 4), units=u.DN),
        "border_ref_pix_top": random_utils.generate_array_float32((2, 4, 4096), units=u.DN),
        "border_ref_pix_bottom": random_utils.generate_array_float32((2, 4, 4096), units=u.DN),
        "dq_border_ref_pix_right": random_utils.generate_array_uint32((4096, 4)),
        "dq_border_ref_pix_left": random_utils.generate_array_uint32((4096, 4)),
        "dq_border_ref_pix_top": random_utils.generate_array_uint32((4, 4096)),
        "dq_border_ref_pix_bottom": random_utils.generate_array_uint32((4, 4096)),
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
        "detector": random_utils.generate_detector(),
        "name": "WFI",
        "optical_element": random_utils.generate_optical_element(),
    }
    raw.update(kwargs)

    return stnode.WfiMode(raw)


def create_wfi_mosaic(**kwargs):
    """
    Create a dummy WfiMosaic instance with valid values for attributes
    required by the schema.

    Parameters
    ----------
    **kwargs
        Additional or overridden attributes.

    Returns
    -------
    roman_datamodels.stnode.WfiIMosaic
    """

    raw = {
        "data": random_utils.generate_array_float32((4088, 4088), units=u.electron / u.s),
        "err": random_utils.generate_array_float32((4088, 4088), min=0.0, units=u.electron / u.s),
        "context": random_utils.generate_array_uint32((2, 4088, 4088)),
        "weight": random_utils.generate_array_float32((4088, 4088)),
        "var_poisson": random_utils.generate_array_float32((4088, 4088), units=u.electron**2 / u.s**2),
        "var_rnoise": random_utils.generate_array_float32((4088, 4088), units=u.electron**2 / u.s**2),
        "var_flat": random_utils.generate_array_float32((4088, 4088), units=u.electron**2 / u.s**2),
        "cal_logs": create_cal_logs(),
        "meta": create_meta(),
    }
    raw.update(kwargs)
    raw["meta"]["photometry"] = create_photometry()
    raw["meta"]["resample"] = create_resample()

    return stnode.WfiMosaic(raw)


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
        "data": random_utils.generate_array_uint16((2, 4096, 4096), units=u.DN),
        "amp33": random_utils.generate_array_uint16((2, 4096, 128), units=u.DN),
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
    `roman_datamodels.stnode.TaggedObjectNode`
    """
    method_name = "create_" + _camel_case_to_snake_case(node_class.__name__)
    if method_name not in globals():
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
    reftypes = ["dark", "distortion", "flat", "gain", "linearity", "mask", "readnoise", "saturation", "photom"]
    val = "N/A"
    raw = dict(zip(reftypes, [val] * len(reftypes)))
    raw["crds"] = {"sw_version": "12.1", "context_used": "781"}
    raw.update(kwargs)

    return stnode.RefFile(raw)
