"""
This exists so that ASDF import performance is not adversely affected by roman_datamodels.
"""


def get_extensions():
    """
    Get the extension instances for the various astropy
    extensions.  This method is registered with the
    `asdf.extension` entry point.

    Returns
    -------
    List[`asdf.extension.Extension`]
    """
    from roman_datamodels.pydantic.extension import RomanPydanticExtension

    return [RomanPydanticExtension()]
