import numpy as np
from astropy.time import Time
import asdf
import roman_datamodels.stnode as stnode

def mk_skycell(output_filename,
               projection_regions,
               skycells,
               author,
               useafter,
               plate_scale,
               border_pixels):
    """
    Create a skycell reference file.


    Parameters
    ----------
    output_filename : string.
        The name of the created reference file.
    projection_regions : numpy structure array.
        An array that defines the projection regions containing the fields as defined by
        the schema.
    skycells : numpy structure array.
        An array that defines all skycells containing the fields as defined by the schema.
    author : string.
        The name of the person creating the reference file.
    useafter : astropy.time.Time instance.
        The useafter date that CRDS requires.
    plate_scale: float.
        The plate scale of the pixel at the tangent point.
    border_pixels: integer.
        The number of pixels the skycells within a projection region overlap with adjacent
        skycells in the same projection region.
    """
    meta = {
        "reftype": "SKYCELLS",
        "pedigree": "GROUND",
        "description": "Skycells covering the celestial sphere",
        "author": author,
        "useafter": Time("2024-01-01T01:00:00.000"),
        "telescope": "ROMAN",
        "origin": "STSCI",
        "instrument": {
            "name": "WFI"
        },
        "nxy_skycell": 5000,
        "skycell_border_pixels": border_pixels,
        "plate_scale": plate_scale,
    }
    projection_regions = np.array(projection_regions)
    skycells = np.array(skycells)
    skycellref = stnode.RomanSkycellsRef()
    skycellref['meta'] = meta
    skycellref['projection_regions'] = projection_regions
    skycellref['skycells'] = skycells
    skycellref['datamodel_name'] = "RomanSkycellsRefModel"
    with asdf.AsdfFile() as afout:
        afout = asdf.AsdfFile()
        afout.tree['roman'] = skycellref
        afout.write_to(output_filename)
