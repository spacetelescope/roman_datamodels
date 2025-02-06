import warnings

from ._maker_utils import *  # noqa: F403

_MSG = """
Use of `roman_datamodels.maker_utils` is deprecated and will be removed in the
future! Please simply initialize the model you want to use directly with no arguments,
e.g. `ImageModel()`. The model will then fill in the default values automatically
if you require them.
"""
warnings.warn(_MSG, DeprecationWarning, stacklevel=2)
