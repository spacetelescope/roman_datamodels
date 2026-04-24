from asdf.extension import ManifestExtension

from ._converters import SerializationNodeConverter, TaggedNodeConverter
from ._manifest import MANIFEST_TAG_REGISTRY
from ._tagged import SerializationNode


def get_extensions():
    """
    Get the extension instances for the various astropy
    extensions.  This method is registered with the
    `asdf.extension` entry point.

    Returns
    -------
    List[`asdf.extension.Extension`]
    """
    serialization_node_by_manifest = {}
    extensions = []
    for manifest_uri, tags in MANIFEST_TAG_REGISTRY.items():
        serialization_node = SerializationNode._factory(manifest_uri)
        serialization_node_by_manifest[manifest_uri] = serialization_node
        extensions.append(
            ManifestExtension.from_uri(
                manifest_uri,
                converters=(
                    SerializationNodeConverter(serialization_node, tags),
                    TaggedNodeConverter(serialization_node_by_manifest),
                ),
            )
        )
    return extensions
