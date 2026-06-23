def get_extensions():
    """
    Get the extension instances for the various astropy
    extensions.  This method is registered with the
    `asdf.extension` entry point.

    Returns
    -------
    List[`asdf.extension.Extension`]
    """
    # Importing from ._stnode itself so that all the dynamically created
    #   objects are in fact created
    from ._stnode import NODE_EXTENSIONS

    return list(NODE_EXTENSIONS.values())
