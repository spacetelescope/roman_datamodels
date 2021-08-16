import pytest

from jsonschema import ValidationError
import asdf
import numpy as np

from roman_datamodels import datamodels
from roman_datamodels import stnode
# from roman_datamodels import table_definitions
from roman_datamodels.extensions import DATAMODEL_EXTENSIONS

from roman_datamodels.testing import utils


EXPECTED_COMMON_REFERENCE = \
    {'$ref': 'ref_common-1.0.0'}

# Helper class to iterate over model subclasses


def iter_subclasses(model_class, include_base_model=True):
    if include_base_model:
        yield model_class
    for sub_class in model_class.__subclasses__():
        yield from iter_subclasses(sub_class)


def test_model_schemas():
    dmodels = datamodels.model_registry.keys()
    for model in dmodels:
        schema_uri = next(t for t in DATAMODEL_EXTENSIONS[0].tags
                          if t._tag_uri == model._tag)._schema_uri
        asdf.schema.load_schema(schema_uri)

# Testing core schema


def test_core_schema(tmp_path):
    # Set temporary asdf file
    file_path = tmp_path / "test.asdf"

    wfi_image = utils.mk_level2_image(arrays=(10, 10))
    with asdf.AsdfFile() as af:
        af.tree = {'roman': wfi_image}
        with pytest.raises(ValidationError):
            af.tree['roman'].meta.telescope = 'NOTROMAN'
        af.tree['roman'].meta['telescope'] = 'NOTROMAN'
        with pytest.raises(ValidationError):
            af.write_to(file_path)
        af.tree['roman'].meta.telescope = 'ROMAN'
        af.write_to(file_path)
    # Now mangle the file
    with open(file_path, 'rb') as fp:
        fcontents = fp.read()
    romanloc = fcontents.find(bytes('ROMAN', 'utf-8'))
    newcontents = fcontents[:romanloc] + \
        bytes('X', 'utf-8') + fcontents[romanloc + 1:]
    with open(file_path, 'wb') as fp:
        fp.write(newcontents)
    with pytest.raises(ValidationError):
        with datamodels.open(file_path) as model:
            pass
    asdf.get_config().validate_on_read = False
    with datamodels.open(file_path) as model:
        assert model.meta.telescope == 'XOMAN'
    asdf.get_config().validate_on_read = True


# Testing all reference file schemas
def test_reference_file_model_base(tmp_path):
    # Set temporary asdf file

    # Get all reference file classes
    tags = [t for t in DATAMODEL_EXTENSIONS[0].tags if "/reference_files/" in t._tag_uri]
    for tag in tags:
        schema = asdf.schema.load_schema(tag._schema_uri)
        # Check that schema references common reference schema
        allofs = schema['properties']['meta']['allOf']
        found_common = False
        for item in allofs:
            if item == EXPECTED_COMMON_REFERENCE:
                found_common = True
        if not found_common:
            raise ValueError("Reference schema does not include ref_common")


def test_opening_flat_ref(tmp_path):
    # First make test reference file
    file_path = tmp_path / 'testflat.asdf'
    utils.mk_flat_file(file_path)
    flat = datamodels.open(file_path)
    assert flat.meta.instrument.optical_element == 'F158'
    assert isinstance(flat, datamodels.FlatRefModel)


# FlatModel tests
def test_flat_model(tmp_path):
    # Set temporary asdf file
    file_path = tmp_path / "test.asdf"

    meta = {}
    utils.add_ref_common(meta)
    meta['reftype'] = "FLAT"
    flatref = stnode.FlatRef()
    flatref['meta'] = meta
    flatref.meta.instrument['optical_element'] = 'F062'
    shape = (4096, 4096)
    flatref['data'] = np.zeros(shape, dtype=np.float32)
    flatref['dq'] = np.zeros(shape, dtype=np.uint32)
    flatref['err'] = np.zeros(shape, dtype=np.float32)

    # Testing flat file asdf file
    with asdf.AsdfFile(meta) as af:
        af.tree = {'roman': flatref}
        af.write_to(file_path)

        # Test that asdf file opens properly
        with datamodels.open(file_path) as model:
            with pytest.warns(None):
                model.validate()

            # Confirm that asdf file is opened as flat file model
            assert isinstance(model, datamodels.FlatRefModel)

# not sure what the following is supposed to ensure PG

# def test_meta_date_management(tmp_path):
#     model = datamodels.RomanDataModel({
#         "meta": {
#             "date": Time("2000-01-01T00:00:00.000"),
#             "instrument": {"name": "WFI", "detector": "WFI01", "optical_element": "F062"},
#             "telescope": "ROMAN",
#         }
#     })
#     assert model.meta.date == Time("2000-01-01T00:00:00.000")
#     model.save(str(tmp_path/"test.asdf"))
#     assert abs((Time.now() - model.meta.date).value) < 1.0

#     model = datamodels.RomanDataModel()
#     assert abs((Time.now() - model.meta.date).value) < 1.0


# Dark Current tests
def test_make_dark():
    dark = utils.mk_dark(shape=(3, 20,20))
    assert dark.meta.reftype == 'DARK'
    assert dark.data.dtype == np.float32
    assert dark.dq.dtype == np.uint32
    assert dark.dq.shape == (20,20)
    assert dark.err.dtype == np.float32

    # Test validation
    dark_model = datamodels.DarkRefModel(dark)
    assert dark_model.validate() is None

def test_opening_dark_ref(tmp_path):
    # First make test reference file
    file_path = tmp_path / 'testdark.asdf'
    utils.mk_dark(filepath=file_path)
    dark = datamodels.open(file_path)
    assert dark.meta.instrument.optical_element == 'F158'
    assert isinstance(dark, datamodels.DarkRefModel)

# Gain tests
def test_make_gain():
    gain = utils.mk_gain(shape=(20,20))
    assert gain.meta.reftype == 'GAIN'
    assert gain.data.dtype == np.float32

    # Test validation
    gain_model = datamodels.RampModel(gain)
    assert gain_model.validate() is None

def test_opening_gain_ref(tmp_path):
    # First make test reference file
    file_path = tmp_path / 'testgain.asdf'
    utils.mk_gain(filepath=file_path)
    gain = datamodels.open(file_path)
    assert gain.meta.instrument.optical_element == 'F158'
    assert isinstance(gain, datamodels.GainRefModel)


# Mask tests
def test_make_mask():
    mask = utils.mk_mask(shape=(20,20))
    assert mask.meta.reftype == 'MASK'
    assert mask.dq.dtype == np.uint32

    # Test validation
    mask_model = datamodels.RampModel(mask)
    assert mask_model.validate() is None

def test_opening_mask_ref(tmp_path):
    # First make test reference file
    file_path = tmp_path / 'testmask.asdf'
    utils.mk_mask(filepath=file_path)
    mask = datamodels.open(file_path)
    assert mask.meta.instrument.optical_element == 'F158'
    assert isinstance(mask, datamodels.MaskRefModel)


# Read Noise tests
def test_make_readnoise():
    readnoise = utils.mk_readnoise(shape=(20,20))
    assert readnoise.meta.reftype == 'READNOISE'
    assert readnoise.data.dtype == np.float32

    # Test validation
    readnoise_model = datamodels.RampModel(readnoise)
    assert readnoise_model.validate() is None

def test_opening_readnoise_ref(tmp_path):
    # First make test reference file
    file_path = tmp_path / 'testreadnoise.asdf'
    utils.mk_readnoise(filepath=file_path)
    readnoise = datamodels.open(file_path)
    assert readnoise.meta.instrument.optical_element == 'F158'
    assert isinstance(readnoise, datamodels.ReadnoiseRefModel)
