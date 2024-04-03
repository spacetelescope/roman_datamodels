import warnings
from pathlib import Path

import asdf
import numpy as np
import pytest
from astropy import units as u
from astropy.io import fits
from astropy.utils import minversion
from numpy.testing import assert_array_equal

from roman_datamodels import datamodels
from roman_datamodels import maker_utils as utils
from roman_datamodels import stnode
from roman_datamodels.testing import assert_node_equal


def test_asdf_file_input():
    tree = utils.mk_level2_image(shape=(8, 8))
    with asdf.AsdfFile() as af:
        af.tree = {"roman": tree}
        model = datamodels.open(af)
        assert model.meta.telescope == "ROMAN"
        model.close()
        # should the asdf file be closed by model.close()?


@pytest.mark.skipif(
    minversion(asdf, "3.dev"),
    reason="asdf >= 3.0 has no AsdfInFits support",
)
def test_asdf_in_fits_error(tmp_path):
    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            category=asdf.exceptions.AsdfDeprecationWarning,
            message=r"AsdfInFits has been deprecated.*",
        )
        from asdf.fits_embed import AsdfInFits
    from astropy.io import fits

    fn = tmp_path / "AsdfInFits.fits"

    # generate an AsdfInFits file
    hdulist = fits.HDUList()
    tree = {"roman": []}
    ff = AsdfInFits(hdulist, tree)
    ff.write_to(fn, overwrite=True)

    # attempt to open it with datamodels, verify error
    with pytest.raises(TypeError, match=r"Roman datamodels does not accept FITS files or objects"):
        with datamodels.open(fn):
            pass


def test_path_input(tmp_path):
    file_path = tmp_path / "test.asdf"
    with asdf.AsdfFile() as af:
        tree = utils.mk_level2_image(shape=(8, 8))
        af.tree = {"roman": tree}
        af.write_to(file_path)

    # Test with PurePath input:
    with datamodels.open(file_path) as model:
        assert model.meta.telescope == "ROMAN"
        af = model._asdf

    # When open creates the file pointer, it should be
    # closed when the model is closed:
    assert af._closed

    # Test with string input:
    with datamodels.open(str(file_path)) as model:
        assert model.meta.telescope == "ROMAN"
        af = model._asdf

    assert af._closed

    # Appropriate error when file is missing:
    with pytest.raises(FileNotFoundError):
        with datamodels.open(tmp_path / "missing.asdf"):
            pass


def test_model_input(tmp_path):
    file_path = tmp_path / "test.asdf"

    data = u.Quantity(np.random.default_rng(42).uniform(size=(4, 4)).astype(np.float32), u.DN / u.s, dtype=np.float32)

    with asdf.AsdfFile() as af:
        af.tree = {"roman": utils.mk_level2_image(shape=(8, 8))}
        af.tree["roman"].meta["bozo"] = "clown"
        af.tree["roman"].data = data
        af.write_to(file_path)

    original_model = datamodels.open(file_path)
    reopened_model = datamodels.open(original_model)

    # It's essential that we get a new instance so that the original
    # model can be closed without impacting the new model.
    assert reopened_model is not original_model

    assert_array_equal(original_model.data, data)
    original_model.close()
    assert_array_equal(reopened_model.data, data)
    reopened_model.close()


def test_invalid_input():
    with pytest.raises(TypeError):
        datamodels.open(fits.HDUList())


def test_memmap(tmp_path):
    data = u.Quantity(
        np.zeros(
            (
                400,
                400,
            ),
            dtype=np.float32,
        ),
        u.DN / u.s,
        dtype=np.float32,
    )
    new_value = u.Quantity(1.0, u.DN / u.s, dtype=np.float32)
    new_data = data.copy()
    new_data[6, 19] = new_value

    file_path = tmp_path / "test.asdf"
    with asdf.AsdfFile() as af:
        af.tree = {"roman": utils.mk_level2_image(shape=(8, 8))}

        af.tree["roman"].data = data
        af.write_to(file_path)

    # Since quantities don't inherit from np.memmap we have to test they are effectively
    # memapped.
    # rw mode needed because we have to test the memmap by manipulating the data on disk.
    with datamodels.open(file_path, memmap=True, mode="rw") as model:
        # Test value before change
        assert (model.data == data).all()
        assert model.data[6, 19] != new_value

        # Change value (full assignment to avoid segfault)
        model.data[6, 19] = new_value

        # Test value after change
        assert model.data[6, 19] == new_value
        assert (model.data == new_data).all()
        assert (model.data != data).any()
        assert (data != new_data).any()

    # Test that the file was modified without pushing an update to it
    with datamodels.open(file_path, memmap=True, mode="rw") as model:
        assert model.data[6, 19] == new_value
        assert (model.data == new_data).all()


@pytest.mark.parametrize(
    "kwargs",
    [
        {"memmap": False},  # explicit False
        {},  # default
    ],
)
def test_no_memmap(tmp_path, kwargs):
    data = u.Quantity(
        np.zeros(
            (
                400,
                400,
            ),
            dtype=np.float32,
        ),
        u.DN / u.s,
        dtype=np.float32,
    )
    new_value = u.Quantity(1.0, u.DN / u.s, dtype=np.float32)
    new_data = data.copy()
    new_data[6, 19] = new_value

    file_path = tmp_path / "test.asdf"
    with asdf.AsdfFile() as af:
        af.tree = {"roman": utils.mk_level2_image(shape=(8, 8))}

        af.tree["roman"].data = data
        af.write_to(file_path)

    # Since quantities don't inherit from np.memmap we have to test they are effectively
    # memapped.
    # rw mode needed because we have to test the memmap by manipulating the data on disk.
    with datamodels.open(file_path, mode="rw", **kwargs) as model:
        # Test value before change
        assert (model.data == data).all()
        assert model.data[6, 19] != new_value

        # Change value (full assignment to avoid segfault)
        model.data[6, 19] = new_value

        # Test value after change
        assert model.data[6, 19] == new_value
        assert (model.data == new_data).all()
        assert (model.data != data).any()
        assert (data != new_data).any()

    # Test that the file was modified without pushing an update to it
    with datamodels.open(file_path, mode="rw", **kwargs) as model:
        assert model.data[6, 19] != new_value
        assert (model.data == data).all()


@pytest.mark.parametrize("node_class", [node for node in datamodels.MODEL_REGISTRY])
@pytest.mark.filterwarnings("ignore:This function assumes shape is 2D")
@pytest.mark.filterwarnings("ignore:Input shape must be 5D")
def test_node_round_trip(tmp_path, node_class):
    file_path = tmp_path / "test.asdf"

    # Create/return a node and write it to disk, then check if the node round trips
    node = utils.mk_node(node_class, filepath=file_path, shape=(2, 8, 8))
    with asdf.open(file_path) as af:
        assert_node_equal(af.tree["roman"], node)


@pytest.mark.parametrize("node_class", [node for node in datamodels.MODEL_REGISTRY])
@pytest.mark.filterwarnings("ignore:This function assumes shape is 2D")
@pytest.mark.filterwarnings("ignore:Input shape must be 5D")
def test_opening_model(tmp_path, node_class):
    file_path = tmp_path / "test.asdf"

    # Create a node and write it to disk
    utils.mk_node(node_class, filepath=file_path, shape=(2, 8, 8))

    # Opened saved file as a datamodel
    with datamodels.open(file_path) as model:
        # Check that some of read data is correct
        if node_class == stnode.Associations:
            assert model.asn_type == "image"
        elif node_class == stnode.WfiMosaic:
            assert model.meta.basic.optical_element == "F158"
        elif node_class in (stnode.SegmentationMap, stnode.SourceCatalog):
            assert model.meta.optical_element == "F158"
        elif node_class in (stnode.MosaicSegmentationMap, stnode.MosaicSourceCatalog):
            assert hasattr(model.meta, "basic")
        else:
            assert model.meta.instrument.optical_element == "F158"

        # Check that the model is the correct type
        assert isinstance(model, datamodels.MODEL_REGISTRY[node_class])


def test_read_pattern_properties():
    """
    Regression test for reading pattern properties
    """

    from roman_datamodels.datamodels import open as rdm_open

    # This file has been modified by hand to break the `photmjsr` value
    with pytest.raises(asdf.ValidationError):
        rdm_open(Path(__file__).parent / "data" / "photmjsm.asdf")


def test_rdm_open_non_datamodel():
    from roman_datamodels.datamodels import open as rdm_open

    with pytest.raises(TypeError, match=r"Unknown datamodel type: .*"):
        rdm_open(Path(__file__).parent / "data" / "not_a_datamodel.asdf")
