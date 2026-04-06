def get_extensions():
    """
    Get the extension instances for the various astropy
    extensions.  This method is registered with the
    `asdf.extension` entry point.

    Returns
    -------
    List[`asdf.extension.Extension`]
    """
    # Importing from the _stnode subpackage itself as that subpackage
    #   forces the creation of all of the dynamically generated objects
    from roman_datamodels._stnode import REGISTRY

    return REGISTRY.asdf_extensions
