from roman_datamodels.stnode import FlushOptions

from ._base import save_node

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
    "mk_pixelarea",
    "mk_readnoise",
    "mk_refpix",
    "mk_saturation",
    "mk_superbias",
    "mk_wfi_img_photom",
]

OPT_ELEM = ("F062", "F087", "F106", "F129", "F146", "F158", "F184", "F213", "GRISM", "PRISM", "DARK")


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
    from roman_datamodels.nodes import AbvegaoffsetRef

    abvegaref = AbvegaoffsetRef(kwargs)
    abvegaref.flush(FlushOptions.EXTRA, recurse=True)

    return save_node(abvegaref, filepath=filepath)


def mk_apcorr(*, shape=None, filepath=None, **kwargs):
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
    from roman_datamodels.nodes import ApcorrRef

    apcorrref = ApcorrRef(kwargs, _array_shape=shape)
    apcorrref.flush(FlushOptions.EXTRA, recurse=True)

    return save_node(apcorrref, filepath=filepath)


def mk_flat(*, shape=None, filepath=None, **kwargs):
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
    from roman_datamodels.nodes import FlatRef

    flatref = FlatRef(kwargs, _array_shape=shape)
    flatref.flush(FlushOptions.EXTRA, recurse=True)

    return save_node(flatref, filepath=filepath)


def mk_dark(*, shape=None, filepath=None, **kwargs):
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
    from roman_datamodels.nodes import DarkRef

    darkref = DarkRef(kwargs, _array_shape=shape)
    darkref.flush(FlushOptions.EXTRA, recurse=True)

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
    from roman_datamodels.nodes import DistortionRef

    distortionref = DistortionRef(kwargs)
    distortionref.flush(FlushOptions.EXTRA, recurse=True)

    return save_node(distortionref, filepath=filepath)


def mk_epsf(*, shape=None, filepath=None, **kwargs):
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
    from roman_datamodels.nodes import EpsfRef

    epsfref = EpsfRef(kwargs, _array_shape=shape)
    epsfref.flush(FlushOptions.EXTRA, recurse=True)

    return save_node(epsfref, filepath=filepath)


def mk_gain(*, shape=None, filepath=None, **kwargs):
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
    from roman_datamodels.nodes import GainRef

    gainref = GainRef(kwargs, _array_shape=shape)
    gainref.flush(FlushOptions.EXTRA, recurse=True)

    return save_node(gainref, filepath=filepath)


def mk_ipc(*, shape=None, filepath=None, **kwargs):
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
    from roman_datamodels.nodes import IpcRef

    ipcref = IpcRef(kwargs, _array_shape=shape)
    ipcref.flush(FlushOptions.EXTRA, recurse=True)

    return save_node(ipcref, filepath=filepath)


def mk_linearity(*, shape=None, filepath=None, **kwargs):
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
    from roman_datamodels.nodes import LinearityRef

    linearityref = LinearityRef(kwargs, _array_shape=shape)
    linearityref.flush(FlushOptions.EXTRA, recurse=True)

    return save_node(linearityref, filepath=filepath)


def mk_inverselinearity(*, shape=None, filepath=None, **kwargs):
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
    from roman_datamodels.nodes import InverselinearityRef

    inverselinearityref = InverselinearityRef(kwargs, _shape=shape)
    inverselinearityref.flush(FlushOptions.EXTRA, recurse=True)

    return save_node(inverselinearityref, filepath=filepath)


def mk_mask(*, shape=None, filepath=None, **kwargs):
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
    from roman_datamodels.nodes import MaskRef

    maskref = MaskRef(kwargs, _array_shape=shape)
    maskref.flush(FlushOptions.EXTRA, recurse=True)

    return save_node(maskref, filepath=filepath)


def mk_pixelarea(*, shape=None, filepath=None, **kwargs):
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
    from roman_datamodels.nodes import PixelareaRef

    pixelarearef = PixelareaRef(kwargs, _array_shape=shape)
    pixelarearef.flush(FlushOptions.EXTRA, recurse=True)

    return save_node(pixelarearef, filepath=filepath)


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
    from roman_datamodels.nodes import WfiImgPhotomRef

    wfi_img_photomref = WfiImgPhotomRef(kwargs)
    wfi_img_photomref.flush(FlushOptions.EXTRA, recurse=True)

    return save_node(wfi_img_photomref, filepath=filepath)


def mk_readnoise(*, shape=None, filepath=None, **kwargs):
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
    from roman_datamodels.nodes import ReadnoiseRef

    readnoiseref = ReadnoiseRef(kwargs, _array_shape=shape)
    readnoiseref.flush(FlushOptions.EXTRA, recurse=True)

    return save_node(readnoiseref, filepath=filepath)


def mk_saturation(*, shape=None, filepath=None, **kwargs):
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
    from roman_datamodels.nodes import SaturationRef

    saturationref = SaturationRef(kwargs, _array_shape=shape)
    saturationref.flush(FlushOptions.EXTRA, recurse=True)

    return save_node(saturationref, filepath=filepath)


def mk_superbias(*, shape=None, filepath=None, **kwargs):
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
    from roman_datamodels.nodes import SuperbiasRef

    superbiasref = SuperbiasRef(kwargs, _array_shape=shape)
    superbiasref.flush(FlushOptions.EXTRA, recurse=True)

    return save_node(superbiasref, filepath=filepath)


def mk_refpix(*, shape=None, filepath=None, **kwargs):
    """
    Create a dummy Refpix instance (or file) with arrays and valid values for
    attributes required by the schema.

    Note the default shape is intrinically connected to the FFT combined with
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
    from roman_datamodels.nodes import RefpixRef

    refpix = RefpixRef(kwargs, _array_shape=shape)
    refpix.flush(FlushOptions.EXTRA, recurse=True)

    return save_node(refpix, filepath=filepath)
