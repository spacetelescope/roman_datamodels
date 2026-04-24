from asdf.extension import ManifestExtension

from ._converters import SerializationNodeConverter
from ._registry import MANIFEST_TAG_REGISTRY, NODE_CONVERTERS


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
        ManifestExtension.from_uri(
            manifest_uri, converters=(SerializationNodeConverter(manifest_uri), *tuple(NODE_CONVERTERS.values()))
        )
        for manifest_uri in MANIFEST_TAG_REGISTRY
    ]
