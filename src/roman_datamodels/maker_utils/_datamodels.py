import warnings
from random import choices

import asdf
import astropy.time as time
import numpy as np
from astropy import units as u

from roman_datamodels import stnode
from roman_datamodels.random_utils import generate_string

from ._base import NONUM, NOSTR
from ._common_meta import mk_common_meta
from ._tagged_nodes import mk_cal_logs, mk_photometry, mk_resample


def mk_level1_science_raw(shape=(8, 4096, 4096), filepath=None):
    """
    Create a dummy level 1 ScienceRaw instance (or file) with arrays and valid values for attributes
    required by the schema.

    Parameters
    ----------
    shape : tuple, int
        (optional) (z, y, x) Shape of data array. This includes a four-pixel
        border representing the reference pixels. Default is (8, 4096, 4096)
        (8 integrations, 4088 x 4088 represent the science pixels, with the
        additional being the border reference pixels).

    filepath : str
        (optional) File name and path to write model to.

    Returns
    -------
    roman_datamodels.stnode.WfiScienceRaw
    """
    meta = mk_common_meta()
    wfi_science_raw = stnode.WfiScienceRaw()
    wfi_science_raw["meta"] = meta

    n_groups = shape[0]

    wfi_science_raw["data"] = u.Quantity(np.zeros(shape, dtype=np.uint16), u.DN, dtype=np.uint16)

    # add amp 33 ref pix
    wfi_science_raw["amp33"] = u.Quantity(np.zeros((n_groups, 4096, 128), dtype=np.uint16), u.DN, dtype=np.uint16)

    if filepath:
        af = asdf.AsdfFile()
        af.tree = {"roman": wfi_science_raw}
        af.write_to(filepath)
    else:
        return wfi_science_raw


def mk_level2_image(shape=(4088, 4088), n_groups=8, filepath=None):
    """
    Create a dummy level 2 Image instance (or file) with arrays and valid values
    for attributes required by the schema.

    Parameters
    ----------
    shape : tuple, int
        (optional) Shape (y, x) of data array in the model (and its
        corresponding dq/err arrays). This specified size does NOT include the
        four-pixel border of reference pixels - those are trimmed at level 2.
        This size, however, is used to construct the additional arrays that
        contain the original border reference pixels (i.e if shape = (10, 10),
        the border reference pixel arrays will have (y, x) dimensions (14, 4)
        and (4, 14)). Default is 4088 x 4088.

    n_groups : int
        The level 2 file is flattened, but it contains arrays for the original
        reference pixels which remain 3D. n_groups specifies what the z dimension
        of these arrays should be. Defaults to 8.

    filepath : str
        (optional) File name and path to write model to.

    Returns
    -------
    roman_datamodels.stnode.WfiImage
    """
    meta = mk_common_meta()
    meta["photometry"] = mk_photometry()
    wfi_image = stnode.WfiImage()
    wfi_image["meta"] = meta

    # add border reference pixel arrays
    wfi_image["border_ref_pix_left"] = u.Quantity(np.zeros((n_groups, shape[0] + 8, 4), dtype=np.float32), u.DN, dtype=np.float32)
    wfi_image["border_ref_pix_right"] = u.Quantity(
        np.zeros((n_groups, shape[0] + 8, 4), dtype=np.float32), u.DN, dtype=np.float32
    )
    wfi_image["border_ref_pix_top"] = u.Quantity(np.zeros((n_groups, shape[0] + 8, 4), dtype=np.float32), u.DN, dtype=np.float32)
    wfi_image["border_ref_pix_bottom"] = u.Quantity(
        np.zeros((n_groups, shape[0] + 8, 4), dtype=np.float32), u.DN, dtype=np.float32
    )

    # and their dq arrays
    wfi_image["dq_border_ref_pix_left"] = np.zeros((shape[0] + 8, 4), dtype=np.uint32)
    wfi_image["dq_border_ref_pix_right"] = np.zeros((shape[0] + 8, 4), dtype=np.uint32)
    wfi_image["dq_border_ref_pix_top"] = np.zeros((4, shape[1] + 8), dtype=np.uint32)
    wfi_image["dq_border_ref_pix_bottom"] = np.zeros((4, shape[1] + 8), dtype=np.uint32)

    # add amp 33 ref pixel array
    amp33_size = (n_groups, 4096, 128)
    wfi_image["amp33"] = u.Quantity(np.zeros(amp33_size, dtype=np.uint16), u.DN, dtype=np.uint16)

    wfi_image["data"] = u.Quantity(np.zeros(shape, dtype=np.float32), u.electron / u.s, dtype=np.float32)
    wfi_image["dq"] = np.zeros(shape, dtype=np.uint32)
    wfi_image["err"] = u.Quantity(np.zeros(shape, dtype=np.float32), u.electron / u.s, dtype=np.float32)

    wfi_image["var_poisson"] = u.Quantity(np.zeros(shape, dtype=np.float32), u.electron**2 / u.s**2, dtype=np.float32)
    wfi_image["var_rnoise"] = u.Quantity(np.zeros(shape, dtype=np.float32), u.electron**2 / u.s**2, dtype=np.float32)
    wfi_image["var_flat"] = u.Quantity(np.zeros(shape, dtype=np.float32), u.electron**2 / u.s**2, dtype=np.float32)
    wfi_image["cal_logs"] = mk_cal_logs()

    if filepath:
        af = asdf.AsdfFile()
        af.tree = {"roman": wfi_image}
        af.write_to(filepath)
    else:
        return wfi_image


def mk_level3_mosaic(shape=None, n_images=2, filepath=None):
    """
    Create a dummy level 3 Mosaic instance (or file) with arrays and valid values
    for attributes required by the schema.

    Parameters
    ----------
    shape : tuple, int
        (optional) Shape (y, x) of data array in the model (and its
        corresponding dq/err arrays). Default is 4088 x 4088.

    n_images : int
        Number of images used to create the level 3 image. Defaults to 2.

    filepath : str
        (optional) File name and path to write model to.

    Returns
    -------
    roman_datamodels.stnode.WfiMosaic
    """
    meta = mk_common_meta()
    meta["photometry"] = mk_photometry()
    meta["resample"] = mk_resample()
    wfi_mosaic = stnode.WfiMosaic()
    wfi_mosaic["meta"] = meta
    if not shape:
        shape = (4088, 4088)

    wfi_mosaic["data"] = u.Quantity(np.zeros(shape, dtype=np.float32), u.electron / u.s, dtype=np.float32)
    wfi_mosaic["err"] = u.Quantity(np.zeros(shape, dtype=np.float32), u.electron / u.s, dtype=np.float32)
    wfi_mosaic["context"] = np.zeros((n_images,) + shape, dtype=np.uint32)
    wfi_mosaic["weight"] = np.zeros(shape, dtype=np.float32)

    wfi_mosaic["var_poisson"] = u.Quantity(np.zeros(shape, dtype=np.float32), u.electron**2 / u.s**2, dtype=np.float32)
    wfi_mosaic["var_rnoise"] = u.Quantity(np.zeros(shape, dtype=np.float32), u.electron**2 / u.s**2, dtype=np.float32)
    wfi_mosaic["var_flat"] = u.Quantity(np.zeros(shape, dtype=np.float32), u.electron**2 / u.s**2, dtype=np.float32)
    wfi_mosaic["cal_logs"] = mk_cal_logs()

    if filepath:
        af = asdf.AsdfFile()
        af.tree = {"roman": wfi_mosaic}
        af.write_to(filepath)
    else:
        return wfi_mosaic


def mk_ramp(shape=(8, 4096, 4096), filepath=None):
    """
    Create a dummy Ramp instance (or file) with arrays and valid values for attributes
    required by the schema.

    Parameters
    ----------
    shape : tuple, int
        (optional) Shape (z, y, x) of data array in the model (and its
        corresponding dq/err arrays). This specified size includes the
        four-pixel border of reference pixels. Default is 8 x 4096 x 4096.

    filepath : str
        (optional) File name and path to write model to.

    Returns
    -------
    roman_datamodels.stnode.Ramp
    """
    meta = mk_common_meta()
    ramp = stnode.Ramp()
    ramp["meta"] = meta

    # add border reference pixel arrays
    ramp["border_ref_pix_left"] = u.Quantity(np.zeros((shape[0], shape[1], 4), dtype=np.float32), u.DN, dtype=np.float32)
    ramp["border_ref_pix_right"] = u.Quantity(np.zeros((shape[0], shape[1], 4), dtype=np.float32), u.DN, dtype=np.float32)
    ramp["border_ref_pix_top"] = u.Quantity(np.zeros((shape[0], 4, shape[2]), dtype=np.float32), u.DN, dtype=np.float32)
    ramp["border_ref_pix_bottom"] = u.Quantity(np.zeros((shape[0], 4, shape[2]), dtype=np.float32), u.DN, dtype=np.float32)

    # and their dq arrays
    ramp["dq_border_ref_pix_left"] = np.zeros((shape[1], 4), dtype=np.uint32)
    ramp["dq_border_ref_pix_right"] = np.zeros((shape[1], 4), dtype=np.uint32)
    ramp["dq_border_ref_pix_top"] = np.zeros((4, shape[2]), dtype=np.uint32)
    ramp["dq_border_ref_pix_bottom"] = np.zeros((4, shape[2]), dtype=np.uint32)

    # add amp 33 ref pixel array
    ramp["amp33"] = u.Quantity(np.zeros((shape[0], shape[1], 128), dtype=np.uint16), u.DN, dtype=np.uint16)

    ramp["data"] = u.Quantity(np.full(shape, 1.0, dtype=np.float32), u.DN, dtype=np.float32)
    ramp["pixeldq"] = np.zeros(shape[1:], dtype=np.uint32)
    ramp["groupdq"] = np.zeros(shape, dtype=np.uint8)
    ramp["err"] = u.Quantity(np.zeros(shape, dtype=np.float32), u.DN, dtype=np.float32)

    if filepath:
        af = asdf.AsdfFile()
        af.tree = {"roman": ramp}
        af.write_to(filepath)
    else:
        return ramp


def mk_ramp_fit_output(shape=(8, 4096, 4096), filepath=None):
    """
    Create a dummy Rampfit Output instance (or file) with arrays and valid values for attributes
    required by the schema.

    Parameters
    ----------
    shape
        (optional) Shape of arrays in the model.

    filepath
        (optional) File name and path to write model to.

    Returns
    -------
    roman_datamodels.stnode.RampFitOutput
    """
    meta = mk_common_meta()
    rampfitoutput = stnode.RampFitOutput()
    rampfitoutput["meta"] = meta

    rampfitoutput["slope"] = u.Quantity(np.zeros(shape, dtype=np.float32), u.electron / u.s, dtype=np.float32)
    rampfitoutput["sigslope"] = u.Quantity(np.zeros(shape, dtype=np.float32), u.electron / u.s, dtype=np.float32)
    rampfitoutput["yint"] = u.Quantity(np.zeros(shape, dtype=np.float32), u.electron, dtype=np.float32)
    rampfitoutput["sigyint"] = u.Quantity(np.zeros(shape, dtype=np.float32), u.electron, dtype=np.float32)
    rampfitoutput["pedestal"] = u.Quantity(np.zeros(shape[1:], dtype=np.float32), u.electron, dtype=np.float32)
    rampfitoutput["weights"] = np.zeros(shape, dtype=np.float32)
    rampfitoutput["crmag"] = u.Quantity(np.zeros(shape, dtype=np.float32), u.electron, dtype=np.float32)
    rampfitoutput["var_poisson"] = u.Quantity(np.zeros(shape, dtype=np.float32), u.electron**2 / u.s**2, dtype=np.float32)
    rampfitoutput["var_rnoise"] = u.Quantity(np.zeros(shape, dtype=np.float32), u.electron**2 / u.s**2, dtype=np.float32)

    if filepath:
        af = asdf.AsdfFile()
        af.tree = {"roman": rampfitoutput}
        af.write_to(filepath)
    else:
        return rampfitoutput


def mk_rampfitoutput(**kwargs):
    warnings.warn("mk_rampfitoutput is deprecated. Use mk_rampfit_output instead.", DeprecationWarning)

    return mk_ramp_fit_output(**kwargs)


def mk_associations(shape=(2, 3, 1), filepath=None):
    """
    Create a dummy Association table instance (or file) with table and valid values for attributes
    required by the schema.
    Parameters
    ----------
    shape : tuple
        (optional) The shape of the member elements of products.
    filepath : string
        (optional) File name and path to write model to.
    Returns
    -------
    roman_datamodels.stnode.AssociationsModel
    """

    associations = stnode.Associations()

    associations["asn_type"] = "image"
    associations["asn_rule"] = "candidate_Asn_Lv2Image_i2d"
    associations["version_id"] = "null"
    associations["code_version"] = "0.16.2.dev16+g640b0b79"
    associations["degraded_status"] = "No known degraded exposures in association."
    associations["program"] = 1
    associations["constraints"] = (
        "DMSAttrConstraint({'name': 'program', 'sources': ['program'], "
        "'value': '001'})\nConstraint_TargetAcq({'name': 'target_acq', 'value': "
        "'target_acquisition'})\nDMSAttrConstraint({'name': 'science', "
        "'DMSAttrConstraint({'name': 'asn_candidate','sources': "
        "['asn_candidate'], 'value': \"\\\\('o036',\\\\ 'observation'\\\\)\"})"
    )
    associations["asn_id"] = "o036"
    associations["asn_pool"] = "r00001_20200530t023154_pool"
    associations["target"] = 16

    file_idx = 0
    associations["products"] = []
    for product_idx in range(len(shape)):
        exptypes = choices(["SCIENCE", "CALIBRATION", "ENGINEERING"], k=shape[product_idx])
        members_lst = []
        for member_idx in range(shape[product_idx]):
            members_lst.append(
                {"expname": "file_" + str(file_idx) + ".asdf", "exposerr": "null", "exptype": exptypes[member_idx]}
            )
            file_idx += 1
        associations["products"].append({"name": "product" + str(product_idx), "members": members_lst})

    if filepath:
        af = asdf.AsdfFile()
        af.tree = {"roman": associations}
        af.write_to(filepath)
    else:
        return associations


def mk_guidewindow(shape=(2, 8, 16, 32, 32), filepath=None):
    """
    Create a dummy Guidewindow instance (or file) with arrays and valid values for attributes
    required by the schema.

    Parameters
    ----------
    shape
        (optional) Shape of arrays in the model.

    filepath
        (optional) File name and path to write model to.

    Returns
    -------
    roman_datamodels.stnode.Guidewindow
    """
    meta = mk_common_meta()
    guidewindow = stnode.Guidewindow()
    guidewindow["meta"] = meta

    guidewindow["meta"]["file_creation_time"] = time.Time("2020-01-01T20:00:00.0", format="isot", scale="utc")
    guidewindow["meta"]["gw_start_time"] = time.Time("2020-01-01T00:00:00.0", format="isot", scale="utc")
    guidewindow["meta"]["gw_end_time"] = time.Time("2020-01-01T10:00:00.0", format="isot", scale="utc")
    guidewindow["meta"]["gw_function_start_time"] = time.Time("2020-01-01T00:00:00.0", format="isot", scale="utc")
    guidewindow["meta"]["gw_function_end_time"] = time.Time("2020-01-01T00:00:00.0", format="isot", scale="utc")
    guidewindow["meta"]["gw_frame_readout_time"] = NONUM
    guidewindow["meta"]["pedestal_resultant_exp_time"] = NONUM
    guidewindow["meta"]["signal_resultant_exp_time"] = NONUM
    guidewindow["meta"]["gw_acq_number"] = NONUM
    guidewindow["meta"]["gw_science_file_source"] = NOSTR
    guidewindow["meta"]["gw_mode"] = "WIM-ACQ"
    guidewindow["meta"]["gw_window_xstart"] = NONUM
    guidewindow["meta"]["gw_window_ystart"] = NONUM
    guidewindow["meta"]["gw_window_xstop"] = guidewindow["meta"]["gw_window_xstart"] + 170
    guidewindow["meta"]["gw_window_ystop"] = guidewindow["meta"]["gw_window_ystart"] + 24
    guidewindow["meta"]["gw_window_xsize"] = 170
    guidewindow["meta"]["gw_window_ysize"] = 24

    guidewindow["meta"]["gw_function_start_time"] = time.Time("2020-01-01T00:00:00.0", format="isot", scale="utc")
    guidewindow["meta"]["gw_function_end_time"] = time.Time("2020-01-01T00:00:00.0", format="isot", scale="utc")
    guidewindow["meta"]["data_start"] = NONUM
    guidewindow["meta"]["data_end"] = NONUM
    guidewindow["meta"]["gw_acq_exec_stat"] = generate_string("Status ", 15)

    guidewindow["pedestal_frames"] = u.Quantity(np.zeros(shape, dtype=np.uint16), u.DN, dtype=np.uint16)
    guidewindow["signal_frames"] = u.Quantity(np.zeros(shape, dtype=np.uint16), u.DN, dtype=np.uint16)
    guidewindow["amp33"] = u.Quantity(np.zeros(shape, dtype=np.uint16), u.DN, dtype=np.uint16)

    if filepath:
        af = asdf.AsdfFile()
        af.tree = {"roman": guidewindow}
        af.write_to(filepath)
    else:
        return guidewindow
