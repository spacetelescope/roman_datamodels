from roman_datamodels.stnode import FlushOptions

from ._base import save_node


def mk_tvac_groundtest(**kwargs):
    """
    Create a dummy GroundGroundtest instance with valid values for attributes
    required by the schema. Utilized by the model maker utilities below.

    This adds the tvac fields

    Returns
    -------
    roman_datamodels.stnode.TvacGroundtest
    """
    from roman_datamodels.nodes import TvacGroundtest

    ground = TvacGroundtest(kwargs)
    ground.flush(FlushOptions.EXTRA, recurse=True)

    return ground


def mk_tvac_common_meta(**kwargs):
    """
    Create a dummy common metadata dictionary with valid values for attributes

    Returns
    -------
    dict (defined by the ground_common-1.0.0 schema)
    """
    from roman_datamodels.nodes import TvacCommonMeta

    meta = TvacCommonMeta(kwargs)
    meta.flush(FlushOptions.EXTRA, recurse=True)

    return meta


def mk_tvac_meta(**kwargs):
    """
    Create a dummy tvac metadata dictionary with valid values for attributes

    Returns
    -------
    dict (defined by the tvac-1.0.0.meta schema)
    """
    from roman_datamodels.nodes.tvac.tvac import Tvac_Meta

    meta = Tvac_Meta(kwargs)
    meta.flush(FlushOptions.EXTRA, recurse=True)

    return meta


def mk_tvac(*, shape=None, filepath=None, **kwargs):
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
    from roman_datamodels.nodes import Tvac

    tvac = Tvac(kwargs, _array_shape=shape)
    tvac.flush(FlushOptions.EXTRA, recurse=True)

    return save_node(tvac, filepath=filepath)
