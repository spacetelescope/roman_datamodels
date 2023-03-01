import warnings

import asdf
import numpy as np
import pytest
from astropy import units as u
from astropy.modeling import Model
from jsonschema import ValidationError

from roman_datamodels import datamodels, stnode
from roman_datamodels import units as ru
from roman_datamodels.extensions import DATAMODEL_EXTENSIONS
from roman_datamodels.testing import utils

EXPECTED_COMMON_REFERENCE = {"$ref": "ref_common-1.0.0"}


@pytest.fixture(name="set_up_list_of_l2_files")
def set_up_list_of_l2_files(tmp_path, request):
    # generate a list of n filepaths and files to be read later on by ModelContainer
    marker = request.node.get_closest_marker("set_up_list_of_l2_files_data")
    number_of_files_to_create = marker.args[0]
    type_of_returned_object = marker.args[1]

    result_list = []
    for i in range(number_of_files_to_create):
        filepath = tmp_path / f"test_model_container_input_as_list_of_filepaths_{i:02}.asdf"
        # create L2 file using filepath
        utils.mk_level2_image(filepath=filepath)
        if type_of_returned_object == "asdf":
            # append filepath to filepath list
            result_list.append(str(filepath))
        elif type_of_returned_object == "datamodel":
            # parse ASDF file as RDM
            datamodel = datamodels.open(str(filepath))
            # append datamodel to datamodel list
            result_list.append(datamodel)

    return result_list


# Helper class to iterate over model subclasses
def iter_subclasses(model_class, include_base_model=True):
    if include_base_model:
        yield model_class
    for sub_class in model_class.__subclasses__():
        yield from iter_subclasses(sub_class)


def test_model_schemas():
    dmodels = datamodels.model_registry.keys()
    for model in dmodels:
        schema_uri = next(t for t in DATAMODEL_EXTENSIONS[0].tags if t._tag_uri == model._tag).schema_uris[0]
        asdf.schema.load_schema(schema_uri)


# Testing core schema
def test_core_schema(tmp_path):
    # Set temporary asdf file
    file_path = tmp_path / "test.asdf"

    wfi_image = utils.mk_level2_image(shape=(10, 10))
    with asdf.AsdfFile() as af:
        af.tree = {"roman": wfi_image}

        # Test telescope name
        af.tree["roman"].meta.telescope = "NOTROMAN"
        with pytest.raises(ValidationError):
            af.write_to(file_path)
        af.tree["roman"].meta["telescope"] = "NOTROMAN"
        with pytest.raises(ValidationError):
            af.write_to(file_path)
        af.tree["roman"].meta.telescope = "ROMAN"

        # Test origin name
        af.tree["roman"].meta.origin = "NOTSTSCI"
        with pytest.raises(ValidationError):
            af.write_to(file_path)
        af.tree["roman"].meta["origin"] = "NOTIPAC/SSC"
        with pytest.raises(ValidationError):
            af.write_to(file_path)
        af.tree["roman"].meta.origin = "IPAC/SSC"
        af.tree["roman"].meta.origin = "STSCI"

        af.write_to(file_path)
    # Now mangle the file
    with open(file_path, "rb") as fp:
        fcontents = fp.read()
    romanloc = fcontents.find(bytes("ROMAN", "utf-8"))
    newcontents = fcontents[:romanloc] + bytes("X", "utf-8") + fcontents[romanloc + 1 :]
    with open(file_path, "wb") as fp:
        fp.write(newcontents)
    with pytest.raises(ValidationError):
        with datamodels.open(file_path) as model:
            pass
    asdf.get_config().validate_on_read = False
    with datamodels.open(file_path) as model:
        assert model.meta.telescope == "XOMAN"
    asdf.get_config().validate_on_read = True


# RampFitOutput tests
def test_make_ramp():
    ramp = utils.mk_ramp(shape=(2, 20, 20))

    assert ramp.meta.exposure.type == "WFI_IMAGE"
    assert ramp.data.dtype == np.float32
    assert ramp.data.unit == ru.DN
    assert ramp.pixeldq.dtype == np.uint32
    assert ramp.pixeldq.shape == (20, 20)
    assert ramp.groupdq.dtype == np.uint8
    assert ramp.err.dtype == np.float32
    assert ramp.err.shape == (2, 20, 20)
    assert ramp.err.unit == ru.DN

    # Test validation
    ramp = datamodels.RampModel(ramp)
    assert ramp.validate() is None


def test_opening_ramp_ref(tmp_path):
    # First make test reference file
    file_path = tmp_path / "testramp.asdf"
    utils.mk_ramp(filepath=file_path)
    ramp = datamodels.open(file_path)
    assert ramp.meta.instrument.optical_element == "F062"
    assert isinstance(ramp, datamodels.RampModel)


# RampFitOutput tests
def test_make_rampfitoutput():
    rampfitoutput = utils.mk_rampfitoutput(shape=(2, 20, 20))

    assert rampfitoutput.meta.exposure.type == "WFI_IMAGE"
    assert rampfitoutput.slope.dtype == np.float32
    assert rampfitoutput.slope.unit == ru.electron / u.s
    assert rampfitoutput.sigslope.dtype == np.float32
    assert rampfitoutput.sigslope.unit == ru.electron / u.s
    assert rampfitoutput.yint.dtype == np.float32
    assert rampfitoutput.yint.unit == ru.electron
    assert rampfitoutput.sigyint.dtype == np.float32
    assert rampfitoutput.sigyint.unit == ru.electron
    assert rampfitoutput.pedestal.dtype == np.float32
    assert rampfitoutput.pedestal.unit == ru.electron
    assert rampfitoutput.weights.dtype == np.float32
    assert rampfitoutput.crmag.dtype == np.float32
    assert rampfitoutput.crmag.unit == ru.electron
    assert rampfitoutput.var_poisson.dtype == np.float32
    assert rampfitoutput.var_poisson.unit == ru.electron**2 / u.s**2
    assert rampfitoutput.var_rnoise.dtype == np.float32
    assert rampfitoutput.var_rnoise.unit == ru.electron**2 / u.s**2
    assert rampfitoutput.var_poisson.shape == (2, 20, 20)
    assert rampfitoutput.pedestal.shape == (20, 20)

    # Test validation
    rampfitoutput_model = datamodels.RampFitOutputModel(rampfitoutput)
    assert rampfitoutput_model.validate() is None


def test_opening_rampfitoutput_ref(tmp_path):
    # First make test reference file
    file_path = tmp_path / "testrampfitoutput.asdf"
    utils.mk_rampfitoutput(filepath=file_path)
    rampfitoutput = datamodels.open(file_path)
    assert rampfitoutput.meta.instrument.optical_element == "F062"
    assert isinstance(rampfitoutput, datamodels.RampFitOutputModel)


# Association tests
def test_make_association():
    member_shapes = (3, 8, 5, 2)
    association = utils.mk_associations(shape=member_shapes)

    print("XXX association.products = " + str(association.products))

    assert association.asn_type == "image"
    assert len(association.products) == len(member_shapes)

    for prod_idx in range(len(member_shapes)):
        assert association.products[prod_idx].name == "product" + str(prod_idx)
        assert len(association.products[prod_idx].members) == member_shapes[prod_idx]
        assert (
            association.products[prod_idx].members[-1].expname
            == "file_" + str(sum(member_shapes[0 : prod_idx + 1]) - 1) + ".asdf"
        )
        assert association.products[prod_idx].members[-1].exposerr == "null"
        assert association.products[prod_idx].members[-1].exptype in ["SCIENCE", "CALIBRATION", "ENGINEERING"]

    # Test validation
    association_model = datamodels.AssociationsModel(association)
    assert association_model.validate() is None


def test_opening_association_ref(tmp_path):
    # First make test reference file
    file_path = tmp_path / "testassociations.asdf"
    utils.mk_associations(filepath=file_path)
    association = datamodels.open(file_path)
    assert association.program == 1
    assert isinstance(association, datamodels.AssociationsModel)


# Guide Window tests
def test_make_guidewindow():
    guidewindow = utils.mk_guidewindow(shape=(2, 8, 16, 32, 32))

    assert guidewindow.meta.exposure.type == "WFI_IMAGE"
    assert guidewindow.pedestal_frames.dtype == np.uint16
    assert guidewindow.pedestal_frames.unit == ru.DN
    assert guidewindow.signal_frames.dtype == np.uint16
    assert guidewindow.signal_frames.unit == ru.DN
    assert guidewindow.amp33.dtype == np.uint16
    assert guidewindow.amp33.unit == ru.DN
    assert guidewindow.pedestal_frames.shape == (2, 8, 16, 32, 32)
    assert guidewindow.signal_frames.shape == (2, 8, 16, 32, 32)
    assert guidewindow.amp33.shape == (2, 8, 16, 32, 32)

    # Test validation
    guidewindow_model = datamodels.GuidewindowModel(guidewindow)
    assert guidewindow_model.validate() is None


def test_opening_guidewindow_ref(tmp_path):
    # First make test reference file
    file_path = tmp_path / "testguidewindow.asdf"
    utils.mk_guidewindow(filepath=file_path)
    guidewindow = datamodels.open(file_path)
    assert guidewindow.meta.gw_mode == "WIM-ACQ"
    assert isinstance(guidewindow, datamodels.GuidewindowModel)


# Model Container tests
@pytest.mark.set_up_list_of_l2_files_data(2, "asdf")
def test_model_container_input_as_list_of_filepaths(set_up_list_of_l2_files):

    filepath_list = set_up_list_of_l2_files
    # provide filepath list as input to ModelContainer
    model_container = datamodels.ModelContainer(filepath_list)

    assert len(model_container) == 2
    # check if all model_container elements are instances of DataModel
    assert all(isinstance(x, datamodels.DataModel) for x in model_container)


def test_model_container_input_as_list_of_datamodels(tmp_path):
    n = 2
    datamodel_list = []
    for i in range(n):
        filepath = tmp_path / f"test_model_container_input_as_list_of_filepaths_{i:02}.asdf"
        # create L2 file using filepath
        utils.mk_level2_image(filepath=filepath)
        # parse ASDF file as RDM
        datamodel = datamodels.open(str(filepath))
        # append datamodel to datamodel list
        datamodel_list.append(datamodel)

    # provide datamodel list as input to ModelContainer
    model_container = datamodels.ModelContainer(datamodel_list)

    assert len(datamodel_list) == n
    assert all(isinstance(x, datamodels.DataModel) for x in model_container)


@pytest.mark.set_up_list_of_l2_files_data(2, "asdf")
def test_imagemodel_set_item(set_up_list_of_l2_files):

    filepath_list = set_up_list_of_l2_files
    # provide filepath list as input to ModelContainer
    model_container = datamodels.ModelContainer(filepath_list)
    # grab first datamodel for testing
    image_model = model_container[0]

    image_model["test_attr"] = "test_attr_value"
    assert hasattr(image_model, "test_attr")
    assert image_model.test_attr == "test_attr_value"
    image_model["test_attr"] = "test_attr_new_value"
    assert image_model.test_attr == "test_attr_new_value"
    # test ValueError
    with pytest.raises(Exception) as e:
        image_model["_test_attr"] = "test_attr_some_other_value"
    assert e.type == ValueError


# Testing all reference file schemas
def test_reference_file_model_base(tmp_path):
    # Set temporary asdf file

    # Get all reference file classes
    tags = [t for t in DATAMODEL_EXTENSIONS[0].tags if "/reference_files/" in t.tag_uri]
    for tag in tags:
        schema = asdf.schema.load_schema(tag.schema_uris[0])
        # Check that schema references common reference schema
        allofs = schema["properties"]["meta"]["allOf"]
        found_common = False
        for item in allofs:
            if item == EXPECTED_COMMON_REFERENCE:
                found_common = True
        if not found_common:
            raise ValueError("Reference schema does not include ref_common")


# Flat tests
def test_make_flat():
    flat = utils.mk_flat(shape=(20, 20))
    assert flat.meta.reftype == "FLAT"
    assert flat.data.dtype == np.float32
    assert flat.dq.dtype == np.uint32
    assert flat.dq.shape == (20, 20)
    assert flat.err.dtype == np.float32

    # Test validation
    flat_model = datamodels.FlatRefModel(flat)
    assert flat_model.validate() is None


def test_opening_flat_ref(tmp_path):
    # First make test reference file
    file_path = tmp_path / "testflat.asdf"
    utils.mk_flat(filepath=file_path)
    flat = datamodels.open(file_path)
    assert flat.meta.instrument.optical_element == "F158"
    assert isinstance(flat, datamodels.FlatRefModel)


def test_flat_model(tmp_path):
    # Set temporary asdf file
    file_path = tmp_path / "test.asdf"

    meta = {}
    utils.add_ref_common(meta)
    meta["reftype"] = "FLAT"
    flatref = stnode.FlatRef()
    flatref["meta"] = meta
    flatref.meta.instrument["optical_element"] = "F062"
    shape = (4096, 4096)
    flatref["data"] = np.zeros(shape, dtype=np.float32)
    flatref["dq"] = np.zeros(shape, dtype=np.uint32)
    flatref["err"] = np.zeros(shape, dtype=np.float32)

    # Testing flat file asdf file
    with asdf.AsdfFile(meta) as af:
        af.tree = {"roman": flatref}
        af.write_to(file_path)

        # Test that asdf file opens properly
        with datamodels.open(file_path) as model:
            with warnings.catch_warnings():
                model.validate()

            # Confirm that asdf file is opened as flat file model
            assert isinstance(model, datamodels.FlatRefModel)


# Dark Current tests
def test_make_dark():
    dark = utils.mk_dark(shape=(3, 20, 20))
    assert dark.meta.reftype == "DARK"
    assert dark.data.dtype == np.float32
    assert dark.dq.dtype == np.uint32
    assert dark.dq.shape == (20, 20)
    assert dark.err.dtype == np.float32
    assert dark.data.unit == ru.DN

    # Test validation
    dark_model = datamodels.DarkRefModel(dark)
    assert dark_model.validate() is None


def test_opening_dark_ref(tmp_path):
    # First make test reference file
    file_path = tmp_path / "testdark.asdf"
    utils.mk_dark(filepath=file_path)
    dark = datamodels.open(file_path)
    assert dark.meta.instrument.optical_element == "F158"
    assert isinstance(dark, datamodels.DarkRefModel)


# Distortion tests
def test_make_distortion():
    distortion = utils.mk_distortion()
    assert distortion.meta.reftype == "DISTORTION"
    assert distortion["meta"]["input_units"] == u.pixel
    assert distortion["meta"]["output_units"] == u.arcsec
    assert isinstance(distortion["coordinate_distortion_transform"], Model)

    # Test validation
    distortion_model = datamodels.DistortionRefModel(distortion)
    assert distortion_model.validate() is None


def test_opening_distortion_ref(tmp_path):
    # First make test reference file
    file_path = tmp_path / "testdistortion.asdf"
    utils.mk_distortion(filepath=file_path)
    distortion = datamodels.open(file_path)
    assert distortion.meta.instrument.optical_element == "F158"
    assert isinstance(distortion, datamodels.DistortionRefModel)


# Gain tests
def test_make_gain():
    gain = utils.mk_gain(shape=(20, 20))
    assert gain.meta.reftype == "GAIN"
    assert gain.data.dtype == np.float32
    assert gain.data.unit == ru.electron / ru.DN

    # Test validation
    gain_model = datamodels.GainRefModel(gain)
    assert gain_model.validate() is None


def test_opening_gain_ref(tmp_path):
    # First make test reference file
    file_path = tmp_path / "testgain.asdf"
    utils.mk_gain(filepath=file_path)
    gain = datamodels.open(file_path)
    assert gain.meta.instrument.optical_element == "F158"
    assert isinstance(gain, datamodels.GainRefModel)


# Gain tests
def test_make_ipc():
    ipc = utils.mk_ipc(shape=(21, 21))
    assert ipc.meta.reftype == "IPC"
    assert ipc.data.dtype == np.float32
    assert ipc.data[10, 10] == 1.0
    assert np.sum(ipc.data) == 1.0

    # Test validation
    ipc_model = datamodels.GainRefModel(ipc)
    assert ipc_model.validate() is None


def test_opening_ipc_ref(tmp_path):
    # First make test reference file
    file_path = tmp_path / "testipc.asdf"
    utils.mk_ipc(filepath=file_path)
    ipc = datamodels.open(file_path)
    assert ipc.data[1, 1] == 1.0
    assert np.sum(ipc.data) == 1.0
    assert ipc.meta.instrument.optical_element == "F158"
    assert isinstance(ipc, datamodels.IpcRefModel)


# Linearity tests
def test_make_linearity():
    linearity = utils.mk_linearity(shape=(2, 20, 20))
    assert linearity.meta.reftype == "LINEARITY"
    assert linearity.coeffs.dtype == np.float32
    assert linearity.dq.dtype == np.uint32

    # Test validation
    linearity_model = datamodels.LinearityRefModel(linearity)
    assert linearity_model.validate() is None


def test_opening_linearity_ref(tmp_path):
    # First make test reference file
    file_path = tmp_path / "testlinearity.asdf"
    utils.mk_linearity(filepath=file_path)
    linearity = datamodels.open(file_path)
    assert linearity.meta.instrument.optical_element == "F158"
    assert isinstance(linearity, datamodels.LinearityRefModel)


# InverseLinearity tests
def test_make_inverse_linearity():
    inverselinearity = utils.mk_inverse_linearity(shape=(2, 20, 20))
    assert inverselinearity.meta.reftype == "INVERSE_LINEARITY"
    assert inverselinearity.coeffs.dtype == np.float32
    assert inverselinearity.dq.dtype == np.uint32

    # Test validation
    inverselinearity_model = datamodels.InverseLinearityRefModel(inverselinearity)
    assert inverselinearity_model.validate() is None


def test_opening_inverse_linearity_ref(tmp_path):
    # First make test reference file
    file_path = tmp_path / "testlinearity.asdf"
    utils.mk_inverse_linearity(filepath=file_path)
    inverselinearity = datamodels.open(file_path)
    assert inverselinearity.meta.instrument.optical_element == "F158"
    assert isinstance(inverselinearity, datamodels.InverseLinearityRefModel)


# Mask tests
def test_make_mask():
    mask = utils.mk_mask(shape=(20, 20))
    assert mask.meta.reftype == "MASK"
    assert mask.dq.dtype == np.uint32

    # Test validation
    mask_model = datamodels.MaskRefModel(mask)
    assert mask_model.validate() is None


def test_opening_mask_ref(tmp_path):
    # First make test reference file
    file_path = tmp_path / "testmask.asdf"
    utils.mk_mask(filepath=file_path)
    mask = datamodels.open(file_path)
    assert mask.meta.instrument.optical_element == "F158"
    assert isinstance(mask, datamodels.MaskRefModel)


# Pixel Area tests
def test_make_pixelarea():
    pixearea = utils.mk_pixelarea(shape=(20, 20))
    assert pixearea.meta.reftype == "AREA"
    assert type(pixearea.meta.photometry.pixelarea_steradians) == u.Quantity
    assert type(pixearea.meta.photometry.pixelarea_arcsecsq) == u.Quantity
    assert pixearea.data.dtype == np.float32

    # Test validation
    pixearea_model = datamodels.PixelareaRefModel(pixearea)
    assert pixearea_model.validate() is None


def test_opening_pixelarea_ref(tmp_path):
    # First make test reference file
    file_path = tmp_path / "testpixelarea.asdf"
    utils.mk_pixelarea(filepath=file_path)
    pixelarea = datamodels.open(file_path)
    assert pixelarea.meta.instrument.optical_element == "F158"
    assert isinstance(pixelarea, datamodels.PixelareaRefModel)


# Read Noise tests
def test_make_readnoise():
    readnoise = utils.mk_readnoise(shape=(20, 20))
    assert readnoise.meta.reftype == "READNOISE"
    assert readnoise.data.dtype == np.float32
    assert readnoise.data.unit == ru.DN

    # Test validation
    readnoise_model = datamodels.ReadnoiseRefModel(readnoise)
    assert readnoise_model.validate() is None


def test_opening_readnoise_ref(tmp_path):
    # First make test reference file
    file_path = tmp_path / "testreadnoise.asdf"
    utils.mk_readnoise(filepath=file_path)
    readnoise = datamodels.open(file_path)
    assert readnoise.meta.instrument.optical_element == "F158"
    assert isinstance(readnoise, datamodels.ReadnoiseRefModel)


def test_add_model_attribute(tmp_path):
    # First make test reference file
    file_path = tmp_path / "testreadnoise.asdf"
    utils.mk_readnoise(filepath=file_path)
    readnoise = datamodels.open(file_path)
    readnoise["new_attribute"] = 77
    assert readnoise.new_attribute == 77
    with pytest.raises(ValueError):
        readnoise["_underscore"] = "bad"
    file_path2 = tmp_path / "testreadnoise2.asdf"
    readnoise.save(file_path2)
    readnoise2 = datamodels.open(file_path2)
    assert readnoise2.new_attribute == 77
    readnoise2.new_attribute = 88
    assert readnoise2.new_attribute == 88
    with pytest.raises(ValidationError):
        readnoise["data"] = "bad_data_value"


# Saturation tests
def test_make_saturation():
    saturation = utils.mk_saturation(shape=(20, 20))
    assert saturation.meta.reftype == "SATURATION"
    assert saturation.dq.dtype == np.uint32
    assert saturation.data.dtype == np.float32
    assert saturation.data.unit == ru.DN

    # Test validation
    saturation_model = datamodels.SaturationRefModel(saturation)
    assert saturation_model.validate() is None


def test_opening_saturation_ref(tmp_path):
    # First make test reference file
    file_path = tmp_path / "testsaturation.asdf"
    utils.mk_saturation(filepath=file_path)
    saturation = datamodels.open(file_path)
    assert saturation.meta.instrument.optical_element == "F158"
    assert isinstance(saturation, datamodels.SaturationRefModel)


# Super Bias tests
def test_make_superbias():
    superbias = utils.mk_superbias(shape=(20, 20))
    assert superbias.meta.reftype == "BIAS"
    assert superbias.data.dtype == np.float32
    assert superbias.err.dtype == np.float32
    assert superbias.dq.dtype == np.uint32
    assert superbias.dq.shape == (20, 20)

    # Test validation
    superbias_model = datamodels.SuperbiasRefModel(superbias)
    assert superbias_model.validate() is None


def test_opening_superbias_ref(tmp_path):
    # First make test reference file
    file_path = tmp_path / "testsuperbias.asdf"
    utils.mk_superbias(filepath=file_path)
    superbias = datamodels.open(file_path)
    assert superbias.meta.instrument.optical_element == "F158"
    assert isinstance(superbias, datamodels.SuperbiasRefModel)


# WFI Photom tests
def test_make_wfi_img_photom():
    wfi_img_photom = utils.mk_wfi_img_photom()

    assert wfi_img_photom.meta.reftype == "PHOTOM"
    assert isinstance(wfi_img_photom.phot_table.F146.photmjsr, u.Quantity)
    assert wfi_img_photom.phot_table.F146.photmjsr.unit == u.megajansky / u.steradian
    assert isinstance(wfi_img_photom.phot_table.F184.photmjsr, u.Quantity)

    assert isinstance(wfi_img_photom.phot_table.F146.uncertainty, u.Quantity)
    assert isinstance(wfi_img_photom.phot_table.F184.uncertainty, u.Quantity)
    assert wfi_img_photom.phot_table.F184.uncertainty.unit == u.megajansky / u.steradian

    assert isinstance(wfi_img_photom.phot_table.F184.pixelareasr, u.Quantity)
    assert isinstance(wfi_img_photom.phot_table.F146.pixelareasr, u.Quantity)
    assert wfi_img_photom.phot_table.GRISM.pixelareasr.unit == u.steradian

    assert wfi_img_photom.phot_table.PRISM.photmjsr is None
    assert wfi_img_photom.phot_table.PRISM.uncertainty is None
    assert isinstance(wfi_img_photom.phot_table.PRISM.pixelareasr, u.Quantity)

    # Test validation
    wfi_img_photom_model = datamodels.WfiImgPhotomRefModel(wfi_img_photom)
    assert wfi_img_photom_model.validate() is None


def test_opening_wfi_img_photom_ref(tmp_path):
    # First make test reference file
    file_path = tmp_path / "testwfi_img_photom.asdf"
    utils.mk_wfi_img_photom(filepath=file_path)
    wfi_img_photom = datamodels.open(file_path)

    assert wfi_img_photom.meta.instrument.optical_element == "F158"
    assert isinstance(wfi_img_photom, datamodels.WfiImgPhotomRefModel)


# WFI Level 1 Science Raw tests
def test_level1_science_raw():
    wfi_science_raw = utils.mk_level1_science_raw()

    assert wfi_science_raw.data.dtype == np.uint16
    assert wfi_science_raw.data.unit == ru.DN

    # Test validation
    wfi_science_raw_model = datamodels.ScienceRawModel(wfi_science_raw)
    assert wfi_science_raw_model.validate() is None


def test_opening_level1_science_raw(tmp_path):
    # First make test reference file
    file_path = tmp_path / "testwfi_science_raw.asdf"
    utils.mk_level1_science_raw(filepath=file_path)
    wfi_science_raw = datamodels.open(file_path)

    assert wfi_science_raw.meta.instrument.optical_element == "F062"
    assert isinstance(wfi_science_raw, datamodels.ScienceRawModel)


# WFI Level 2 Image tests
def test_level2_image():
    wfi_image = utils.mk_level2_image()

    assert wfi_image.data.dtype == np.float32
    assert wfi_image.data.unit == ru.electron / u.s
    assert wfi_image.dq.dtype == np.uint32
    assert wfi_image.err.dtype == np.float32
    assert wfi_image.err.unit == ru.electron / u.s
    assert wfi_image.var_poisson.dtype == np.float32
    assert wfi_image.var_poisson.unit == ru.electron**2 / u.s**2
    assert wfi_image.var_rnoise.dtype == np.float32
    assert wfi_image.var_rnoise.unit == ru.electron**2 / u.s**2
    assert wfi_image.var_flat.dtype == np.float32
    assert type(wfi_image.cal_logs[0]) == str

    # Test validation
    wfi_image_model = datamodels.ImageModel(wfi_image)
    assert wfi_image_model.validate() is None


def test_opening_level2_image(tmp_path):
    # First make test reference file
    file_path = tmp_path / "testwfi_image.asdf"
    utils.mk_level2_image(filepath=file_path)
    wfi_image = datamodels.open(file_path)

    assert wfi_image.meta.instrument.optical_element == "F062"
    assert isinstance(wfi_image, datamodels.ImageModel)


def test_datamodel_info_search(capsys):
    wfi_science_raw = utils.mk_level1_science_raw()
    af = asdf.AsdfFile()
    af.tree = {"roman": wfi_science_raw}
    dm = datamodels.open(af)
    dm.info(max_rows=200)
    captured = capsys.readouterr()
    assert "optical_element" in captured.out
    result = dm.search("optical_element")
    assert "F062" in repr(result)
    assert result.node == "F062"


def test_datamodel_schema_info():
    wfi_science_raw = utils.mk_level1_science_raw()
    af = asdf.AsdfFile()
    af.tree = {"roman": wfi_science_raw}
    dm = datamodels.open(af)

    info = dm.schema_info("archive_catalog")
    assert info["roman"]["meta"]["aperture"] == {
        "name": {
            "archive_catalog": (
                {"datatype": "nvarchar(40)", "destination": ["ScienceCommon.aperture_name"]},
                dm.meta.aperture.name,
            ),
        },
        "position_angle": {"archive_catalog": ({"datatype": "float", "destination": ["ScienceCommon.position_angle"]}, 30.0)},
    }


def test_crds_parameters(tmp_path):
    # CRDS uses meta.exposure.start_time to compare to USEAFTER
    file_path = tmp_path / "testwfi_image.asdf"
    utils.mk_level2_image(filepath=file_path)
    wfi_image = datamodels.open(file_path)

    crds_pars = wfi_image.get_crds_parameters()
    assert "roman.meta.exposure.start_time" in crds_pars

    utils.mk_ramp(filepath=file_path)
    ramp = datamodels.open(file_path)

    crds_pars = ramp.get_crds_parameters()
    assert "roman.meta.exposure.start_time" in crds_pars
