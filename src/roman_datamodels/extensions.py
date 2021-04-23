from asdf.extension import ManifestExtension
from .stnode import TaggedObjectNodeConverter


DATAMODEL_CONVERTERS = [
    TaggedObjectNodeConverter(),
]

DATAMODEL_EXTENSIONS = [
    ManifestExtension.from_uri(
        "asdf://stsci.edu/datamodels/roman/manifests/datamodels-1.0",
        converters=DATAMODEL_CONVERTERS)
]
