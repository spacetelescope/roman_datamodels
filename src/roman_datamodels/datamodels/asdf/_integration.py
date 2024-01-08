"""
This exists so that ASDF import performance is not adversely affected by roman_datamodels.
"""
__all__ = ["get_extensions"]


def get_extensions():
    """
    Get the extension instances for the various astropy
    extensions.  This method is registered with the
    `asdf.extension` entry point.

    Returns
    -------
    List[`asdf.extension.Extension`]
    """
    from ._extension import RomanPydanticExtension

    return [RomanPydanticExtension()]
