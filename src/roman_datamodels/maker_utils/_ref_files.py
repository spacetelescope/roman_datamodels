import warnings

import numpy as np
from astropy.modeling import models

from roman_datamodels import stnode

from ._base import MESSAGE, NONUM, NOSTR, save_node
from ._common_meta import (
    mk_ref_common,
    mk_ref_dark_meta,
    mk_ref_distoriton_meta,
    mk_ref_epsf_meta,
    mk_ref_pixelarea_meta,
    mk_ref_readnoise_meta,
    mk_ref_skycells_meta,
    mk_ref_units_dn_meta,
)

__all__ = [
    "mk_abvegaoffset",
    "mk_apcorr",
    "mk_dark",
    "mk_distortion",
    "mk_epsf",
    "mk_flat",
    "mk_gain",
    "mk_inverselinearity",
    "mk_ipc",
    "mk_linearity",
    "mk_mask",
    "mk_matable",
    "mk_pixelarea",
    "mk_readnoise",
    "mk_refpix",
    "mk_saturation",
    "mk_skycells",
    "mk_superbias",
    "mk_wfi_img_photom",
]

OPT_ELEM = ("F062", "F087", "F106", "F129", "F146", "F158", "F184", "F213", "GRISM", "PRISM", "DARK")


def mk_ref_abvegaoffset_data(**kwargs):
    """
    Create dummy data for AB Vega Offset reference file instances.

    Returns
    -------
    dict
    """
    data = {}
    for optical_elem in OPT_ELEM:
        data[optical_elem] = {}
        data[optical_elem]["abvega_offset"] = kwargs.get(optical_elem, {}).get("abvega_offset", float(NONUM))

    return data


def mk_abvegaoffset(*, filepath=None, **kwargs):
    """
    Create a dummy AB Vega Offset instance (or file) with valid values
    for attributes required by the schema.

    Parameters
    ----------
    filepath
        (optional, keyword-only) File name and path to write model to.

    Returns
    -------
    roman_datamodels.stnode.AbvegaoffsetRef
    """
    abvegaref = stnode.AbvegaoffsetRef()
    abvegaref["meta"] = mk_ref_common("ABVEGAOFFSET", **kwargs.get("meta", {}))
    abvegaref["data"] = mk_ref_abvegaoffset_data(**kwargs.get("data", {}))

    return save_node(abvegaref, filepath=filepath)


def mk_ref_apcorr_data(shape=(10,), **kwargs):
    """
    Create dummy data for Aperture Correction reference file instances.

    Parameters
    ----------
    shape
        (optional, keyword-only) Shape of arrays in the model.
        If shape is greater than 1D, the first dimension is used.

    Returns
    -------
    dict
    """
    if len(shape) > 1:
        shape = shape[:1]

        warnings.warn(f"{MESSAGE} assuming the first entry. The remaining are thrown out!", UserWarning, stacklevel=2)

    data = {}
    for optical_elem in OPT_ELEM:
        data[optical_elem] = {}
        data[optical_elem]["ap_corrections"] = kwargs.get(optical_elem, {}).get(
            "ap_corrections", np.zeros(shape, dtype=np.float64)
        )
        data[optical_elem]["ee_fractions"] = kwargs.get(optical_elem, {}).get("ee_fractions", np.zeros(shape, dtype=np.float64))
        data[optical_elem]["ee_radii"] = kwargs.get(optical_elem, {}).get("ee_radii", np.zeros(shape, dtype=np.float64))
        data[optical_elem]["sky_background_rin"] = kwargs.get(optical_elem, {}).get("sky_background_rin", float(NONUM))
        data[optical_elem]["sky_background_rout"] = kwargs.get(optical_elem, {}).get("sky_background_rout", float(NONUM))

    return data


def mk_apcorr(*, shape=(10,), filepath=None, **kwargs):
    """
    Create a dummy Aperture Correction instance (or file) with arrays and valid values
    for attributes required by the schema.

    Parameters
    ----------
    shape
        (optional, keyword-only) Shape of arrays in the model.
        If shape is greater than 1D, the first dimension is used.

    filepath
        (optional, keyword-only) File name and path to write model to.

    Returns
    -------
    roman_datamodels.stnode.ApcorrRef
    """
    if len(shape) > 1:
        shape = shape[:1]

        warnings.warn(f"{MESSAGE} assuming the first entry. The remaining is thrown out!", UserWarning, stacklevel=2)

    apcorrref = stnode.ApcorrRef()
    apcorrref["meta"] = mk_ref_common("APCORR", **kwargs.get("meta", {}))
    apcorrref["data"] = mk_ref_apcorr_data(shape, **kwargs.get("data", {}))

    return save_node(apcorrref, filepath=filepath)


def mk_flat(*, shape=(4096, 4096), filepath=None, **kwargs):
    """
    Create a dummy Flat instance (or file) with arrays and valid values for
    attributes required by the schema.

    Parameters
    ----------
    shape
        (optional, keyword-only) Shape of arrays in the model.
        If shape is greater than 2D, the first two dimensions are used.

    filepath
        (optional, keyword-only) File name and path to write model to.

    Returns
    -------
    roman_datamodels.stnode.FlatRef
    """
    if len(shape) > 2:
        shape = shape[:2]

        warnings.warn(f"{MESSAGE} assuming the first two entries. The remaining is thrown out!", UserWarning, stacklevel=2)

    flatref = stnode.FlatRef()
    flatref["meta"] = mk_ref_common("FLAT", **kwargs.get("meta", {}))

    flatref["data"] = kwargs.get("data", np.zeros(shape, dtype=np.float32))
    flatref["dq"] = kwargs.get("dq", np.zeros(shape, dtype=np.uint32))
    flatref["err"] = kwargs.get("err", np.zeros(shape, dtype=np.float32))

    return save_node(flatref, filepath=filepath)


def mk_dark(*, shape=(2, 4096, 4096), filepath=None, **kwargs):
    """
    Create a dummy Dark Current instance (or file) with arrays and valid values
    for attributes required by the schema.

    Parameters
    ----------
    shape
        (optional, keyword-only) Shape of arrays in the model.

    filepath
        (optional, keyword-only) File name and path to write model to.

    Returns
    -------
    roman_datamodels.stnode.DarkRef
    """
    if len(shape) != 3:
        shape = (2, 4096, 4096)
        warnings.warn("Input shape must be 3D. Defaulting to (2, 4096, 4096)", UserWarning, stacklevel=2)

    darkref = stnode.DarkRef()
    darkref["meta"] = mk_ref_dark_meta(**kwargs.get("meta", {}))

    darkref["dq"] = kwargs.get("dq", np.zeros(shape[1:], dtype=np.uint32))
    darkref["dark_slope"] = kwargs.get("dark_slope", np.zeros(shape[1:], dtype=np.float32))
    darkref["dark_slope_error"] = kwargs.get("dark_slope_error", np.zeros(shape[1:], dtype=np.float32))

    return save_node(darkref, filepath=filepath)


def mk_distortion(*, filepath=None, **kwargs):
    """
    Create a dummy Distortion instance (or file) with arrays and valid values
    for attributes required by the schema.

    Parameters
    ----------

    filepath
        (optional, keyword-only) File name and path to write model to.

    Returns
    -------
    roman_datamodels.stnode.DistortionRef
    """
    distortionref = stnode.DistortionRef()
    distortionref["meta"] = mk_ref_distoriton_meta(**kwargs.get("meta", {}))

    distortionref["coordinate_distortion_transform"] = kwargs.get(
        "coordinate_distortion_transform", models.Shift(1) & models.Shift(2)
    )

    return save_node(distortionref, filepath=filepath)


def mk_epsf(*, shape=(3, 6, 9, 361, 361), filepath=None, **kwargs):
    """
    Create a dummy ePSF instance (or file) with arrays and valid values
    for attributes required by the schema.

    Parameters
    ----------
    shape
        (optional, keyword-only) Shape of arrays in the model.
        If shape is greater than 1D, the first dimension is used.

    filepath
        (optional, keyword-only) File name and path to write model to.

    Returns
    -------
    roman_datamodels.stnode.EpsfRef
    """
    if len(shape) != 5:
        shape = (3, 6, 9, 361, 361)
        warnings.warn("Input shape must be 5D. Defaulting to (3, 6, 9, 361, 361)", UserWarning, stacklevel=2)

    epsfref = stnode.EpsfRef()
    epsfref["meta"] = mk_ref_epsf_meta(**kwargs.get("meta", {}))

    epsfref["psf"] = kwargs.get("psf", np.zeros(shape, dtype=np.float32))
    epsfref["extended_psf"] = kwargs.get("extended_psf", np.zeros(shape[-2:], dtype=np.float32))

    return save_node(epsfref, filepath=filepath)


def mk_gain(*, shape=(4096, 4096), filepath=None, **kwargs):
    """
    Create a dummy Gain instance (or file) with arrays and valid values for
    attributes required by the schema.

    Parameters
    ----------
    shape
        (optional, keyword-only) Shape of arrays in the model.
        If shape is greater than 2D, the first two dimensions are used.

    filepath
        (optional, keyword-only) File name and path to write model to.

    Returns
    -------
    roman_datamodels.stnode.GainRef
    """
    if len(shape) > 2:
        shape = shape[:2]

        warnings.warn(f"{MESSAGE} assuming the first two entries. The remaining is thrown out!", UserWarning, stacklevel=2)

    gainref = stnode.GainRef()
    gainref["meta"] = mk_ref_common("GAIN", **kwargs.get("meta", {}))

    gainref["data"] = kwargs.get("data", np.zeros(shape, dtype=np.float32))

    return save_node(gainref, filepath=filepath)


def mk_ipc(*, shape=(3, 3), filepath=None, **kwargs):
    """
    Create a dummy IPC instance (or file) with arrays and valid values for
    attributes required by the schema.

    Parameters
    ----------
    shape
        (optional, keyword-only) Shape of array in the model.
        If shape is greater than 2D, the first two dimensions are used.

    filepath
        (optional, keyword-only) File name and path to write model to.

    Returns
    -------
    roman_datamodels.stnode.IpcRef
    """
    if len(shape) > 2:
        shape = shape[:2]

        warnings.warn(f"{MESSAGE} assuming the first two entries. The remaining is thrown out!", UserWarning, stacklevel=2)

    ipcref = stnode.IpcRef()
    ipcref["meta"] = mk_ref_common("IPC", **kwargs.get("meta", {}))

    if "data" in kwargs:
        ipcref["data"] = kwargs["data"]
    else:
        ipcref["data"] = np.zeros(shape, dtype=np.float32)
        ipcref["data"][int(np.floor(shape[0] / 2))][int(np.floor(shape[1] / 2))] = 1.0

    return save_node(ipcref, filepath=filepath)


def mk_linearity(*, shape=(2, 4096, 4096), filepath=None, **kwargs):
    """
    Create a dummy Linearity instance (or file) with arrays and valid values for
    attributes required by the schema.

    Parameters
    ----------
    shape
        (optional, keyword-only) Shape of arrays in the model.

    filepath
        (optional, keyword-only) File name and path to write model to.

    Returns
    -------
    roman_datamodels.stnode.LinearityRef
    """
    if len(shape) != 3:
        shape = (2, 4096, 4096)
        warnings.warn("Input shape must be 3D. Defaulting to (2, 4096, 4096)", UserWarning, stacklevel=2)

    linearityref = stnode.LinearityRef()
    linearityref["meta"] = mk_ref_units_dn_meta("LINEARITY", **kwargs.get("meta", {}))

    linearityref["dq"] = kwargs.get("dq", np.zeros(shape[1:], dtype=np.uint32))
    linearityref["coeffs"] = kwargs.get("coeffs", np.zeros(shape, dtype=np.float32))

    return save_node(linearityref, filepath=filepath)


def mk_inverselinearity(*, shape=(2, 4096, 4096), filepath=None, **kwargs):
    """
    Create a dummy InverseLinearity instance (or file) with arrays and valid
    values for attributes required by the schema.

    Parameters
    ----------
    shape
        (optional, keyword-only) Shape of arrays in the model.

    filepath
        (optional, keyword-only) File name and path to write model to.

    Returns
    -------
    roman_datamodels.stnode.InverseLinearityRef
    """
    if len(shape) != 3:
        shape = (2, 4096, 4096)
        warnings.warn("Input shape must be 3D. Defaulting to (2, 4096, 4096)", UserWarning, stacklevel=2)

    inverselinearityref = stnode.InverselinearityRef()
    inverselinearityref["meta"] = mk_ref_units_dn_meta("INVERSELINEARITY", **kwargs.get("meta", {}))

    inverselinearityref["dq"] = kwargs.get("dq", np.zeros(shape[1:], dtype=np.uint32))
    inverselinearityref["coeffs"] = kwargs.get("coeffs", np.zeros(shape, dtype=np.float32))

    return save_node(inverselinearityref, filepath=filepath)


def mk_mask(*, shape=(4096, 4096), filepath=None, **kwargs):
    """
    Create a dummy Mask instance (or file) with arrays and valid values for
    attributes required by the schema.

    Parameters
    ----------
    shape
        (optional, keyword-only) Shape of arrays in the model.
        If shape is greater than 2D, the first two dimensions are used.

    filepath
        (optional, keyword-only) File name and path to write model to.

    Returns
    -------
    roman_datamodels.stnode.MaskRef
    """
    if len(shape) > 2:
        shape = shape[:2]

        warnings.warn(f"{MESSAGE} assuming the first two entries. The remaining is thrown out!", UserWarning, stacklevel=2)

    maskref = stnode.MaskRef()
    maskref["meta"] = mk_ref_common("MASK", **kwargs.get("meta", {}))

    maskref["dq"] = kwargs.get("dq", np.zeros(shape, dtype=np.uint32))

    return save_node(maskref, filepath=filepath)


def mk_ref_matable_guide_window_tables(table_ids=None, **kwargs):
    """
    Create dummy data for MA Table Guide Window table instances.

    Parameters
    ----------
    table_ids
        list of integer IDs of the MA Tables

    Returns
    -------
    dictionary of dictionaries
    """
    if table_ids is None:
        if "guide_window_tables" in kwargs.keys():
            table_ids = kwargs["guide_window_tables"].keys()
        else:
            table_ids = []
            for idx in range(1, 11):
                table_ids.append(f"GW{idx:04}")

    guide_window_tables = {}
    for gw_idx in table_ids:
        if "guide_window_tables" in kwargs.keys():
            kwarg_idx = kwargs["guide_window_tables"][gw_idx]
        else:
            kwarg_idx = {}
        guide_window_tables[gw_idx] = {}
        guide_window_tables[gw_idx]["effective_pedestal_exposure_time"] = kwarg_idx.get("effective_pedestal_exposure_time", NONUM)
        guide_window_tables[gw_idx]["effective_signal_exposure_time"] = kwarg_idx.get("effective_signal_exposure_time", NONUM)
        guide_window_tables[gw_idx]["gw_readout_time"] = kwarg_idx.get("gw_readout_time", NONUM)
        guide_window_tables[gw_idx]["ma_table_description"] = kwarg_idx.get("ma_table_description", NOSTR)
        guide_window_tables[gw_idx]["ma_table_name"] = kwarg_idx.get("ma_table_name", NOSTR)
        guide_window_tables[gw_idx]["ma_table_number"] = kwarg_idx.get("ma_table_number", NONUM)
        guide_window_tables[gw_idx]["fsw_slot_number"] = kwarg_idx.get("fsw_slot_number", NONUM)
        guide_window_tables[gw_idx]["num_gw_columns"] = kwarg_idx.get("num_gw_columns", NONUM)
        guide_window_tables[gw_idx]["num_gw_rows"] = kwarg_idx.get("num_gw_rows", NONUM)
        guide_window_tables[gw_idx]["num_pedestal_reads"] = kwarg_idx.get("num_pedestal_reads", NONUM)
        guide_window_tables[gw_idx]["num_pre_pedestal_reset_reads"] = kwarg_idx.get("num_pre_pedestal_reset_reads", NONUM)
        guide_window_tables[gw_idx]["num_pre_signal_skips"] = kwarg_idx.get("num_pre_signal_skips", NONUM)
        guide_window_tables[gw_idx]["num_signal_reads"] = kwarg_idx.get("num_signal_reads", NONUM)
        guide_window_tables[gw_idx]["science_block_size"] = kwarg_idx.get("science_block_size", NONUM)

    return guide_window_tables


def mk_ref_matable_science_tables(table_ids=None, length=10, **kwargs):
    """
    Create dummy data for MA Table Science table instances.

    Parameters
    ----------
    table_ids
        list of integer IDs of the MA Tables

    length
        (optional, keyword-only) Length of lists in the model.

    Returns
    -------
    dictionary of dictionaries
    """
    if table_ids is None:
        if "science_tables" in kwargs.keys():
            table_ids = kwargs["science_tables"].keys()
        else:
            table_ids = []
            for idx in range(1, 11):
                table_ids.append(f"SCI{idx:04}")

    science_tables = {}
    for sci_idx in table_ids:
        if "science_tables" in kwargs.keys():
            kwarg_idx = kwargs["science_tables"][sci_idx]
        else:
            kwarg_idx = {}
        science_tables[sci_idx] = {}
        science_tables[sci_idx]["accumulated_exposure_time"] = kwarg_idx.get(
            "accumulated_exposure_time", np.arange(1, length + 1, dtype=np.float32).tolist()
        )
        science_tables[sci_idx]["effective_exposure_time"] = kwarg_idx.get(
            "effective_exposure_time", np.arange(1, length + 1, dtype=np.float32).tolist()
        )
        science_tables[sci_idx]["frame_time"] = kwarg_idx.get("frame_time", NONUM)
        science_tables[sci_idx]["integration_duration"] = kwarg_idx.get(
            "integration_duration", np.arange(1, length + 1, dtype=np.float32).tolist()
        )
        science_tables[sci_idx]["ma_table_description"] = kwarg_idx.get("ma_table_description", NOSTR)
        science_tables[sci_idx]["ma_table_name"] = kwarg_idx.get("ma_table_name", NOSTR)
        science_tables[sci_idx]["ma_table_number"] = kwarg_idx.get("ma_table_number", NONUM)
        science_tables[sci_idx]["fsw_slot_number"] = kwarg_idx.get("fsw_slot_number", NONUM)
        science_tables[sci_idx]["min_science_resultants"] = kwarg_idx.get("min_science_resultants", NONUM)
        science_tables[sci_idx]["num_pre_science_reads"] = kwarg_idx.get("num_pre_science_reads", NONUM)
        science_tables[sci_idx]["num_pre_science_resultants"] = kwarg_idx.get("num_pre_science_resultants", NONUM)
        science_tables[sci_idx]["num_science_resultants"] = kwarg_idx.get("num_science_resultants", NONUM)
        science_tables[sci_idx]["observing_mode"] = kwarg_idx.get("observing_mode", NOSTR)
        science_tables[sci_idx]["pre_science_read_is_reference"] = kwarg_idx.get(
            "pre_science_read_is_reference", ([True] * length)
        )
        science_tables[sci_idx]["pre_science_read_is_resultant"] = kwarg_idx.get(
            "pre_science_read_is_resultant", ([True] * length)
        )
        science_tables[sci_idx]["pre_science_read_types"] = kwarg_idx.get("pre_science_read_types", ([NOSTR] * length))
        science_tables[sci_idx]["pre_science_time_after_reset"] = kwarg_idx.get("pre_science_time_after_reset", NONUM)
        science_tables[sci_idx]["reset_frame_time"] = kwarg_idx.get("reset_frame_time", NONUM)
        science_tables[sci_idx]["science_read_pattern"] = kwarg_idx.get(
            "science_read_pattern", np.arange(1, length + 1, dtype=np.int32).reshape((-1, 1)).tolist()
        )

    return science_tables


def mk_matable(*, gw_table_ids=None, sci_table_ids=None, length=10, filepath=None, **kwargs):
    """
    Create a dummy MA Table instance (or file) with arrays and valid values
    for attributes required by the schema.

    Parameters
    ----------
    table_ids
        list of integer IDs of the MA Tables

    length
        (optional, keyword-only) Length of lists in the model.

    filepath
        (optional, keyword-only) File name and path to write model to.

    Returns
    -------
    roman_datamodels.stnode.MatableRef
    """

    matablerref = stnode.MatableRef()
    matablerref["meta"] = mk_ref_common("MATABLE", **kwargs.get("meta", {}))
    matablerref["guide_window_tables"] = mk_ref_matable_guide_window_tables(gw_table_ids, **kwargs)
    matablerref["science_tables"] = mk_ref_matable_science_tables(sci_table_ids, length, **kwargs)

    return save_node(matablerref, filepath=filepath)


def mk_pixelarea(*, shape=(4096, 4096), filepath=None, **kwargs):
    """
    Create a dummy Pixelarea instance (or file) with arrays and valid values for
    attributes required by the schema.

    Parameters
    ----------
    shape
        (optional, keyword-only) Shape of arrays in the model.
        If shape is greater than 2D, the first two dimensions are used.

    filepath
        (optional, keyword-only) File name and path to write model to.

    Returns
    -------
    roman_datamodels.stnode.PixelareaRef
    """
    if len(shape) > 2:
        shape = shape[:2]

        warnings.warn(f"{MESSAGE} assuming the first two entries. The remaining is thrown out!", UserWarning, stacklevel=2)

    pixelarearef = stnode.PixelareaRef()
    pixelarearef["meta"] = mk_ref_pixelarea_meta(**kwargs.get("meta", {}))

    pixelarearef["data"] = kwargs.get("data", np.zeros(shape, dtype=np.float32))

    return save_node(pixelarearef, filepath=filepath)


def _mk_phot_table_entry(key, **kwargs):
    """
    Create single phot_table entry for a given key.
    """
    if key in ("GRISM", "PRISM", "DARK"):
        entry = {
            "photmjsr": kwargs.get("photmjsr"),
            "uncertainty": kwargs.get("uncertainty"),
        }
    else:
        entry = {
            "photmjsr": kwargs.get("photmjsr", 1.0e-15),
            "uncertainty": kwargs.get("uncertainty", 1.0e-16),
        }

    entry["pixelareasr"] = kwargs.get("pixelareasr", 1.0e-13)

    return entry


def _mk_phot_table(**kwargs):
    """
    Create the phot_table for the photom reference file.
    """
    return {entry: _mk_phot_table_entry(entry, **kwargs.get(entry, {})) for entry in OPT_ELEM}


def mk_wfi_img_photom(*, filepath=None, **kwargs):
    """
    Create a dummy WFI Img Photom instance (or file) with dictionary and valid
    values for attributes required by the schema.

    Parameters
    ----------
    filepath
        (optional, keyword-only) File name and path to write model to.

    Returns
    -------
    roman_datamodels.stnode.WfiImgPhotomRef
    """
    wfi_img_photomref = stnode.WfiImgPhotomRef()
    wfi_img_photomref["meta"] = mk_ref_common("PHOTOM", **kwargs.get("meta", {}))

    wfi_img_photomref["phot_table"] = _mk_phot_table(**kwargs.get("phot_table", {}))

    return save_node(wfi_img_photomref, filepath=filepath)


def mk_readnoise(*, shape=(4096, 4096), filepath=None, **kwargs):
    """
    Create a dummy Readnoise instance (or file) with arrays and valid values for
    attributes required by the schema.

    Parameters
    ----------
    shape
        (optional, keyword-only) Shape of arrays in the model.
        If shape is greater than 2D, the first two dimensions are used.

    filepath
        (optional, keyword-only) File name and path to write model to.

    Returns
    -------
    roman_datamodels.stnode.ReadnoiseRef
    """
    if len(shape) > 2:
        shape = shape[:2]

        warnings.warn(f"{MESSAGE} assuming the first two entries. The remaining is thrown out!", UserWarning, stacklevel=2)

    readnoiseref = stnode.ReadnoiseRef()
    readnoiseref["meta"] = mk_ref_readnoise_meta(**kwargs.get("meta", {}))

    readnoiseref["data"] = kwargs.get("data", np.zeros(shape, dtype=np.float32))

    return save_node(readnoiseref, filepath=filepath)


def mk_saturation(*, shape=(4096, 4096), filepath=None, **kwargs):
    """
    Create a dummy Saturation instance (or file) with arrays and valid values
    for attributes required by the schema.

    Parameters
    ----------
    shape
        (optional, keyword-only) Shape of arrays in the model.
        If shape is greater than 2D, the first two dimensions are used.

    filepath
        (optional, keyword-only) File name and path to write model to.

    Returns
    -------
    roman_datamodels.stnode.SaturationRef
    """
    if len(shape) > 2:
        shape = shape[:2]

        warnings.warn(f"{MESSAGE} assuming the first two entries. The remaining is thrown out!", UserWarning, stacklevel=2)

    saturationref = stnode.SaturationRef()
    saturationref["meta"] = mk_ref_common("SATURATION", **kwargs.get("meta", {}))

    saturationref["dq"] = kwargs.get("dq", np.zeros(shape, dtype=np.uint32))
    saturationref["data"] = kwargs.get("data", np.zeros(shape, dtype=np.float32))

    return save_node(saturationref, filepath=filepath)


def mk_skycells(*, shape_pr=(100,), shape_sc=(1000,), filepath=None, **kwargs):
    skycellref = stnode.SkycellsRef()
    skycellref["meta"] = mk_ref_skycells_meta(**kwargs.get("meta", {}))
    proj_dtype = np.dtype(
        [
            ("index", "<i4"),
            ("ra_tangent", "<f8"),
            ("dec_tangent", "<f8"),
            ("ra_min", "<f8"),
            ("ra_max", "<f8"),
            ("dec_min", "<f8"),
            ("dec_max", "<f8"),
            ("orientat", "<f4"),
            ("x_tangent", "<f8"),
            ("y_tangent", "<f8"),
            ("nx", "<i4"),
            ("ny", "<i4"),
            ("skycell_start", "<i4"),
            ("skycell_end", "<i4"),
        ]
    )
    skycell_dtype = np.dtype(
        [
            ("name", "<U16"),
            ("ra_center", "<f8"),
            ("dec_center", "<f8"),
            ("orientat", "<f4"),
            ("x_tangent", "<f8"),
            ("y_tangent", "<f8"),
            ("ra_corn1", "<f8"),
            ("dec_corn1", "<f8"),
            ("ra_corn2", "<f8"),
            ("dec_corn2", "<f8"),
            ("ra_corn3", "<f8"),
            ("dec_corn3", "<f8"),
            ("ra_corn4", "<f8"),
            ("dec_corn4", "<f8"),
        ]
    )
    proj_tab = kwargs.get("projection_regions", np.zeros(shape_pr, dtype=proj_dtype))
    proj_tab[:]["index"] = np.arange(len(proj_tab))
    skycell_tab = kwargs.get("skycells", np.zeros(shape_sc, dtype=skycell_dtype))
    skycellref["projection_regions"] = proj_tab
    skycellref["skycells"] = skycell_tab

    return save_node(skycellref, filepath=filepath)


def mk_superbias(*, shape=(4096, 4096), filepath=None, **kwargs):
    """
    Create a dummy Superbias instance (or file) with arrays and valid values for
    attributes required by the schema.

    Parameters
    ----------
    shape
        (optional, keyword-only) Shape of arrays in the model.
        If shape is greater than 2D, the first two dimensions are used.

    filepath
        (optional, keyword-only) File name and path to write model to.

    Returns
    -------
    roman_datamodels.stnode.SuperbiasRef
    """
    if len(shape) > 2:
        shape = shape[:2]

        warnings.warn(f"{MESSAGE} assuming the first two entries. The remaining is thrown out!", UserWarning, stacklevel=2)

    superbiasref = stnode.SuperbiasRef()
    superbiasref["meta"] = mk_ref_common("BIAS", **kwargs.get("meta", {}))

    superbiasref["data"] = kwargs.get("data", np.zeros(shape, dtype=np.float32))
    superbiasref["dq"] = kwargs.get("dq", np.zeros(shape, dtype=np.uint32))
    superbiasref["err"] = kwargs.get("err", np.zeros(shape, dtype=np.float32))

    return save_node(superbiasref, filepath=filepath)


def mk_refpix(*, shape=(32, 286721), filepath=None, **kwargs):
    """
    Create a dummy Refpix instance (or file) with arrays and valid values for
    attributes required by the schema.

    Note the default shape is intrinsically connected to the FFT combined with
    specifics of the detector:
        - 32: is the number of detector channels (amp33 is a non-observation
            channel).
        - 286721 is more complex:
            There are 128 columns of the detector per channel, and for time read
            alignment purposes, these columns are padded by 12 additional
            columns. That is 140 columns per row. There are 4096 rows per
            channel. Each channel is then flattened into a 1D array of
            140 * 4096 = 573440 elements. Since the length is even the FFT of
            this array will be of length (573440 / 2) + 1 = 286721.
    Also, note the FFT gives a complex value and we are carrying full numerical
    precision which means it is a complex128.

    Parameters
    ----------
    shape
        (optional, keyword-only) Shape of arrays in the model.
        If shape is greater than 2D, the first two dimensions are used.

    filepath
        (optional, keyword-only) File name and path to write model to.

    Returns
    -------
    roman_datamodels.stnode.RefPixRef
    """
    if len(shape) > 2:
        shape = shape[:2]

        warnings.warn(f"{MESSAGE} assuming the first two entries. The remaining is thrown out!", UserWarning, stacklevel=2)

    refpix = stnode.RefpixRef()
    refpix["meta"] = mk_ref_units_dn_meta("REFPIX", **kwargs.get("meta", {}))

    refpix["gamma"] = kwargs.get("gamma", np.zeros(shape, dtype=np.complex128))
    refpix["zeta"] = kwargs.get("zeta", np.zeros(shape, dtype=np.complex128))
    refpix["alpha"] = kwargs.get("alpha", np.zeros(shape, dtype=np.complex128))

    return save_node(refpix, filepath=filepath)
