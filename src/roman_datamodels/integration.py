def get_extensions():
    """
    Get the extension instances for the various astropy
    extensions.  This method is registered with the
    asdf.extensions entry point.

    Returns
    -------
    list of asdf.extension.Extension
    """
    from . import extensions
    return extensions.DATAMODEL_EXTENSIONS
