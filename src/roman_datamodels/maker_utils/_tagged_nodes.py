from astropy import units as u

from roman_datamodels import stnode

from ._base import NONUM


def mk_photometry():
    """
    Create a dummy Photometry instance with valid values for attributes
    required by the schema. Utilized by the model maker utilities below.

    Returns
    -------
    roman_datamodels.stnode.Photometry
    """
    phot = stnode.Photometry()
    phot["conversion_microjanskys"] = NONUM * u.uJy / u.sr
    phot["conversion_megajanskys"] = NONUM * u.MJy / u.sr
    phot["pixelarea_steradians"] = NONUM * u.sr
    phot["pixelarea_arcsecsq"] = NONUM * u.arcsec**2
    phot["conversion_microjanskys_uncertainty"] = NONUM * u.uJy / u.sr
    phot["conversion_megajanskys_uncertainty"] = NONUM * u.MJy / u.sr

    return phot


def mk_cal_logs():
    """
    Create a dummy CalLogs instance with valid values for attributes
    required by the schema.

    Returns
    -------
    roman_datamodels.stnode.CalLogs
    """
    return stnode.CalLogs(
        [
            "2021-11-15T09:15:07.12Z :: FlatFieldStep :: INFO :: Completed",
            "2021-11-15T10:22.55.55Z :: RampFittingStep :: WARNING :: Wow, lots of Cosmic Rays detected",
        ]
    )


def mk_resample():
    """
    Create a dummy Resample instance with valid values for attributes
    required by the schema. Utilized by the model maker utilities below.

    Returns
    -------
    roman_datamodels.stnode.Resample
    """
    res = stnode.Resample()
    res["pixel_scale_ratio"] = NONUM
    res["pixfrac"] = NONUM
    res["pointings"] = -1 * NONUM
    res["product_exposure_time"] = -1 * NONUM
    res["weight_type"] = "exptime"

    return res
