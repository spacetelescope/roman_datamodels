import warnings

from ._maker_utils import *  # noqa: F403

warnings.warn(
    "roman_datamodels.maker_utils is deprecated. Please use DataModel.create_minimal or DataModel.create_fake_data",
    DeprecationWarning,
    stacklevel=2,
)
