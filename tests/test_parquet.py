import astropy.table as astrotab
import numpy as np
import pyarrow.parquet as pq
import pytest

from roman_datamodels import datamodels
from roman_datamodels import maker_utils as utils

source_catalogs = [
    (datamodels.ImageSourceCatalogModel, utils.mk_image_source_catalog),
    (datamodels.MosaicSourceCatalogModel, utils.mk_mosaic_source_catalog),
]


@pytest.mark.parametrize(("catalog_class", "mk_catalog"), source_catalogs)
def test_source_catalog(catalog_class, mk_catalog, tmp_path):
    sc_node = mk_catalog(save=False)
    sc_dm = catalog_class(sc_node)

    sc_dm.source_catalog["a"].description = "a description"
    sc_dm.source_catalog["b"].description = "b description"

    test_path = tmp_path / "test.parquet"
    sc_dm.to_parquet(test_path)

    ptab = astrotab.Table.read(test_path, format="parquet")

    # check that tables round trip
    for cname in ["a", "b"]:
        assert ptab[cname].description == sc_dm.source_catalog[cname].description
        assert ptab[cname].unit == sc_dm.source_catalog[cname].unit
        assert np.all(ptab[cname] == sc_dm.source_catalog[cname])

    # Spot check metadata.
    par_schema = pq.read_schema(test_path)
    tabmeta = par_schema.metadata
    assert tabmeta[b"roman.meta.telescope"] == sc_dm.meta.telescope.encode("ascii")
    # Spot check column metadata.
    assert par_schema.field("a").metadata[b"unit"] == str(sc_dm.source_catalog["a"].unit).encode("ascii")

    # Check that save() works
    test_path2 = tmp_path / "test2.parquet"
    sc_dm.save(test_path2)
    with open(test_path2, "rb") as f:
        assert f.read(4) == b"PAR1"
