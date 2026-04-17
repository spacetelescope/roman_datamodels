def get_extensions():
    """
    Get the extension instances for the various astropy
    extensions.  This method is registered with the
    `asdf.extension` entry point.

    Returns
    -------
    List[`asdf.extension.Extension`]
    """
    from asdf.extension import ManifestExtension

    from roman_datamodels import _stnode  # noqa: F401

    from ._converters import SerializationNodeConverter, TaggedNodeConverter
    from ._tagged import SerializationNode

    # assert False, f"{list(node._manifest_uri for node in SerializationNode.__subclasses__())}"

    return [
        ManifestExtension.from_uri(
            manifest_uri=node_cls.manifest_uri,
            converters=(SerializationNodeConverter(node_cls), TaggedNodeConverter()),
        )
        for node_cls in SerializationNode.__subclasses__()
    ]
