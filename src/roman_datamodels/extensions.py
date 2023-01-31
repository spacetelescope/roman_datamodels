from asdf.extension import ManifestExtension

from .stnode import TaggedListNodeConverter, TaggedObjectNodeConverter, TaggedScalarNodeConverter, UnitConverter

DATAMODEL_CONVERTERS = [
    TaggedObjectNodeConverter(),
    TaggedListNodeConverter(),
    TaggedScalarNodeConverter(),
    UnitConverter(),
]

DATAMODEL_EXTENSIONS = [
    ManifestExtension.from_uri("asdf://stsci.edu/datamodels/roman/manifests/datamodels-1.0", converters=DATAMODEL_CONVERTERS)
]
