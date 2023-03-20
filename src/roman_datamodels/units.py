import warnings

from astropy import units as u

warnings.warn(
    category=DeprecationWarning,
    message="The roman_datamodels.units module is deprecated. Use astropy.units instead.",
)

DN = u.DN
electron = u.electron

__all__ = ["DN", "electron"]
