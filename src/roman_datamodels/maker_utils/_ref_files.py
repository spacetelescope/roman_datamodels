import asdf
import numpy as np
from astropy import units as u
from astropy.modeling import models

from roman_datamodels import stnode

from ._base import NONUM, NOSTR
from ._common_meta import mk_ref_common

__all__ = [
    "mk_flat",
    "mk_dark",
    "mk_distortion",
    "mk_gain",
    "mk_ipc",
    "mk_linearity",
    "mk_inverse_linearity",
    "mk_mask",
    "mk_pixelarea",
    "mk_wfi_img_photom",
    "mk_readnoise",
    "mk_saturation",
    "mk_superbias",
    "mk_refpix",
]


def mk_flat(shape=(4096, 4096), filepath=None):
    """
    Create a dummy Flat instance (or file) with arrays and valid values for attributes
    required by the schema.

    Parameters
    ----------
    shape
        (optional) Shape of arrays in the model.

    filepath
        (optional) File name and path to write model to.

    Returns
    -------
    roman_datamodels.stnode.FlatRef
    """
    meta = mk_ref_common()
    flatref = stnode.FlatRef()
    meta["reftype"] = "FLAT"
    flatref["meta"] = meta

    flatref["data"] = np.zeros(shape, dtype=np.float32)
    flatref["dq"] = np.zeros(shape, dtype=np.uint32)
    flatref["err"] = np.zeros(shape, dtype=np.float32)

    if filepath:
        af = asdf.AsdfFile()
        af.tree = {"roman": flatref}
        af.write_to(filepath)
    else:
        return flatref


def mk_dark(shape=(2, 4096, 4096), filepath=None):
    """
    Create a dummy Dark Current instance (or file) with arrays and valid values for attributes
    required by the schema.

    Parameters
    ----------
    shape
        (optional) Shape of arrays in the model.

    filepath
        (optional) File name and path to write model to.

    Returns
    -------
    roman_datamodels.stnode.DarkRef
    """
    meta = mk_ref_common()
    darkref = stnode.DarkRef()
    meta["reftype"] = "DARK"
    darkref["meta"] = meta
    exposure = {}
    exposure["ngroups"] = 6
    exposure["nframes"] = 8
    exposure["groupgap"] = 0
    exposure["type"] = "WFI_IMAGE"
    exposure["p_exptype"] = "WFI_IMAGE|WFI_GRISM|WFI_PRISM|"
    exposure["ma_table_name"] = NOSTR
    exposure["ma_table_number"] = NONUM
    darkref["meta"]["exposure"] = exposure

    darkref["data"] = u.Quantity(np.zeros(shape, dtype=np.float32), u.DN, dtype=np.float32)
    darkref["dq"] = np.zeros(shape[1:], dtype=np.uint32)
    darkref["err"] = u.Quantity(np.zeros(shape, dtype=np.float32), u.DN, dtype=np.float32)

    if filepath:
        af = asdf.AsdfFile()
        af.tree = {"roman": darkref}
        af.write_to(filepath)
    else:
        return darkref


def mk_distortion(filepath=None):
    """
    Create a dummy Distortion instance (or file) with arrays and valid values for attributes
    required by the schema.

    Parameters
    ----------

    filepath
        (optional) File name and path to write model to.

    Returns
    -------
    roman_datamodels.stnode.DistortionRef
    """
    meta = mk_ref_common()
    distortionref = stnode.DistortionRef()
    meta["reftype"] = "DISTORTION"
    distortionref["meta"] = meta

    distortionref["meta"]["input_units"] = u.pixel
    distortionref["meta"]["output_units"] = u.arcsec

    distortionref["coordinate_distortion_transform"] = models.Shift(1) & models.Shift(2)

    if filepath:
        af = asdf.AsdfFile()
        af.tree = {"roman": distortionref}
        af.write_to(filepath)
    else:
        return distortionref


def mk_gain(shape=(4096, 4096), filepath=None):
    """
    Create a dummy Gain instance (or file) with arrays and valid values for attributes
    required by the schema.

    Parameters
    ----------
    shape
        (optional) Shape of arrays in the model.

    filepath
        (optional) File name and path to write model to.

    Returns
    -------
    roman_datamodels.stnode.GainRef
    """
    meta = mk_ref_common()
    gainref = stnode.GainRef()
    meta["reftype"] = "GAIN"
    gainref["meta"] = meta

    gainref["data"] = u.Quantity(np.zeros(shape, dtype=np.float32), u.electron / u.DN, dtype=np.float32)

    if filepath:
        af = asdf.AsdfFile()
        af.tree = {"roman": gainref}
        af.write_to(filepath)
    else:
        return gainref


def mk_ipc(shape=(3, 3), filepath=None):
    """
    Create a dummy IPC instance (or file) with arrays and valid values for attributes
    required by the schema.

    Parameters
    ----------
    shape
        (optional) Shape of array in the model.

    filepath
        (optional) File name and path to write model to.

    Returns
    -------
    roman_datamodels.stnode.IpcRef
    """
    meta = mk_ref_common()
    ipcref = stnode.IpcRef()
    meta["reftype"] = "IPC"
    ipcref["meta"] = meta

    ipcref["data"] = np.zeros(shape, dtype=np.float32)
    ipcref["data"][int(np.floor(shape[0] / 2))][int(np.floor(shape[1] / 2))] = 1.0

    if filepath:
        af = asdf.AsdfFile()
        af.tree = {"roman": ipcref}
        af.write_to(filepath)
    else:
        return ipcref


def mk_linearity(shape=(2, 4096, 4096), filepath=None):
    """
    Create a dummy Linearity instance (or file) with arrays and valid values for attributes
    required by the schema.

    Parameters
    ----------
    shape
        (optional) Shape of arrays in the model.

    filepath
        (optional) File name and path to write model to.

    Returns
    -------
    roman_datamodels.stnode.LinearityRef
    """
    meta = mk_ref_common()
    linearityref = stnode.LinearityRef()
    meta["reftype"] = "LINEARITY"
    linearityref["meta"] = meta

    linearityref["meta"]["input_units"] = u.DN
    linearityref["meta"]["output_units"] = u.DN

    linearityref["dq"] = np.zeros(shape[1:], dtype=np.uint32)
    linearityref["coeffs"] = np.zeros(shape, dtype=np.float32)

    if filepath:
        af = asdf.AsdfFile()
        af.tree = {"roman": linearityref}
        af.write_to(filepath)
    else:
        return linearityref


def mk_inverse_linearity(shape=(2, 4096, 4096), filepath=None):
    """
    Create a dummy InverseLinearity instance (or file) with arrays and valid
    values for attributes required by the schema.

    Parameters
    ----------
    shape
        (optional) Shape of arrays in the model.

    filepath
        (optional) File name and path to write model to.

    Returns
    -------
    roman_datamodels.stnode.InverseLinearityRef
    """
    meta = mk_ref_common()
    inverselinearityref = stnode.InverseLinearityRef()
    meta["reftype"] = "INVERSELINEARITY"
    inverselinearityref["meta"] = meta

    inverselinearityref["meta"]["input_units"] = u.DN
    inverselinearityref["meta"]["output_units"] = u.DN

    inverselinearityref["dq"] = np.zeros(shape[1:], dtype=np.uint32)
    inverselinearityref["coeffs"] = np.zeros(shape, dtype=np.float32)

    if filepath:
        af = asdf.AsdfFile()
        af.tree = {"roman": inverselinearityref}
        af.write_to(filepath)
    else:
        return inverselinearityref


def mk_mask(shape=(4096, 4096), filepath=None):
    """
    Create a dummy Mask instance (or file) with arrays and valid values for attributes
    required by the schema.

    Parameters
    ----------
    shape
        (optional) Shape of arrays in the model.

    filepath
        (optional) File name and path to write model to.

    Returns
    -------
    roman_datamodels.stnode.MaskRef
    """
    meta = mk_ref_common()
    maskref = stnode.MaskRef()
    meta["reftype"] = "MASK"
    maskref["meta"] = meta

    maskref["dq"] = np.zeros(shape, dtype=np.uint32)

    if filepath:
        af = asdf.AsdfFile()
        af.tree = {"roman": maskref}
        af.write_to(filepath)
    else:
        return maskref


def mk_pixelarea(shape=(4096, 4096), filepath=None):
    """
    Create a dummy Pixelarea instance (or file) with arrays and valid values for attributes
    required by the schema.

    Parameters
    ----------
    shape
        (optional) Shape of arrays in the model.

    filepath
        (optional) File name and path to write model to.

    Returns
    -------
    roman_datamodels.stnode.PixelareaRef
    """
    meta = mk_ref_common()
    pixelarearef = stnode.PixelareaRef()
    meta["reftype"] = "AREA"
    meta["photometry"] = {
        "pixelarea_steradians": float(NONUM) * u.sr,
        "pixelarea_arcsecsq": float(NONUM) * u.arcsec**2,
    }
    pixelarearef["meta"] = meta

    pixelarearef["data"] = np.zeros(shape, dtype=np.float32)

    if filepath:
        af = asdf.AsdfFile()
        af.tree = {"roman": pixelarearef}
        af.write_to(filepath)
    else:
        return pixelarearef


def mk_wfi_img_photom(filepath=None):
    """
    Create a dummy WFI Img Photom instance (or file) with dictionary and valid values for attributes
    required by the schema.

    Parameters
    ----------
    filepath
        (optional) File name and path to write model to.

    Returns
    -------
    roman_datamodels.stnode.WfiImgPhotomRef
    """
    meta = mk_ref_common()
    wfi_img_photomref = stnode.WfiImgPhotomRef()
    meta["reftype"] = "PHOTOM"
    wfi_img_photomref["meta"] = meta

    wfi_img_photo_dict = {
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
    wfi_img_photomref["phot_table"] = wfi_img_photo_dict

    if filepath:
        af = asdf.AsdfFile()
        af.tree = {"roman": wfi_img_photomref}
        af.write_to(filepath)
    else:
        return wfi_img_photomref


def mk_readnoise(shape=(4096, 4096), filepath=None):
    """
    Create a dummy Readnoise instance (or file) with arrays and valid values for attributes
    required by the schema.

    Parameters
    ----------
    shape
        (optional) Shape of arrays in the model.

    filepath
        (optional) File name and path to write model to.

    Returns
    -------
    roman_datamodels.stnode.ReadnoiseRef
    """
    meta = mk_ref_common()
    readnoiseref = stnode.ReadnoiseRef()
    meta["reftype"] = "READNOISE"
    readnoiseref["meta"] = meta
    exposure = {}
    exposure["type"] = "WFI_IMAGE"
    exposure["p_exptype"] = "WFI_IMAGE|WFI_GRISM|WFI_PRISM|"
    readnoiseref["meta"]["exposure"] = exposure

    readnoiseref["data"] = u.Quantity(np.zeros(shape, dtype=np.float32), u.DN, dtype=np.float32)

    if filepath:
        af = asdf.AsdfFile()
        af.tree = {"roman": readnoiseref}
        af.write_to(filepath)
    else:
        return readnoiseref


def mk_saturation(shape=(4096, 4096), filepath=None):
    """
    Create a dummy Saturation instance (or file) with arrays and valid values for attributes
    required by the schema.

    Parameters
    ----------
    shape
        (optional) Shape of arrays in the model.

    filepath
        (optional) File name and path to write model to.

    Returns
    -------
    roman_datamodels.stnode.SaturationRef
    """
    meta = mk_ref_common()
    saturationref = stnode.SaturationRef()
    meta["reftype"] = "SATURATION"
    saturationref["meta"] = meta

    saturationref["dq"] = np.zeros(shape, dtype=np.uint32)
    saturationref["data"] = u.Quantity(np.zeros(shape, dtype=np.float32), u.DN, dtype=np.float32)

    if filepath:
        af = asdf.AsdfFile()
        af.tree = {"roman": saturationref}
        af.write_to(filepath)
    else:
        return saturationref


def mk_superbias(shape=(4096, 4096), filepath=None):
    """
    Create a dummy Superbias instance (or file) with arrays and valid values for attributes
    required by the schema.

    Parameters
    ----------
    shape
        (optional) Shape of arrays in the model.

    filepath
        (optional) File name and path to write model to.

    Returns
    -------
    roman_datamodels.stnode.SuperbiasRef
    """
    meta = mk_ref_common()
    superbiasref = stnode.SuperbiasRef()
    meta["reftype"] = "BIAS"
    superbiasref["meta"] = meta

    superbiasref["data"] = np.zeros(shape, dtype=np.float32)
    superbiasref["dq"] = np.zeros(shape, dtype=np.uint32)
    superbiasref["err"] = np.zeros(shape, dtype=np.float32)

    if filepath:
        af = asdf.AsdfFile()
        af.tree = {"roman": superbiasref}
        af.write_to(filepath)
    else:
        return superbiasref


def mk_refpix(shape=(32, 286721), filepath=None):
    """
    Create a dummy Refpix instance (or file) with arrays and valid values for attributes
    required by the schema.

    Note the default shape is intrinically connected to the FFT combined with specifics
    of the detector:
        - 32: is the number of detector channels (amp33 is a non-observation channel).
        - 286721 is more complex:
            There are 128 columns of the detector per channel, and for time read alignment
            purposes, these columns are padded by 12 additional columns. That is 140 columns
            per row. There are 4096 rows per channel. Each channel is then flattened into a
            1D array of 140 * 4096 = 573440 elements. Since the length is even the FFT of
            this array will be of length (573440 / 2) + 1 = 286721.
    Also, note the FFT gives a complex value and we are carrying full numerical precision
    which means it is a complex128.

    Parameters
    ----------
    shape
        (optional) Shape of arrays in the model.

    filepath
        (optional) File name and path to write model to.

    Returns
    -------
    roman_datamodels.stnode.RefPixRef
    """
    meta = mk_ref_common()
    refpix = stnode.RefpixRef()
    meta["reftype"] = "REFPIX"
    meta["input_units"] = u.DN
    meta["output_units"] = u.DN
    refpix["meta"] = meta

    refpix["gamma"] = np.zeros(shape, dtype=np.complex128)
    refpix["zeta"] = np.zeros(shape, dtype=np.complex128)
    refpix["alpha"] = np.zeros(shape, dtype=np.complex128)

    if filepath:
        af = asdf.AsdfFile()
        af.tree = {"roman": refpix}
        af.write_to(filepath)
    else:
        return refpix
