import warnings

from ._maker_utils import *  # noqa: F403

_MSG = """
Use of `roman_datamodels.maker_utils` is deprecated and will be removed in the
future! Please use the `.create_default()` constructor for the datamodel that
you wish to make a default datamodel for.
"""
warnings.warn(_MSG, DeprecationWarning, stacklevel=2)
