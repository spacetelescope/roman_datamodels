from asdf.extension import Extension

# Import all the models so they get registered
from . import _generated  # noqa: F401
from .converter import RomanDataModelConverter
from .datamodel import RomanDataModel

TAGGED_MODELS = {}
for model_name in _generated.__all__:
    model = getattr(_generated, model_name)
    if issubclass(model, RomanDataModel) and model._tag_uri is not None:
        TAGGED_MODELS[model._tag_uri] = model

# Add all the models to the converter
RomanDataModelConverter.from_registry(TAGGED_MODELS)


class RomanPydanticExtension(Extension):
    extension_uri = "asdf://stsci.edu/datamodels/roman/manifests/datamodels-1.0"
    converters = [RomanDataModelConverter()]
    tags = list(TAGGED_MODELS.keys())
