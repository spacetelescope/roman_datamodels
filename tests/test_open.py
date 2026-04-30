import json
import os
from contextlib import nullcontext
from pathlib import Path

import asdf
import numpy as np
import pytest
from astropy.io import fits
from numpy.testing import assert_array_equal

from roman_datamodels import datamodels
from roman_datamodels._stnode import TaggedObjectNode, WfiImage, tagged_type
from roman_datamodels.datamodels._utils import _patch_meta_filename
from roman_datamodels.testing import assert_node_equal


def test_asdf_file_input():
    tree = WfiImage.create_fake_data()
    with asdf.AsdfFile() as af:
        af.tree = {"roman": tree}
        model = datamodels.open(af)
        assert model.meta.telescope == "ROMAN"
        model.close()
        # should the asdf file be closed by model.close()?


def test_path_input(tmp_path):
    file_path = tmp_path / "test.asdf"
    with asdf.AsdfFile() as af:
        tree = WfiImage.create_fake_data()
        af.tree = {"roman": tree}
        af.write_to(file_path)

    # Test with PurePath input:
    #     FilenameMismatchWarning should be raised, as we have not synced the filename
    with pytest.warns(datamodels.FilenameMismatchWarning), datamodels.open(file_path) as model:
        assert model.meta.telescope == "ROMAN"
        af = model._asdf

    # When open creates the file pointer, it should be
    # closed when the model is closed:
    assert af._closed

    # Test with string input:
    #     FilenameMismatchWarning should be raised, as we have not synced the filename
    with pytest.warns(datamodels.FilenameMismatchWarning), datamodels.open(str(file_path)) as model:
        assert model.meta.telescope == "ROMAN"
        af = model._asdf

    assert af._closed

    # Appropriate error when file is missing:
    with pytest.raises(FileNotFoundError):
        with datamodels.open(tmp_path / "missing.asdf"):
            pass


def test_model_input(tmp_path):
    file_path = tmp_path / "test.asdf"

    data = np.random.default_rng(42).uniform(size=(4, 4)).astype(np.float32)

    with asdf.AsdfFile() as af:
        af.tree = {"roman": WfiImage.create_fake_data()}
        af.tree["roman"].meta["bozo"] = "clown"
        af.tree["roman"].data = data
        af.write_to(file_path)

    # We have not set the filename so we should get a warning that it doesn't match
    with pytest.warns(datamodels.FilenameMismatchWarning):
        original_model = datamodels.open(file_path)

    reopened_model = datamodels.open(original_model)

    # It's essential that we get a new instance so that the original
    # model can be closed without impacting the new model.
    assert reopened_model is not original_model

    assert_array_equal(original_model.data, data)
    original_model.close()
    assert_array_equal(reopened_model.data, data)
    reopened_model.close()


def test_file_input(tmp_path):
    file_path = tmp_path / "test.asdf"
    tree = WfiImage.create_fake_data()
    with asdf.AsdfFile() as af:
        af.tree = {"roman": tree}
        af.write_to(file_path)
    with open(file_path, "rb") as f:
        with datamodels.open(f) as model:
            assert model.meta.telescope == "ROMAN"


def test_invalid_input():
    with pytest.raises(TypeError):
        datamodels.open(fits.HDUList())


def test_memmap(tmp_path):
    data = np.zeros(
        (
            400,
            400,
        ),
        dtype=np.float32,
    )
    new_value = 1.0
    new_data = data.copy()
    new_data[6, 19] = new_value

    file_path = tmp_path / "test.asdf"
    with asdf.AsdfFile() as af:
        af.tree = {"roman": WfiImage.create_fake_data()}

        af.tree["roman"].data = data
        af.write_to(file_path)

    # Since quantities don't inherit from np.memmap we have to test they are effectively
    # memapped.
    # rw mode needed because we have to test the memmap by manipulating the data on disk.
    # We have not set the filename so we should get a warning that it doesn't match
    with pytest.warns(datamodels.FilenameMismatchWarning), datamodels.open(file_path, memmap=True, mode="rw") as model:
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
    # We have not set the filename so we should get a warning that it doesn't match
    with pytest.warns(datamodels.FilenameMismatchWarning), datamodels.open(file_path, memmap=True, mode="rw") as model:
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
    data = np.zeros(
        (
            400,
            400,
        ),
        dtype=np.float32,
    )
    new_value = 1.0
    new_data = data.copy()
    new_data[6, 19] = new_value

    file_path = tmp_path / "test.asdf"
    with asdf.AsdfFile() as af:
        af.tree = {"roman": WfiImage.create_fake_data()}

        af.tree["roman"].data = data
        af.write_to(file_path)

    # Since quantities don't inherit from np.memmap we have to test they are effectively
    # memapped.
    # rw mode needed because we have to test the memmap by manipulating the data on disk.
    # We have not set the filename so we should get a warning that it doesn't match
    with pytest.warns(datamodels.FilenameMismatchWarning), datamodels.open(file_path, mode="rw", **kwargs) as model:
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
    # We have not set the filename so we should get a warning that it doesn't match
    with pytest.warns(datamodels.FilenameMismatchWarning), datamodels.open(file_path, mode="rw", **kwargs) as model:
        assert model.data[6, 19] != new_value
        assert (model.data == data).all()


def test_node_round_trip(tmp_path, tag_uri: str, node_class: tagged_type):
    file_path = tmp_path / "test.asdf"

    # Create/return a node and write it to disk, then check if the node round trips
    node = node_class.create_fake_data(tag=tag_uri)
    asdf.AsdfFile({"roman": node}).write_to(file_path)
    with asdf.open(file_path) as af:
        assert_node_equal(af.tree["roman"], node)
        assert af.tree["roman"]._read_tag == tag_uri


def test_opening_model(tmp_path, model_node: type[TaggedObjectNode]):
    file_path = tmp_path / "test.asdf"

    # Create a node and write it to disk
    node = model_node.create_fake_data()
    if hasattr(node, "meta") and hasattr(node.meta, "filename"):
        node.meta.filename = type(node.meta.filename)(file_path.name)
    asdf.AsdfFile({"roman": node}).write_to(file_path)

    with datamodels.open(file_path) as model:
        # Check that the model is the correct type
        assert isinstance(model, datamodels.MODEL_REGISTRY[model_node])


def test_read_pattern_properties():
    """
    Regression test for reading pattern properties
    """
    # This file has been modified by hand to break the `photmjsr` value
    with pytest.raises(asdf.ValidationError):
        datamodels.open(Path(__file__).parent / "data" / "photmjsm.asdf")


def test_rdm_open_non_datamodel():
    with pytest.raises(TypeError, match=r"Unknown datamodel type: .*"):
        datamodels.open(Path(__file__).parent / "data" / "not_a_datamodel.asdf")


def test_rdm_open_asdf(tmp_path):
    fn = tmp_path / "test.asdf"
    asdf.AsdfFile({"a": 1}).write_to(fn)
    with pytest.raises(ValueError, match=r"is not a roman file"):
        datamodels.open(fn)


def test_open_asn(tmp_path):
    romancal = pytest.importorskip("romancal")

    fn = tmp_path / "test.json"
    asn = {
        "products": [
            {
                "members": [],
                "name": "foo",
            }
        ],
    }
    with open(fn, "w") as f:
        json.dump(asn, f)

    lib = datamodels.open(fn)

    assert isinstance(lib, romancal.datamodels.ModelLibrary)


def test_filename_matches_meta(tmp_path, model_node: type[TaggedObjectNode]):
    # These models do not have meta.filename
    if "Ref" in model_node.__name__ or "Associations" in model_node.__name__:
        return

    save_path = tmp_path / "test_filename.asdf"
    open_path = tmp_path / "test_filename_read.asdf"

    # Create a node and write it to disk
    gen_model = model_node.create_fake_data()
    asdf.AsdfFile({"roman": gen_model}).write_to(save_path)

    # Save the filename type
    gn_fn_type = type(gen_model.meta.filename)

    # Rename the model so filenames don't match
    os.rename(save_path, open_path)

    # Prove filename is different from meta.filename without using datamodels.open
    with asdf.open(open_path) as af:
        assert af["roman"]["meta"]["filename"] != open_path.name

    # Show datamodels.open will update the filename in memory
    with (
        pytest.warns(
            match="meta.filename: \\? does not match filename: test_filename_read.asdf, updating the filename in memory!"
        ),
        datamodels.open(open_path) as model,
    ):
        assert model.meta.filename == open_path.name
        assert isinstance(model.meta.filename, gn_fn_type)


@pytest.mark.parametrize(
    "filename, original, expected",
    [
        ("bar.asdf", "fizz.asdf", "bar.asdf"),
        ("foo/bar.asdf", "fizz.asdf", "bar.asdf"),
        ("/foo/bar.asdf", "fizz.asdf", "bar.asdf"),
        # no patching for urls
        ("s3://foo/bar.asdf", "fizz.asdf", "fizz.asdf"),
        ("http://foo/bar.asdf", "fizz.asdf", "fizz.asdf"),
    ],
)
def test_patch_filename(filename, original, expected):
    asdf_file = asdf.AsdfFile({"roman": WfiImage.create_fake_data()})
    asdf_file["roman"]["meta"]["filename"] = original
    ctx = nullcontext() if original == expected else pytest.warns(datamodels.FilenameMismatchWarning)
    with ctx:
        _patch_meta_filename(filename, asdf_file)
    assert asdf_file["roman"]["meta"]["filename"] == expected
