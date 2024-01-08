from asdf.extension import Extension
from pydantic import RootModel

from roman_datamodels.core import RomanDataModel

# Import all the models so they get registered
from . import _generated  # noqa: F401
from .converter import RomanDataModelConverter, RomanRootModelConverter

# Populate dictionaries to register into the converters
_TAGGED_MODELS = {}
_ROOT_MODELS = {}
for model_name in _generated.__all__:
    model = getattr(_generated, model_name)
    if issubclass(model, RomanDataModel) and model.tag_uri is not None:
        _TAGGED_MODELS[model.tag_uri] = model

    if issubclass(model, RootModel) and hasattr(model, "tag_uri") and model.tag_uri is not None:
        _ROOT_MODELS[model.tag_uri] = model


# Add all the models to the converter
RomanDataModelConverter.from_registry(_TAGGED_MODELS)
RomanRootModelConverter.from_registry(_ROOT_MODELS)


class RomanPydanticExtension(Extension):
    extension_uri = "asdf://stsci.edu/datamodels/roman/manifests/datamodels-1.0"
    converters = [datamodel_converter := RomanDataModelConverter(), rootmodel_converter := RomanRootModelConverter()]
    tags = list(datamodel_converter.tags + rootmodel_converter.tags)
