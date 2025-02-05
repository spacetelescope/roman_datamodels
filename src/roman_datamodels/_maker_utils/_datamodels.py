import warnings

from roman_datamodels.stnode import FlushOptions

from ._base import save_node


def mk_level1_science_raw(*, shape=None, dq=False, filepath=None, **kwargs):
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
    from roman_datamodels.nodes import WfiScienceRaw

    wfi_science_raw = WfiScienceRaw(kwargs, _array_shape=shape)
    wfi_science_raw.flush(FlushOptions.EXTRA, recurse=True)
    if not dq:
        del wfi_science_raw._data["resultantdq"]

    return save_node(wfi_science_raw, filepath=filepath)


def mk_level2_image(*, shape=None, n_groups=None, filepath=None, **kwargs):
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
    from roman_datamodels.nodes import WfiImage

    if n_groups is not None:
        shape = (n_groups, shape[0], shape[1])

    wfi_image = WfiImage(kwargs, _array_shape=shape)
    wfi_image.flush(FlushOptions.EXTRA, recurse=True)

    return save_node(wfi_image, filepath=filepath)


def mk_level3_mosaic(*, shape=None, n_images=None, filepath=None, **kwargs):
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
    from roman_datamodels.nodes import WfiMosaic

    if n_images is not None:
        shape = (n_images, shape[0], shape[1])

    wfi_mosaic = WfiMosaic(kwargs, _array_shape=shape)
    wfi_mosaic.flush(FlushOptions.EXTRA, recurse=True)

    return save_node(wfi_mosaic, filepath=filepath)


def mk_msos_stack(*, shape=None, filepath=None, **kwargs):
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
    from roman_datamodels.nodes import MsosStack

    msos_stack = MsosStack(kwargs, _array_shape=shape)
    msos_stack.flush(FlushOptions.EXTRA, recurse=True)
    return save_node(msos_stack, filepath=filepath)


def mk_ramp(*, shape=None, filepath=None, **kwargs):
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
    from roman_datamodels.nodes import Ramp

    ramp = Ramp(kwargs, _array_shape=shape)
    ramp.flush(FlushOptions.EXTRA, recurse=True)

    return save_node(ramp, filepath=filepath)


def mk_ramp_fit_output(*, shape=None, filepath=None, **kwargs):
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
    from roman_datamodels.nodes import RampFitOutput

    rampfitoutput = RampFitOutput(kwargs, _array_shape=shape)
    rampfitoutput.flush(FlushOptions.EXTRA, recurse=True)

    return save_node(rampfitoutput, filepath=filepath)


def mk_rampfitoutput(**kwargs):
    warnings.warn("mk_rampfitoutput is deprecated. Use mk_rampfit_output instead.", DeprecationWarning, stacklevel=2)

    return mk_ramp_fit_output(**kwargs)


def mk_associations(*, shape=None, filepath=None, **kwargs):
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
    from roman_datamodels.nodes import Associations

    associations = Associations(kwargs, _array_shape=shape)
    associations.flush(FlushOptions.EXTRA, recurse=True)

    return save_node(associations, filepath=filepath)


def mk_guidewindow(*, shape=None, filepath=None, **kwargs):
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
    from roman_datamodels.nodes import Guidewindow

    guidewindow = Guidewindow(kwargs, _array_shape=shape)
    guidewindow.flush(FlushOptions.EXTRA, recurse=True)

    return save_node(guidewindow, filepath=filepath)


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
    from roman_datamodels.nodes import MosaicSourceCatalog

    source_catalog = MosaicSourceCatalog(kwargs)
    source_catalog.flush(FlushOptions.EXTRA, recurse=True)

    return save_node(source_catalog, filepath=filepath)


def mk_mosaic_segmentation_map(*, filepath=None, shape=None, **kwargs):
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
    from roman_datamodels.nodes import MosaicSegmentationMap

    segmentation_map = MosaicSegmentationMap(kwargs, _array_shape=shape)
    segmentation_map.flush(FlushOptions.EXTRA, recurse=True)

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
    from roman_datamodels.nodes import ImageSourceCatalog

    source_catalog = ImageSourceCatalog(kwargs)
    source_catalog.flush(FlushOptions.EXTRA, recurse=True)

    return save_node(source_catalog, filepath=filepath)


def mk_segmentation_map(*, filepath=None, shape=None, **kwargs):
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
    from roman_datamodels.nodes import SegmentationMap

    segmentation_map = SegmentationMap(kwargs, _array_shape=shape)
    segmentation_map.flush(FlushOptions.EXTRA, recurse=True)

    return save_node(segmentation_map, filepath=filepath)
