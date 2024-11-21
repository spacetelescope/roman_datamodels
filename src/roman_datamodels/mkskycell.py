from datetime import datetime
import numpy as np
import asdf
import roman_datamodels.stnode as stnode

def mk_skycell(rawskycells_filename):
    meta = {
        "reftype": "SKYCELLS",
        "pedigree": "None",
        "description": "Skycells covering the celestial sphere",
        "author": "Dario Fadda",
        "useafter": "2024-01-01T00:00:00.000",
        "telescope": "ROMAN",
        "origin": "STSCI",
        "instrument": {
            "name": "WFI"
        },
        "nxy_skycell": 5000,
        "skycell_border_pixels": 100,
        "plate_scale": 0.55,

    }
    af = asdf.open(rawskycells_filename)
    projection_regions = np.array(af.tree['projection_regions'])
    skycells = np.array(af.tree['skycells'])
    skycellref = stnode.RomanSkycellsRef()
    skycellref['meta'] = meta
    skycellref['projection_regions'] = projection_regions
    skycellref['skycells'] = skycells
    skycellref['datamodel_name'] = "RomanSkycellsRefModel"
    afout = asdf.AsdfFile()
    afout.tree['roman'] = skycellref
    afout.write_to('skycell_reference.asdf')

