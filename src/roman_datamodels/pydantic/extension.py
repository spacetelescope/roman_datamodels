from asdf.extension import Extension
from pydantic import RootModel

# Import all the models so they get registered
from roman_datamodels.datamodels import _generated  # noqa: F401

from .converter import RomanDataModelConverter, RomanRootModelConverter
from .datamodel import RomanDataModel

TAGGED_MODELS = {}
ROOT_MODELS = {}
for model_name in _generated.__all__:
    model = getattr(_generated, model_name)
    if issubclass(model, RomanDataModel) and model._tag_uri is not None:
        TAGGED_MODELS[model._tag_uri] = model

    if issubclass(model, RootModel) and hasattr(model, "_tag_uri") and model._tag_uri is not None:
        ROOT_MODELS[model._tag_uri] = model


# Add all the models to the converter
RomanDataModelConverter.from_registry(TAGGED_MODELS)
RomanRootModelConverter.from_registry(ROOT_MODELS)


class RomanPydanticExtension(Extension):
    extension_uri = "asdf://stsci.edu/datamodels/roman/manifests/datamodels-1.0"
    converters = [datamodel_converter := RomanDataModelConverter(), rootmodel_converter := RomanRootModelConverter()]
    tags = list(datamodel_converter.tags + rootmodel_converter.tags)
