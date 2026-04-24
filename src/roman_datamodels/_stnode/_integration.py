from asdf.extension import ManifestExtension

from ._converters import SerializationNodeConverter, TaggedNodeConverter
from ._registry import MANIFEST_TAG_REGISTRY


def get_extensions():
    """
    Get the extension instances for the various astropy
    extensions.  This method is registered with the
    `asdf.extension` entry point.

    Returns
    -------
    List[`asdf.extension.Extension`]
    """
    return [
        ManifestExtension.from_uri(manifest_uri, converters=(SerializationNodeConverter(manifest_uri), TaggedNodeConverter()))
        for manifest_uri in MANIFEST_TAG_REGISTRY
    ]
