import io
import numpy as np
import pytest
import astropy.table as astrotab
import pyarrow.parquet as pq

from roman_datamodels import datamodels
from roman_datamodels import maker_utils as utils

source_catalogs = [
    (datamodels.ImageSourceCatalogModel, utils.mk_image_source_catalog),
    (datamodels.MosaicSourceCatalogModel, utils.mk_mosaic_source_catalog),
]

@pytest.mark.parametrize(("catalog_class","mk_catalog"), source_catalogs)
def test_source_catalog(catalog_class, mk_catalog):
    sc_node = mk_catalog(save=False)
    sc_dm = catalog_class(sc_node)
    bio = io.BytesIO()
    sc_dm.to_parquet(file=bio)
    bio.seek(0)

    ptab = astrotab.Table.read(bio, format='parquet')
    # Compare columns
    assert np.all(ptab["a"] == sc_dm.source_catalog["a"])
    assert np.all(ptab["b"] == sc_dm.source_catalog["b"])

    bio.seek(0)
    # Spot check metadata.
    par_schema = pq.read_schema(bio)
    tabmeta = par_schema.metadata
    assert(tabmeta[b'roman.meta.telescope'] == sc_dm.meta.telescope.encode('ascii'))
    # Spot check column metadata.
    assert(par_schema.field('a').metadata[b'unit'] == str(sc_dm.source_catalog['a'].unit).encode('ascii'))
