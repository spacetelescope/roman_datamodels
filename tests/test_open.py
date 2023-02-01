import asdf
import numpy as np
import pytest
from astropy import units as u
from astropy.io import fits
from numpy.testing import assert_array_equal

from roman_datamodels import datamodels
from roman_datamodels import units as ru
from roman_datamodels.testing import utils


def test_asdf_file_input():
    tree = utils.mk_level2_image()
    with asdf.AsdfFile() as af:
        af.tree = {"roman": tree}
        model = datamodels.open(af)
        assert model.meta.telescope == "ROMAN"
        model.close()
        # should the asdf file be closed by model.close()?


def test_path_input(tmp_path):
    file_path = tmp_path / "test.asdf"
    with asdf.AsdfFile() as af:
        tree = utils.mk_level2_image()
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

    data = u.Quantity(np.random.uniform(size=(1024, 1024)).astype(np.float32), ru.electron / u.s, dtype=np.float32)

    with asdf.AsdfFile() as af:
        af.tree = {"roman": utils.mk_level2_image()}
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
        ru.electron / u.s,
        dtype=np.float32,
    )
    new_value = u.Quantity(1.0, ru.electron / u.s, dtype=np.float32)
    new_data = data.copy()
    new_data[6, 19] = new_value

    file_path = tmp_path / "test.asdf"
    with asdf.AsdfFile() as af:
        af.tree = {"roman": utils.mk_level2_image()}

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
        ru.electron / u.s,
        dtype=np.float32,
    )
    new_value = u.Quantity(1.0, ru.electron / u.s, dtype=np.float32)
    new_data = data.copy()
    new_data[6, 19] = new_value

    file_path = tmp_path / "test.asdf"
    with asdf.AsdfFile() as af:
        af.tree = {"roman": utils.mk_level2_image()}

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
