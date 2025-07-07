import warnings

import numpy as np
from astropy import time

from roman_datamodels import stnode

from ._base import MESSAGE, save_node
from ._common_meta import (
    mk_catalog_meta,
    mk_common_meta,
    mk_guidewindow_meta,
    mk_l1_detector_guidewindow_meta,
    mk_l1_face_guidewindow_meta,
    mk_l2_meta,
    mk_mosaic_catalog_meta,
    mk_msos_stack_meta,
    mk_ramp_meta,
    mk_wcs,
    mk_wfi_wcs_common_meta,
)


def mk_level1_science_raw(*, shape=(8, 4096, 4096), dq=False, filepath=None, **kwargs):
    """
    Create a dummy level 1 ScienceRaw instance (or file) with arrays and valid
    values for attributes required by the schema.

    Parameters
    ----------
    shape : tuple, int
        (optional, keyword-only) (z, y, x) Shape of data array. This includes a
        four-pixel border representing the reference pixels. Default is
            (8, 4096, 4096)
        (8 integrations, 4088 x 4088 represent the science pixels, with the
        additional being the border reference pixels).

    dq : bool
        (optional, keyword-only) Toggle to add a data quality array for
        dropout pixels

    filepath : str
        (optional, keyword-only) File name and path to write model to.

    Returns
    -------
    roman_datamodels.stnode.WfiScienceRaw
    """
    if len(shape) != 3:
        shape = (8, 4096, 4096)
        warnings.warn("Input shape must be 3D. Defaulting to (8, 4096, 4096)", UserWarning, stacklevel=2)

    wfi_science_raw = stnode.WfiScienceRaw()
    wfi_science_raw["meta"] = mk_common_meta(**kwargs.get("meta", {}))

    n_groups = shape[0]

    wfi_science_raw["data"] = kwargs.get("data", np.zeros(shape, dtype=np.uint16))

    if dq:
        wfi_science_raw["resultantdq"] = kwargs.get("resultantdq", np.zeros(shape, dtype=np.uint8))

    # add amp 33 ref pix
    wfi_science_raw["amp33"] = kwargs.get("amp33", np.zeros((n_groups, 4096, 128), dtype=np.uint16))

    return save_node(wfi_science_raw, filepath=filepath)


def mk_level2_image(*, shape=(4088, 4088), n_groups=8, filepath=None, **kwargs):
    """
    Create a dummy level 2 Image instance (or file) with arrays and valid values
    for attributes required by the schema.

    Parameters
    ----------
    shape : tuple, int
        (optional, keyword-only) Shape (y, x) of data array in the model (and
        its corresponding dq/err arrays). This specified size does NOT include
        the four-pixel border of reference pixels - those are trimmed at level
        2.  This size, however, is used to construct the additional arrays that
        contain the original border reference pixels (i.e if shape = (10, 10),
        the border reference pixel arrays will have (y, x) dimensions (14, 4)
        and (4, 14)). Default is 4088 x 4088.
        If shape is a tuple of length 3, the first element is assumed to be the
        n_groups and will override any settings there.

    n_groups : int
        (optional, keyword-only) The level 2 file is flattened, but it contains
        arrays for the original reference pixels which remain 3D. n_groups
        specifies what the z dimension of these arrays should be. Defaults to 8.

    filepath : str
        (optional, keyword-only) File name and path to write model to.

    Returns
    -------
    roman_datamodels.stnode.WfiImage
    """
    if len(shape) > 2:
        n_groups = shape[0]
        shape = shape[1:3]

        warnings.warn(
            f"{MESSAGE} assuming the first entry is n_groups followed by y, x. The remaining is thrown out!",
            UserWarning,
            stacklevel=2,
        )

    wfi_image = stnode.WfiImage()

    wfi_image["meta"] = mk_l2_meta(**kwargs.get("meta", {}))

    # add border reference pixel arrays
    wfi_image["border_ref_pix_left"] = kwargs.get("border_ref_pix_left", np.zeros((n_groups, shape[0] + 8, 4), dtype=np.float32))
    wfi_image["border_ref_pix_right"] = kwargs.get(
        "border_ref_pix_right", np.zeros((n_groups, shape[0] + 8, 4), dtype=np.float32)
    )
    wfi_image["border_ref_pix_top"] = kwargs.get("border_ref_pix_top", np.zeros((n_groups, shape[0] + 8, 4), dtype=np.float32))
    wfi_image["border_ref_pix_bottom"] = kwargs.get(
        "border_ref_pix_bottom", np.zeros((n_groups, shape[0] + 8, 4), dtype=np.float32)
    )

    # and their dq arrays
    wfi_image["dq_border_ref_pix_left"] = kwargs.get("dq_border_ref_pix_left", np.zeros((shape[0] + 8, 4), dtype=np.uint32))
    wfi_image["dq_border_ref_pix_right"] = kwargs.get("dq_border_ref_pix_right", np.zeros((shape[0] + 8, 4), dtype=np.uint32))
    wfi_image["dq_border_ref_pix_top"] = kwargs.get("dq_border_ref_pix_top", np.zeros((4, shape[1] + 8), dtype=np.uint32))
    wfi_image["dq_border_ref_pix_bottom"] = kwargs.get("dq_border_ref_pix_bottom", np.zeros((4, shape[1] + 8), dtype=np.uint32))

    # add amp 33 ref pixel array
    amp33_size = (n_groups, 4096, 128)
    wfi_image["amp33"] = kwargs.get("amp33", np.zeros(amp33_size, dtype=np.uint16))
    wfi_image["data"] = kwargs.get("data", np.zeros(shape, dtype=np.float32))
    wfi_image["dq"] = kwargs.get("dq", np.zeros(shape, dtype=np.uint32))
    wfi_image["err"] = kwargs.get("err", np.zeros(shape, dtype=np.float32))

    wfi_image["var_poisson"] = kwargs.get("var_poisson", np.zeros(shape, dtype=np.float32))
    wfi_image["var_rnoise"] = kwargs.get("var_rnoise", np.zeros(shape, dtype=np.float32))
    wfi_image["var_flat"] = kwargs.get("var_flat", np.zeros(shape, dtype=np.float32))
    # wfi_image["cal_logs"] = mk_cal_logs(**kwargs)

    wfi_image["meta"]["wcs"] = mk_wcs()

    return save_node(wfi_image, filepath=filepath)


def mk_level3_mosaic(*, shape=(4088, 4088), n_images=2, filepath=None, **kwargs):
    """
    Create a dummy level 3 Mosaic instance (or file) with arrays and valid
    values for attributes required by the schema.

    Parameters
    ----------
    shape : tuple, int
        (optional, keyword-only) Shape (y, x) of data array in the model (and
        its corresponding dq/err arrays). Default is 4088 x 4088.
        If shape is a tuple of length 3, the first element is assumed to be
        n_images and will override the n_images parameter.

    n_images : int
        Number of images used to create the level 3 image. Defaults to 2.

    filepath : str
        (optional) File name and path to write model to.

    Returns
    -------
    roman_datamodels.stnode.WfiMosaic
    """
    if len(shape) > 2:
        shape = shape[1:3]
        n_images = shape[0]

        warnings.warn(
            f"{MESSAGE} assuming the first entry is n_images followed by y, x. The remaining is thrown out!",
            UserWarning,
            stacklevel=2,
        )

    wfi_mosaic = stnode.WfiMosaic.create_fake_data(defaults=kwargs, shape=shape)

    # reshape the context array to match n_images
    if "context" not in kwargs:
        wfi_mosaic.context = np.zeros((n_images, *shape), dtype=wfi_mosaic.context.dtype)

    return save_node(wfi_mosaic, filepath=filepath)


def mk_msos_stack(*, shape=(4096, 4096), filepath=None, **kwargs):
    """
    Create a dummy Level 3 MSOS stack instance (or file) with arrays and valid values

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
    roman_datamodels.stnode.MsosStack
    """
    if len(shape) > 2:
        shape = shape[1:3]

        warnings.warn(
            f"{MESSAGE} assuming the the first two entries are y, x. The remaining is thrown out!", UserWarning, stacklevel=2
        )

    msos_stack = stnode.MsosStack()
    msos_stack["meta"] = mk_msos_stack_meta(**kwargs.get("meta", {}))

    msos_stack["data"] = kwargs.get("data", np.zeros(shape, dtype=np.float64))
    msos_stack["uncertainty"] = kwargs.get("uncertainty", np.zeros(shape, dtype=np.float64))
    msos_stack["mask"] = kwargs.get("mask", np.zeros(shape, dtype=np.uint8))
    msos_stack["coverage"] = kwargs.get("coverage", np.zeros(shape, dtype=np.uint8))

    return save_node(msos_stack, filepath=filepath)


def mk_ramp(*, shape=(8, 4096, 4096), filepath=None, **kwargs):
    """
    Create a dummy Ramp instance (or file) with arrays and valid values for attributes
    required by the schema.

    Parameters
    ----------
    shape : tuple, int
        (optional, keyword-only) Shape (z, y, x) of data array in the model (and
        its corresponding dq/err arrays). This specified size includes the
        four-pixel border of reference pixels. Default is 8 x 4096 x 4096.

    filepath : str
        (optional, keyword-only) File name and path to write model to.

    Returns
    -------
    roman_datamodels.stnode.Ramp
    """
    if len(shape) != 3:
        shape = (8, 4096, 4096)
        warnings.warn("Input shape must be 3D. Defaulting to (8, 4096, 4096)", UserWarning, stacklevel=2)

    ramp = stnode.Ramp()
    ramp["meta"] = mk_ramp_meta(**kwargs.get("meta", {}))

    # add border reference pixel arrays
    ramp["border_ref_pix_left"] = kwargs.get("border_ref_pix_left", np.zeros((shape[0], shape[1], 4), dtype=np.float32))
    ramp["border_ref_pix_right"] = kwargs.get("border_ref_pix_right", np.zeros((shape[0], shape[1], 4), dtype=np.float32))
    ramp["border_ref_pix_top"] = kwargs.get("border_ref_pix_top", np.zeros((shape[0], 4, shape[2]), dtype=np.float32))
    ramp["border_ref_pix_bottom"] = kwargs.get("border_ref_pix_bottom", np.zeros((shape[0], 4, shape[2]), dtype=np.float32))

    # and their dq arrays
    ramp["dq_border_ref_pix_left"] = kwargs.get("dq_border_ref_pix_left", np.zeros((shape[1], 4), dtype=np.uint32))
    ramp["dq_border_ref_pix_right"] = kwargs.get("dq_border_ref_pix_right", np.zeros((shape[1], 4), dtype=np.uint32))
    ramp["dq_border_ref_pix_top"] = kwargs.get("dq_border_ref_pix_top", np.zeros((4, shape[2]), dtype=np.uint32))
    ramp["dq_border_ref_pix_bottom"] = kwargs.get("dq_border_ref_pix_bottom", np.zeros((4, shape[2]), dtype=np.uint32))

    # add amp 33 ref pixel array
    ramp["amp33"] = kwargs.get("amp33", np.zeros((shape[0], shape[1], 128), dtype=np.uint16))

    ramp["data"] = kwargs.get("data", np.full(shape, 1.0, dtype=np.float32))
    ramp["pixeldq"] = kwargs.get("pixeldq", np.zeros(shape[1:], dtype=np.uint32))
    ramp["groupdq"] = kwargs.get("groupdq", np.zeros(shape, dtype=np.uint8))
    ramp["err"] = kwargs.get("err", np.zeros(shape, dtype=np.float32))

    return save_node(ramp, filepath=filepath)


def mk_ramp_fit_output(*, shape=(8, 4096, 4096), filepath=None, **kwargs):
    """
    Create a dummy Rampfit Output instance (or file) with arrays and valid
    values for attributes required by the schema.

    Parameters
    ----------
    shape
        (optional, keyword-only) Shape of arrays in the model.

    filepath
        (optional, keyword-only) File name and path to write model to.

    Returns
    -------
    roman_datamodels.stnode.RampFitOutput
    """
    if len(shape) != 3:
        shape = (8, 4096, 4096)
        warnings.warn("Input shape must be 3D. Defaulting to (8, 4096, 4096)", UserWarning, stacklevel=2)

    rampfitoutput = stnode.RampFitOutput()
    rampfitoutput["meta"] = mk_common_meta(**kwargs.get("meta", {}))

    rampfitoutput["slope"] = kwargs.get("slope", np.zeros(shape, dtype=np.float32))
    rampfitoutput["sigslope"] = kwargs.get("sigslope", np.zeros(shape, dtype=np.float32))
    rampfitoutput["yint"] = kwargs.get("yint", np.zeros(shape, dtype=np.float32))
    rampfitoutput["sigyint"] = kwargs.get("sigyint", np.zeros(shape, dtype=np.float32))
    rampfitoutput["pedestal"] = kwargs.get("pedestal", np.zeros(shape[1:], dtype=np.float32))
    rampfitoutput["weights"] = kwargs.get("weights", np.zeros(shape, dtype=np.float32))
    rampfitoutput["crmag"] = kwargs.get("crmag", np.zeros(shape, dtype=np.float32))
    rampfitoutput["var_poisson"] = kwargs.get("var_poisson", np.zeros(shape, dtype=np.float32))
    rampfitoutput["var_rnoise"] = kwargs.get("var_rnoise", np.zeros(shape, dtype=np.float32))

    return save_node(rampfitoutput, filepath=filepath)


def mk_rampfitoutput(**kwargs):
    warnings.warn("mk_rampfitoutput is deprecated. Use mk_rampfit_output instead.", DeprecationWarning, stacklevel=2)

    return mk_ramp_fit_output(**kwargs)


def mk_associations(*, shape=(2, 3, 1), filepath=None, **kwargs):
    """
    Create a dummy Association table instance (or file) with table and valid
    values for attributes required by the schema.

    Parameters
    ----------
    shape : tuple
        (optional, keyword-only) The shape of the member elements of products.
    filepath : string
        (optional, keyword-only) File name and path to write model to.

    Returns
    -------
    roman_datamodels.stnode.AssociationsModel
    """

    associations = stnode.Associations()

    associations["asn_type"] = kwargs.get("asn_type", "image")
    associations["asn_rule"] = kwargs.get("asn_rule", "candidate_Asn_Lv2Image_i2d")
    associations["version_id"] = kwargs.get("version_id", "null")
    associations["code_version"] = kwargs.get("code_version", "0.16.2.dev16+g640b0b79")
    associations["degraded_status"] = kwargs.get("degraded_status", "No known degraded exposures in association.")
    associations["program"] = kwargs.get("program", 1)
    associations["constraints"] = kwargs.get(
        "constraints",
        (
            "DMSAttrConstraint({'name': 'program', 'sources': ['program'], "
            "'value': '001'})\nConstraint_TargetAcq({'name': 'target_acq', 'value': "
            "'target_acquisition'})\nDMSAttrConstraint({'name': 'science', "
            "'DMSAttrConstraint({'name': 'asn_candidate','sources': "
            "['asn_candidate'], 'value': \"\\\\('o036',\\\\ 'observation'\\\\)\"})"
        ),
    )
    associations["asn_id"] = kwargs.get("asn_id", "o036")
    associations["asn_pool"] = kwargs.get("asn_pool", "r00001_20200530t023154_pool")
    associations["target"] = kwargs.get("target", 16)

    file_idx = 0
    if "products" in kwargs:
        associations["products"] = kwargs["products"]
    else:
        associations["products"] = []
        CHOICES = ["SCIENCE", "CALIBRATION", "ENGINEERING"]
        for product_idx, members in enumerate(shape):
            members_lst = []
            for member_idx in range(members):
                members_lst.append(
                    {"expname": "file_" + str(file_idx) + ".asdf", "exposerr": "null", "exptype": CHOICES[member_idx % 3]}
                )
                file_idx += 1
            associations["products"].append({"name": f"product{product_idx}", "members": members_lst})

    return save_node(associations, filepath=filepath)


def mk_l1_face_gw_face_data(*, shape=(16,), filepath=None, **kwargs):
    """
    Create a dummy L1FaceGuidewindow instance (or file) with arrays and valid values
    for attributes required by the schema.

    Parameters
    ----------
    shape
        (optional, keyword-only) Shape of arrays in the model.
    mode
        (optional, keyword-only) Mode of the instrument, image (WIM) or spectrograph (WSM).
    filepath
        (optional, keyword-only) File name and path to write model to.

    Returns
    -------
    dict
    """
    if len(shape) != 1:
        shape = (16,)
        warnings.warn("Input shape must be 1D. Defaulting to (16,)", UserWarning, stacklevel=2)

    l1facegw_fd = {}
    l1facegw_fd["delta"] = kwargs.get("delta", np.zeros(shape, dtype=np.float32))
    l1facegw_fd["delta2"] = kwargs.get("delta2", np.zeros(shape, dtype=np.float32))
    l1facegw_fd["epsilon"] = kwargs.get("epsilon", np.zeros(shape, dtype=np.float32))
    l1facegw_fd["epsilon2"] = kwargs.get("epsilon2", np.zeros(shape, dtype=np.float32))
    l1facegw_fd["zeta"] = kwargs.get("zeta", np.zeros(shape, dtype=np.float32))
    l1facegw_fd["delta_var"] = kwargs.get("delta_var", np.zeros(shape, dtype=np.float32))
    l1facegw_fd["epsilon_var"] = kwargs.get("epsilon_var", np.zeros(shape, dtype=np.float32))
    l1facegw_fd["zeta_var"] = kwargs.get("zeta_var", np.zeros(shape, dtype=np.float32))
    l1facegw_fd["horizontal_variance"] = kwargs.get("horizontal_variance", np.zeros(shape, dtype=np.float32))
    l1facegw_fd["vertical_variance"] = kwargs.get("vertical_variance", np.zeros(shape, dtype=np.float32))
    l1facegw_fd["num_stars_used"] = kwargs.get("num_stars_used", np.zeros(shape, dtype=np.uint8))
    l1facegw_fd["num_centroid_cycles"] = kwargs.get("num_centroid_cycles", np.zeros(shape, dtype=np.uint8))
    l1facegw_fd["attitude_estimate_quality"] = kwargs.get(
        "attitude_estimate_quality", np.array(["AQ_FAILED_IN_PHASE_TRANSITION"] * shape[0], dtype="<U30")
    )

    l1facegw_fd["centroid_times"] = kwargs.get(
        "centroid_times", [time.Time("2024-01-01T12:00:00", format="isot", scale="utc")] * shape[0]
    )
    l1facegw_fd["fgs_op_phase"] = kwargs.get("fgs_op_phase", ["NOT_CONFIGURED"] * shape[0])

    return l1facegw_fd


def mk_l1_face_guidewindow(*, shape=(16,), mode="WSM", filepath=None, **kwargs):
    """
    Create a dummy L1FaceGuidewindow instance (or file) with arrays and valid values
    for attributes required by the schema.

    Parameters
    ----------
    shape
        (optional, keyword-only) Shape of arrays in the model.
    mode
        (optional, keyword-only) Mode of the instrument, image (WIM) or spectrograph (WSM).
    filepath
        (optional, keyword-only) File name and path to write model to.

    Returns
    -------
    roman_datamodels.stnode.L1FaceGuidewindow
    """
    if len(shape) != 1:
        shape = (16,)
        warnings.warn("Input shape must be 1D. Defaulting to (16,).", UserWarning, stacklevel=2)

    if mode not in ["WIM", "WSM"]:
        mode = "WSM"
        warnings.warn("Mode must be in [WIM, WSM]. Defaulting to WSM.", UserWarning, stacklevel=2)

    l1facegw = stnode.L1FaceGuidewindow()
    l1facegw["meta"] = mk_l1_face_guidewindow_meta(mode, **kwargs.get("meta", {}))
    l1facegw["face_data"] = mk_l1_face_gw_face_data(**kwargs.get("face_data", {}))

    return save_node(l1facegw, filepath=filepath)


def mk_guidewindow(*, shape=(2, 8, 16, 32, 32), filepath=None, **kwargs):
    """
    Create a dummy Guidewindow instance (or file) with arrays and valid values
    for attributes required by the schema.

    Parameters
    ----------
    shape
        (optional, keyword-only) Shape of arrays in the model.

    filepath
        (optional, keyword-only) File name and path to write model to.

    Returns
    -------
    roman_datamodels.stnode.Guidewindow
    """
    if len(shape) != 5:
        shape = (2, 8, 16, 32, 32)
        warnings.warn("Input shape must be 5D. Defaulting to (2, 8, 16, 32, 32)", UserWarning, stacklevel=2)

    guidewindow = stnode.Guidewindow()
    guidewindow["meta"] = mk_guidewindow_meta(**kwargs.get("meta", {}))

    guidewindow["pedestal_frames"] = kwargs.get("pedestal_frames", np.zeros(shape, dtype=np.uint16))
    guidewindow["signal_frames"] = kwargs.get("signal_frames", np.zeros(shape, dtype=np.uint16))
    guidewindow["amp33"] = kwargs.get("amp33", np.zeros(shape, dtype=np.uint16))

    return save_node(guidewindow, filepath=filepath)


def mk_l1_detector_guidewindow_amp33(*, mode="WSM", shape=(16, 32, 32), **kwargs):
    """
    Create a dummy Level 1 detector guidewindow amp33 instance (or file) with
    arrays and valid values for attributes required by the schema.

    Parameters
    ----------
    mode : string
        (optional, keyword-only) Mode of the instrument, image (WIM) or spectrograph (WSM).

    shape
        (optional, keyword-only) Shape of arrays in the model.

    filepath
        (optional, keyword-only) File name and path to write model to.

    Returns
    -------
    dict (defined by the l1_detector_guidewindow-1.0.0 schema with additional guidewindow metadata)
    """
    if len(shape) != 3:
        shape = (16, 32, 32)
        warnings.warn("Input shape must be 3D. Defaulting to (16, 32, 32)", UserWarning, stacklevel=2)

    if mode is None:
        mode = "WSM"

    l1detectorgwamp33 = {}

    l1detectorgwamp33["amp33_track_pedestals"] = kwargs.get("amp33_track_pedestals", np.zeros(shape, dtype=np.uint16))
    l1detectorgwamp33["amp33_track_signals"] = kwargs.get("amp33_track_signals", np.zeros(shape, dtype=np.uint16))

    l1detectorgwamp33["amp33_acq_pedestals"] = kwargs.get("amp33_acq_pedestals", np.zeros(shape, dtype=np.uint16))
    l1detectorgwamp33["amp33_acq_signals"] = kwargs.get("amp33_acq_signals", np.zeros(shape, dtype=np.uint16))

    if mode == "WSM":
        l1detectorgwamp33["amp33_edge_acq_pedestals"] = kwargs.get("amp33_edge_acq_pedestals", np.zeros(shape, dtype=np.uint16))
        l1detectorgwamp33["amp33_edge_acq_signals"] = kwargs.get("amp33_edge_acq_signals", np.zeros(shape, dtype=np.uint16))

    return l1detectorgwamp33


def mk_l1_detector_guidewindow_centroid(*, mode="WSM", shape=(16, 32, 32), **kwargs):
    """
    Create a dummy Level 1 detector guidewindow centroid instance (or file) with
    arrays and valid values for attributes required by the schema.

    Parameters
    ----------
    mode : string
        (optional, keyword-only) Mode of the instrument, image (WIM) or spectrograph (WSM).

    shape
        (optional, keyword-only) Shape of arrays in the model.

    filepath
        (optional, keyword-only) File name and path to write model to.

    Returns
    -------
    dict (defined by the l1_detector_guidewindow-1.0.0 schema with additional guidewindow metadata)
    """
    if len(shape) != 3:
        shape = (16, 32, 32)
        warnings.warn("Input shape must be 3D. Defaulting to (16, 32, 32)", UserWarning, stacklevel=2)

    if mode is None:
        mode = "WSM"

    l1detectorgwcentroid = {}
    l1detectorgwcentroid["acq_centroids"] = kwargs.get("acq_centroids", np.zeros(shape, dtype=np.float32))
    l1detectorgwcentroid["acq_centroid_errs"] = kwargs.get("acq_centroid_errs", np.zeros(shape, dtype=np.float32))
    l1detectorgwcentroid["acq_centroid_quality"] = kwargs.get(
        "acq_centroid_quality", np.array([["?"] * shape[2]] * shape[1], dtype="<U40")
    )
    l1detectorgwcentroid["acq_centroid_times"] = kwargs.get(
        "acq_centroid_times", [time.Time("2024-01-01T12:00:00", format="isot", scale="utc")] * shape[0]
    )
    l1detectorgwcentroid["track_centroids"] = kwargs.get("track_centroids", np.zeros(shape[1:], dtype=np.float32))
    l1detectorgwcentroid["track_centroid_errs"] = kwargs.get("track_centroid_errs", np.zeros(shape[1:], dtype=np.float32))
    l1detectorgwcentroid["track_centroid_quality"] = kwargs.get(
        "track_centroid_quality", np.array(["?"] * shape[0], dtype="<U40")
    )
    l1detectorgwcentroid["track_centroid_times"] = kwargs.get(
        "track_centroid_times", [time.Time("2024-01-01T12:00:00", format="isot", scale="utc")] * shape[0]
    )

    if mode == "WSM":
        l1detectorgwcentroid["edge_acq_centroids"] = kwargs.get("edge_acq_centroids", np.zeros(shape[1:], dtype=np.float32))
        l1detectorgwcentroid["edge_acq_centroid_errs"] = kwargs.get(
            "edge_acq_centroid_errs", np.zeros(shape[1:], dtype=np.float32)
        )
        l1detectorgwcentroid["edge_acq_centroid_quality"] = kwargs.get(
            "edge_acq_centroid_quality", np.array(["?"] * shape[0], dtype="<U40")
        )
        l1detectorgwcentroid["edge_acq_centroid_times"] = kwargs.get(
            "edge_acq_centroid_times", [time.Time("2024-01-01T12:00:00", format="isot", scale="utc")] * shape[0]
        )

    return l1detectorgwcentroid


def mk_l1_detector_guidewindow_array(*, name, shape=(16, 32, 32), **kwargs):
    """
    Create a dummy Level 1 detector guidewindow data arrays instance (or file) with
    arrays and valid values for attributes required by the schema.

    Parameters
    ----------
    name
        Name of array block to create.

    shape
        (optional, keyword-only) Shape of arrays in the model.

    filepath
        (optional, keyword-only) File name and path to write model to.

    Returns
    -------
    dict (defined by the l1_detector_guidewindow-1.0.0 schema with additional guidewindow metadata)
    """
    if len(shape) != 3:
        shape = (16, 32, 32)
        warnings.warn("Input shape must be 3D. Defaulting to (16, 32, 32)", UserWarning, stacklevel=2)

    l1detectorgwarr = {}

    l1detectorgwarr["pedestal_resultants"] = kwargs.get("pedestal_resultants", np.zeros(shape, dtype=np.uint16))
    l1detectorgwarr["signal_resultants"] = kwargs.get("signal_resultants", np.zeros(shape, dtype=np.uint16))
    l1detectorgwarr["lower_left_corners"] = kwargs.get("lower_left_corners", np.zeros(shape[1:], dtype=np.uint16))
    l1detectorgwarr["upper_right_corners"] = kwargs.get("upper_right_corners", np.zeros(shape[1:], dtype=np.uint16))
    l1detectorgwarr["pixel_offsets"] = kwargs.get("pixel_offsets", np.zeros(shape[0], dtype=np.uint16))
    l1detectorgwarr["reset_impacted_pairs"] = kwargs.get("reset_impacted_pairs", np.zeros(shape[0], dtype=bool))
    l1detectorgwarr["reset_read_flag"] = kwargs.get("reset_read_flag", np.zeros(shape[0], dtype=bool))
    l1detectorgwarr["pedestal_times"] = kwargs.get(
        "pedestal_times", [time.Time("2024-01-01T12:00:00", format="isot", scale="utc")] * shape[0]
    )
    l1detectorgwarr["signal_times"] = kwargs.get(
        "signal_times", [time.Time("2024-01-01T12:00:00", format="isot", scale="utc")] * shape[0]
    )
    l1detectorgwarr["sci_data_packet_counts"] = kwargs.get("sci_data_packet_counts", np.zeros(shape[1:], dtype=np.uint16))
    l1detectorgwarr["sce_status_flag"] = kwargs.get("sce_status_flag", np.zeros(shape[1:], dtype=np.uint8))
    l1detectorgwarr["gw_resultant_err_flag"] = kwargs.get("gw_resultant_err_flag", np.zeros(shape[1:], dtype=np.uint8))
    l1detectorgwarr["min_bind_flag"] = kwargs.get("min_bind_flag", np.zeros(shape[1:], dtype=np.uint8))
    l1detectorgwarr["max_bind_flag"] = kwargs.get("max_bind_flag", np.zeros(shape[1:], dtype=np.uint8))

    if name == "track_data":
        l1detectorgwarr["exposure_mapping"] = kwargs.get("exposure_mapping", np.zeros(shape[0], dtype=np.int16))

    return l1detectorgwarr


def mk_l1_detector_guidewindow(*, shape=(16, 32, 32), mode="WSM", filepath=None, **kwargs):
    """
    Create a dummy L1DetectorGuidewindow instance (or file) with arrays and valid values
    for attributes required by the schema.

    Parameters
    ----------
    shape
        (optional, keyword-only) Shape of arrays in the model.

    mode : string
        (optional, keyword-only) Mode of the instrument, image (WIM) or spectrograph (WSM).

    filepath
        (optional, keyword-only) File name and path to write model to.

    Returns
    -------
    roman_datamodels.stnode.L1DetectorGuidewindow
    """
    if len(shape) != 3:
        shape = (16, 32, 32)
        warnings.warn("Input shape must be 3D. Defaulting to (16, 32, 32)", UserWarning, stacklevel=2)

    if mode not in ["WIM", "WSM"]:
        mode = "WSM"
        warnings.warn("Mode must be in [WIM, WSM]", UserWarning, stacklevel=2)

    l1detectorgw = stnode.L1DetectorGuidewindow()
    l1detectorgw["meta"] = mk_l1_detector_guidewindow_meta(mode, **kwargs.get("meta", {}))

    l1detectorgw["amp33"] = mk_l1_detector_guidewindow_amp33(mode=mode, shape=shape, **kwargs.get("amp33", {}))
    l1detectorgw["centroid"] = mk_l1_detector_guidewindow_centroid(mode=mode, shape=shape, **kwargs.get("centroid", {}))

    l1detectorgw["acq_data"] = mk_l1_detector_guidewindow_array(name="acq_data", shape=shape, **kwargs.get("acq_data", {}))
    l1detectorgw["track_data"] = mk_l1_detector_guidewindow_array(name="track_data", shape=shape, **kwargs.get("track_data", {}))
    if mode == "WSM":
        l1detectorgw["edge_acq_data"] = mk_l1_detector_guidewindow_array(
            name="edge_acq_data", shape=shape, **kwargs.get("edge_acq_data", {})
        )

    return save_node(l1detectorgw, filepath=filepath)


def mk_mosaic_source_catalog(*, filepath=None, **kwargs):
    """
    Create a dummy Source Catalog instance (or file) with arrays and valid values
    for attributes required by the schema.

    Parameters
    ----------
    filepath
        (optional, keyword-only) File name and path to write model to.

    Returns
    -------
    roman_datamodels.stnode.MosaicSourceCatalog
    """
    source_catalog = stnode.MosaicSourceCatalog()

    if "source_catalog" in kwargs:
        source_catalog["source_catalog"] = kwargs["source_catalog"]
    else:
        source_catalog["source_catalog"] = source_catalog.create_fake_data().source_catalog

    source_catalog["meta"] = mk_mosaic_catalog_meta(**kwargs.get("meta", {}))

    return save_node(source_catalog, filepath=filepath)


def mk_forced_mosaic_source_catalog(*, filepath=None, **kwargs):
    """
    Create a dummy Source Catalog instance (or file) with arrays and valid values
    for attributes required by the schema.

    Parameters
    ----------
    filepath
        (optional, keyword-only) File name and path to write model to.

    Returns
    -------
    roman_datamodels.stnode.ForcedMosaicSourceCatalog
    """
    source_catalog = stnode.ForcedMosaicSourceCatalog()

    if "source_catalog" in kwargs:
        source_catalog["source_catalog"] = kwargs["source_catalog"]
    else:
        source_catalog["source_catalog"] = source_catalog.create_fake_data().source_catalog

    source_catalog["meta"] = mk_mosaic_catalog_meta(**kwargs.get("meta", {}))

    return save_node(source_catalog, filepath=filepath)


def mk_multiband_source_catalog(*, filepath=None, **kwargs):
    """
    Create a dummy Multiband Source Catalog instance (or file) with arrays and valid values
    for attributes required by the schema.

    Parameters
    ----------
    filepath
        (optional, keyword-only) File name and path to write model to.

    Returns
    -------
    roman_datamodels.stnode.MultibandSourceCatalog
    """
    source_catalog = stnode.MultibandSourceCatalog()

    if "source_catalog" in kwargs:
        source_catalog["source_catalog"] = kwargs["source_catalog"]
    else:
        source_catalog["source_catalog"] = source_catalog.create_fake_data().source_catalog

    source_catalog["meta"] = mk_mosaic_catalog_meta(**kwargs.get("meta", {}))

    return save_node(source_catalog, filepath=filepath)


def mk_mosaic_segmentation_map(*, filepath=None, shape=(4096, 4096), **kwargs):
    """
    Create a dummy Segmentation Map (or file) with arrays and valid values
    for attributes required by the schema.

    Parameters
    ----------
    filepath
        (optional, keyword-only) File name and path to write model to.

    shape
        (optional, keyword-only) Shape of arrays in the model.

    Returns
    -------
    roman_datamodels.stnode.SegmentationMap
    """
    if len(shape) > 2:
        shape = shape[1:3]

        warnings.warn(
            f"{MESSAGE} assuming the first entry is n_groups followed by y, x. The remaining is thrown out!",
            UserWarning,
            stacklevel=2,
        )

    segmentation_map = stnode.MosaicSegmentationMap()
    segmentation_map["data"] = kwargs.get("data", np.zeros(shape, dtype=np.uint32))
    segmentation_map["meta"] = mk_mosaic_catalog_meta(**kwargs.get("meta", {}))

    return save_node(segmentation_map, filepath=filepath)


def mk_image_source_catalog(*, filepath=None, **kwargs):
    """
    Create a dummy Source Catalog instance (or file) with arrays and valid values
    for attributes required by the schema.

    Parameters
    ----------
    filepath
        (optional, keyword-only) File name and path to write model to.

    Returns
    -------
    roman_datamodels.stnode.ImageSourceCatalog
    """
    source_catalog = stnode.ImageSourceCatalog()

    if "source_catalog" in kwargs:
        source_catalog["source_catalog"] = kwargs["source_catalog"]
    else:
        source_catalog["source_catalog"] = source_catalog.create_fake_data().source_catalog

    source_catalog["meta"] = mk_catalog_meta(**kwargs.get("meta", {}))

    return save_node(source_catalog, filepath=filepath)


def mk_forced_image_source_catalog(*, filepath=None, **kwargs):
    """
    Create a dummy Source Catalog instance (or file) with arrays and valid values
    for attributes required by the schema.

    Parameters
    ----------
    filepath
        (optional, keyword-only) File name and path to write model to.

    Returns
    -------
    roman_datamodels.stnode.ForcedImageSourceCatalog
    """
    source_catalog = stnode.ForcedImageSourceCatalog()

    if "source_catalog" in kwargs:
        source_catalog["source_catalog"] = kwargs["source_catalog"]
    else:
        source_catalog["source_catalog"] = source_catalog.create_fake_data().source_catalog

    source_catalog["meta"] = mk_catalog_meta(**kwargs.get("meta", {}))

    return save_node(source_catalog, filepath=filepath)


def mk_segmentation_map(*, filepath=None, shape=(4096, 4096), **kwargs):
    """
    Create a dummy Segmentation Map (or file) with arrays and valid values
    for attributes required by the schema.

    Parameters
    ----------
    filepath
        (optional, keyword-only) File name and path to write model to.

    shape
        (optional, keyword-only) Shape of arrays in the model.

    Returns
    -------
    roman_datamodels.stnode.SegmentationMap
    """
    if len(shape) > 2:
        shape = shape[1:3]

        warnings.warn(
            f"{MESSAGE} assuming the first entry is n_groups followed by y, x. The remaining is thrown out!",
            UserWarning,
            stacklevel=2,
        )

    segmentation_map = stnode.SegmentationMap()
    segmentation_map["data"] = kwargs.get("data", np.zeros(shape, dtype=np.uint32))
    segmentation_map["meta"] = mk_catalog_meta(**kwargs.get("meta", {}))

    return save_node(segmentation_map, filepath=filepath)


def mk_wfi_wcs(*, filepath=None, **kwargs):
    """
    Create dummy Level 2 WfiWcsModel instance with valid values for attributes required by the schema.

    Parameters
    ----------
    filepath : str
        (optional, keyword-only) File name and path to write model to.

    Returns
    -------
    roman_datamodels.stnode.WfiWcs
    """
    wfi_wcs = stnode.WfiWcs()
    wfi_wcs["meta"] = mk_wfi_wcs_common_meta(**kwargs.get("meta", {}))
    wfi_wcs["wcs_l2"] = mk_wcs()
    wfi_wcs["wcs_l1"] = mk_wcs()

    return save_node(wfi_wcs, filepath=filepath)
