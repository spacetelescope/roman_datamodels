def get_extensions():
    """
    Get the extension instances for the various astropy
    extensions.  This method is registered with the
    `asdf.extension` entry point.

    Returns
    -------
    List[`asdf.extension.Extension`]
    """
    from .stnode import NODE_EXTENSIONS

    return NODE_EXTENSIONS
