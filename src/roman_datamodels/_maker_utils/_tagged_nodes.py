from roman_datamodels import stnode

from ._base import NONUM


def mk_photometry(**kwargs):
    """
    Create a dummy Photometry instance with valid values for attributes
    required by the schema. Utilized by the model maker utilities below.

    Returns
    -------
    roman_datamodels.stnode.Photometry
    """
    phot = stnode.Photometry()
    phot["conversion_megajanskys"] = kwargs.get("conversion_megajanskys", NONUM)
    phot["conversion_megajanskys_uncertainty"] = kwargs.get("conversion_megajanskys_uncertainty", NONUM)
    phot["pixel_area"] = kwargs.get("pixel_area", NONUM)

    return phot


def mk_resample(**kwargs):
    """
    Create a dummy Resample instance with valid values for attributes
    required by the schema. Utilized by the model maker utilities below.

    Returns
    -------
    roman_datamodels.stnode.Resample
    """
    res = stnode.Resample()
    res["good_bits"] = kwargs.get("good_bits", "NA")
    res["members"] = kwargs.get("members", [])
    res["pixel_scale_ratio"] = kwargs.get("pixel_scale_ratio", NONUM)
    res["pixfrac"] = kwargs.get("pixfrac", NONUM)
    res["pointings"] = kwargs.get("pointings", -1 * NONUM)
    res["product_exposure_time"] = kwargs.get("product_exposure_time", -1 * NONUM)
    res["weight_type"] = kwargs.get("weight_type", "exptime")

    return res


def mk_cal_logs(**kwargs):
    """
    Create a dummy CalLogs instance with valid values for attributes
    required by the schema.

    Returns
    -------
    roman_datamodels.stnode.CalLogs
    """
    return stnode.CalLogs(
        kwargs.get(
            "cal_logs",
            [
                "2021-11-15T09:15:07.12Z :: FlatFieldStep :: INFO :: Completed",
                "2021-11-15T10:22.55.55Z :: RampFittingStep :: WARNING :: Wow, lots of Cosmic Rays detected",
            ],
        )
    )


def mk_source_catalog(**kwargs):
    """
    Create a dummy Source Catalog instance with valid values for attributes
    required by the schema. Utilized by the model maker utilities below.

    Returns
    -------
    roman_datamodels.stnode.SourceCatalog
    """
    sd = stnode.SourceCatalog()
    sd["tweakreg_catalog_name"] = kwargs.get("tweakreg_catalog_name", "catalog")

    return sd
