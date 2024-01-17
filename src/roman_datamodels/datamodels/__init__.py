from roman_datamodels.core import DataModel  # noqa: F403, F401
from roman_datamodels.core import open  # noqa: F403, F401

# Import all the data model objects
#    In a try/except, block to catch when when the generated code is not available
#    such as when the generator is run during installation.
try:
    from ._generated import *  # noqa: F403
except ImportError:
    import warnings

    warnings.warn("Failed to import the data model objects, attempting to run the generator.")

    from roman_datamodels.generator import setup_files

    setup_files()

    from ._generated import *  # noqa: F403


def __getattr__(name):
    """Allow use of deprecated model names"""
    import warnings

    # These models have have be renamed to be consistent with their schema names,
    #    but we want to allow the old names to be used for now.
    deprecated_models = {
        "ImageModel": WfiImageModel,  # noqa: F405
        "MosaicModel": WfiMosaicModel,  # noqa: F405
        "ScienceRawModel": WfiScienceRawModel,  # noqa: F405
    }

    if name in deprecated_models:
        warnings.warn(
            f"Use of deprecated model {name} is discouraged, use {deprecated_models[name].__name__} instead.", DeprecationWarning
        )
        return deprecated_models[name]
