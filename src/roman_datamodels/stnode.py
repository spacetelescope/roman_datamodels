import warnings

from ._stnode import *  # noqa: F403

warnings.warn(
    "roman_datamodels.stnode as public API has been deprecated. Please use use the DataModel directly",
    DeprecationWarning,
    stacklevel=2,
)
