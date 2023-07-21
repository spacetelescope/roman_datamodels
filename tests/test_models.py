import warnings
from contextlib import nullcontext

import asdf
import numpy as np
import pytest
from asdf.exceptions import ValidationError
from astropy import units as u
from astropy.modeling import Model
from numpy.testing import assert_array_equal

from roman_datamodels import datamodels
from roman_datamodels import maker_utils as utils
from roman_datamodels import stnode
from roman_datamodels.testing import assert_node_equal

from .conftest import MANIFEST

EXPECTED_COMMON_REFERENCE = {"$ref": "ref_common-1.0.0"}


def datamodel_names():
    names = []

    extension_manager = asdf.AsdfFile().extension_manager
    for tag in MANIFEST["tags"]:
        schema_uri = extension_manager.get_tag_definition(tag["tag_uri"]).schema_uris[0]
        schema = asdf.schema.load_schema(schema_uri, resolve_references=True)

        if "datamodel_name" in schema:
            names.append(schema["datamodel_name"])

    return names


@pytest.mark.parametrize("name", datamodel_names())
def test_datamodel_exists(name):
    """
    Confirm that a datamodel exists for every schema indicating that it is a datamodel
    """
    assert hasattr(datamodels, name)


@pytest.mark.parametrize("model", datamodels.MODEL_REGISTRY.values())
@pytest.mark.filterwarnings("ignore:This function assumes shape is 2D")
@pytest.mark.filterwarnings("ignore:Input shape must be 5D")
def test_node_type_matches_model(model):
    """
    Test that the _node_type listed for each model is what is listed in the schema
    """
    node_type = model._node_type
    node = utils.mk_node(node_type, shape=(8, 8, 8))
    schema = node.get_schema()
    name = schema["datamodel_name"]

    assert model.__name__ == name


@pytest.mark.filterwarnings("ignore:ERFA function.*")
@pytest.mark.parametrize("node, model", datamodels.MODEL_REGISTRY.items())
def test_model_schemas(node, model):
    instance = model(utils.mk_node(node))
    asdf.schema.load_schema(instance.schema_uri)


# Testing core schema
def test_core_schema(tmp_path):
    # Set temporary asdf file
    file_path = tmp_path / "test.asdf"

    wfi_image = utils.mk_level2_image(shape=(8, 8))
    with asdf.AsdfFile() as af:
        af.tree = {"roman": wfi_image}

        # Test telescope name
        with pytest.raises(ValidationError):
            # The error should be raised by the first statement,
            # but a bug in asdf is preventing it.  Including both
            # in the pytest.raises context will allow the test
            # to pass both before and after the asdf bug is fixed.
            af.tree["roman"].meta.telescope = "NOTROMAN"
            af.write_to(file_path)

        af.tree["roman"].meta["telescope"] = "NOTROMAN"
        with pytest.raises(ValidationError):
            af.write_to(file_path)
        af.tree["roman"].meta.telescope = "ROMAN"

        # Test origin name
        with pytest.raises(ValidationError):
            # See note above for explanation of why both
            # statements are included in the context here.
            af.tree["roman"].meta.origin = "NOTSTSCI"
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
    ramp = utils.mk_ramp(shape=(2, 8, 8))

    assert ramp.meta.exposure.type == "WFI_IMAGE"
    assert ramp.data.dtype == np.float32
    assert ramp.data.unit == u.DN
    assert ramp.pixeldq.dtype == np.uint32
    assert ramp.pixeldq.shape == (8, 8)
    assert ramp.groupdq.dtype == np.uint8
    assert ramp.err.dtype == np.float32
    assert ramp.err.shape == (2, 8, 8)
    assert ramp.err.unit == u.DN

    # Test validation
    ramp = datamodels.RampModel(ramp)
    assert ramp.validate() is None


# RampFitOutput tests
def test_make_ramp_fit_output():
    rampfitoutput = utils.mk_ramp_fit_output(shape=(2, 8, 8))

    assert rampfitoutput.meta.exposure.type == "WFI_IMAGE"
    assert rampfitoutput.slope.dtype == np.float32
    assert rampfitoutput.slope.unit == u.electron / u.s
    assert rampfitoutput.sigslope.dtype == np.float32
    assert rampfitoutput.sigslope.unit == u.electron / u.s
    assert rampfitoutput.yint.dtype == np.float32
    assert rampfitoutput.yint.unit == u.electron
    assert rampfitoutput.sigyint.dtype == np.float32
    assert rampfitoutput.sigyint.unit == u.electron
    assert rampfitoutput.pedestal.dtype == np.float32
    assert rampfitoutput.pedestal.unit == u.electron
    assert rampfitoutput.weights.dtype == np.float32
    assert rampfitoutput.crmag.dtype == np.float32
    assert rampfitoutput.crmag.unit == u.electron
    assert rampfitoutput.var_poisson.dtype == np.float32
    assert rampfitoutput.var_poisson.unit == u.electron**2 / u.s**2
    assert rampfitoutput.var_rnoise.dtype == np.float32
    assert rampfitoutput.var_rnoise.unit == u.electron**2 / u.s**2
    assert rampfitoutput.var_poisson.shape == (2, 8, 8)
    assert rampfitoutput.pedestal.shape == (8, 8)

    # Test validation
    rampfitoutput_model = datamodels.RampFitOutputModel(rampfitoutput)
    assert rampfitoutput_model.validate() is None


# TEST MSOS stack model
def test_make_msos_stack():
    msos_stack = utils.mk_msos_stack(shape=(8, 8))

    assert msos_stack.meta.exposure.type == "WFI_IMAGE"
    assert isinstance(msos_stack.meta.image_list, str)

    assert msos_stack.data.dtype == np.float64
    assert msos_stack.uncertainty.dtype == np.float64
    assert msos_stack.mask.dtype == np.uint8
    assert msos_stack.coverage.dtype == np.uint8

    datamodel = datamodels.MsosStackModel(msos_stack)
    assert datamodel.validate() is None


# Associations tests
def test_make_associations():
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
        assert association.products[prod_idx].members[-1].exptype in [
            "SCIENCE",
            "CALIBRATION",
            "ENGINEERING",
        ]

    # Test validation
    association_model = datamodels.AssociationsModel(association)
    assert association_model.validate() is None


@pytest.mark.parametrize(
    "expected, asn_data",
    [
        (True, {"asn_id": "foo", "asn_pool": "bar"}),
        (False, {"asn_id": "foo"}),
        (False, {"asn_pool": "bar"}),
        (False, {"foo": "bar"}),
        (False, "foo"),
    ],
)
def test_is_association(expected, asn_data):
    """
    Test the is_association function.
    """

    assert datamodels.AssociationsModel.is_association(asn_data) is expected


# Exposure Test
def test_read_pattern():
    exposure = utils.mk_exposure()
    assert exposure.read_pattern != [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
    assert len(exposure.read_pattern) == exposure.ngroups
    assert exposure.read_pattern == [
        [1],
        [2, 3],
        [4],
        [5, 6, 7, 8],
        [9, 10],
        [11],
    ]
    assert (type(rp) == list for rp in exposure.read_pattern)


# Guide Window tests
def test_make_guidewindow():
    guidewindow = utils.mk_guidewindow(shape=(2, 2, 2, 2, 2))

    assert guidewindow.meta.exposure.type == "WFI_IMAGE"
    assert guidewindow.pedestal_frames.dtype == np.uint16
    assert guidewindow.pedestal_frames.unit == u.DN
    assert guidewindow.signal_frames.dtype == np.uint16
    assert guidewindow.signal_frames.unit == u.DN
    assert guidewindow.amp33.dtype == np.uint16
    assert guidewindow.amp33.unit == u.DN
    assert guidewindow.pedestal_frames.shape == (2, 2, 2, 2, 2)
    assert guidewindow.signal_frames.shape == (2, 2, 2, 2, 2)
    assert guidewindow.amp33.shape == (2, 2, 2, 2, 2)

    # Test validation
    guidewindow_model = datamodels.GuidewindowModel(guidewindow)
    assert guidewindow_model.validate() is None


# Testing all reference file schemas
def test_reference_file_model_base(tmp_path):
    # Set temporary asdf file

    # Get all reference file classes
    tags = [t for t in stnode.NODE_EXTENSIONS[0].tags if "/reference_files/" in t.tag_uri]
    for tag in tags:
        schema = asdf.schema.load_schema(tag.schema_uris[0])
        # Check that schema references common reference schema
        allofs = schema["properties"]["meta"]["allOf"]
        found_common = False
        for item in allofs:
            if item == EXPECTED_COMMON_REFERENCE:
                found_common = True
        if not found_common:
            raise ValueError("Reference schema does not include ref_common")  # pragma: no cover


# Flat tests
def test_make_flat():
    flat = utils.mk_flat(shape=(8, 8))
    assert flat.meta.reftype == "FLAT"
    assert flat.data.dtype == np.float32
    assert flat.dq.dtype == np.uint32
    assert flat.dq.shape == (8, 8)
    assert flat.err.dtype == np.float32

    # Test validation
    flat_model = datamodels.FlatRefModel(flat)
    assert flat_model.validate() is None


def test_flat_model(tmp_path):
    # Set temporary asdf file
    file_path = tmp_path / "test.asdf"

    meta = utils.mk_ref_common("FLAT")
    flatref = stnode.FlatRef()
    flatref["meta"] = meta
    flatref.meta.instrument["optical_element"] = "F158"
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
    dark = utils.mk_dark(shape=(2, 8, 8))
    assert dark.meta.reftype == "DARK"
    assert dark.data.dtype == np.float32
    assert dark.dq.dtype == np.uint32
    assert dark.dq.shape == (8, 8)
    assert dark.err.dtype == np.float32
    assert dark.data.unit == u.DN

    # Test validation
    dark_model = datamodels.DarkRefModel(dark)
    assert dark_model.validate() is None


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


# Gain tests
def test_make_gain():
    gain = utils.mk_gain(shape=(8, 8))
    assert gain.meta.reftype == "GAIN"
    assert gain.data.dtype == np.float32
    assert gain.data.unit == u.electron / u.DN

    # Test validation
    gain_model = datamodels.GainRefModel(gain)
    assert gain_model.validate() is None


# Gain tests
def test_make_ipc():
    ipc = utils.mk_ipc(shape=(21, 21))
    assert ipc.meta.reftype == "IPC"
    assert ipc.data.dtype == np.float32
    assert ipc.data[10, 10] == 1.0
    assert np.sum(ipc.data) == 1.0

    # Test validation
    ipc_model = datamodels.IpcRefModel(ipc)
    assert ipc_model.validate() is None


# Linearity tests
def test_make_linearity():
    linearity = utils.mk_linearity(shape=(2, 8, 8))
    assert linearity.meta.reftype == "LINEARITY"
    assert linearity.coeffs.dtype == np.float32
    assert linearity.dq.dtype == np.uint32

    # Test validation
    linearity_model = datamodels.LinearityRefModel(linearity)
    assert linearity_model.validate() is None


# Inverselinearity tests
def test_make_inverselinearity():
    inverselinearity = utils.mk_inverselinearity(shape=(2, 8, 8))
    assert inverselinearity.meta.reftype == "INVERSELINEARITY"
    assert inverselinearity.coeffs.dtype == np.float32
    assert inverselinearity.dq.dtype == np.uint32

    # Test validation
    inverselinearity_model = datamodels.InverselinearityRefModel(inverselinearity)
    assert inverselinearity_model.validate() is None


# Mask tests
def test_make_mask():
    mask = utils.mk_mask(shape=(8, 8))
    assert mask.meta.reftype == "MASK"
    assert mask.dq.dtype == np.uint32

    # Test validation
    mask_model = datamodels.MaskRefModel(mask)
    assert mask_model.validate() is None


# Pixel Area tests
def test_make_pixelarea():
    pixearea = utils.mk_pixelarea(shape=(8, 8))
    assert pixearea.meta.reftype == "AREA"
    assert type(pixearea.meta.photometry.pixelarea_steradians) == u.Quantity
    assert type(pixearea.meta.photometry.pixelarea_arcsecsq) == u.Quantity
    assert pixearea.data.dtype == np.float32

    # Test validation
    pixearea_model = datamodels.PixelareaRefModel(pixearea)
    assert pixearea_model.validate() is None


# Read Noise tests
def test_make_readnoise():
    readnoise = utils.mk_readnoise(shape=(8, 8))
    assert readnoise.meta.reftype == "READNOISE"
    assert readnoise.data.dtype == np.float32
    assert readnoise.data.unit == u.DN

    # Test validation
    readnoise_model = datamodels.ReadnoiseRefModel(readnoise)
    assert readnoise_model.validate() is None


def test_add_model_attribute(tmp_path):
    # First make test reference file
    file_path = tmp_path / "testreadnoise.asdf"
    file_path2 = tmp_path / "testreadnoise2.asdf"

    utils.mk_readnoise(filepath=file_path)
    with datamodels.open(file_path) as readnoise:
        readnoise["new_attribute"] = 77
        assert readnoise.new_attribute == 77
        with pytest.raises(ValueError):
            readnoise["_underscore"] = "bad"
        readnoise.save(file_path2)

    with datamodels.open(file_path2) as readnoise2:
        assert readnoise2.new_attribute == 77
        readnoise2.new_attribute = 88
        assert readnoise2.new_attribute == 88
        with pytest.raises(ValidationError):
            readnoise["data"] = "bad_data_value"


# Saturation tests
def test_make_saturation():
    saturation = utils.mk_saturation(shape=(8, 8))
    assert saturation.meta.reftype == "SATURATION"
    assert saturation.dq.dtype == np.uint32
    assert saturation.data.dtype == np.float32
    assert saturation.data.unit == u.DN

    # Test validation
    saturation_model = datamodels.SaturationRefModel(saturation)
    assert saturation_model.validate() is None


# Super Bias tests
def test_make_superbias():
    superbias = utils.mk_superbias(shape=(8, 8))
    assert superbias.meta.reftype == "BIAS"
    assert superbias.data.dtype == np.float32
    assert superbias.err.dtype == np.float32
    assert superbias.dq.dtype == np.uint32
    assert superbias.dq.shape == (8, 8)

    # Test validation
    superbias_model = datamodels.SuperbiasRefModel(superbias)
    assert superbias_model.validate() is None


# Refpix tests
def test_make_refpix():
    refpix = utils.mk_refpix(shape=(8, 8))
    assert refpix.meta.reftype == "REFPIX"

    assert refpix.gamma.dtype == np.complex128
    assert refpix.zeta.dtype == np.complex128
    assert refpix.alpha.dtype == np.complex128

    assert refpix.gamma.shape == (8, 8)
    assert refpix.zeta.shape == (8, 8)
    assert refpix.alpha.shape == (8, 8)

    assert refpix.meta.input_units == u.DN
    assert refpix.meta.output_units == u.DN


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


# WFI Level 1 Science Raw tests
def test_make_level1_science_raw():
    wfi_science_raw = utils.mk_level1_science_raw(shape=(2, 8, 8))

    assert wfi_science_raw.data.dtype == np.uint16
    assert wfi_science_raw.data.unit == u.DN

    # Test validation
    wfi_science_raw_model = datamodels.ScienceRawModel(wfi_science_raw)
    assert wfi_science_raw_model.validate() is None


# WFI Level 2 Image tests
def test_make_level2_image():
    wfi_image = utils.mk_level2_image(shape=(8, 8))

    assert wfi_image.data.dtype == np.float32
    assert wfi_image.data.unit == u.electron / u.s
    assert wfi_image.dq.dtype == np.uint32
    assert wfi_image.err.dtype == np.float32
    assert wfi_image.err.unit == u.electron / u.s
    assert wfi_image.var_poisson.dtype == np.float32
    assert wfi_image.var_poisson.unit == u.electron**2 / u.s**2
    assert wfi_image.var_rnoise.dtype == np.float32
    assert wfi_image.var_rnoise.unit == u.electron**2 / u.s**2
    assert wfi_image.var_flat.dtype == np.float32
    assert type(wfi_image.cal_logs[0]) == str

    # Test validation
    wfi_image_model = datamodels.ImageModel(wfi_image)
    assert wfi_image_model.validate() is None


# WFI Level 3 Mosaic tests
def test_make_level3_mosaic():
    wfi_mosaic = utils.mk_level3_mosaic(shape=(8, 8))

    assert wfi_mosaic.data.dtype == np.float32
    assert wfi_mosaic.data.unit == u.electron / u.s

    assert wfi_mosaic.err.dtype == np.float32
    assert wfi_mosaic.err.unit == u.electron / u.s
    assert wfi_mosaic.context.dtype == np.uint32
    assert wfi_mosaic.weight.dtype == np.float32
    assert wfi_mosaic.var_poisson.dtype == np.float32
    assert wfi_mosaic.var_poisson.unit == u.electron**2 / u.s**2
    assert wfi_mosaic.var_rnoise.dtype == np.float32
    assert wfi_mosaic.var_rnoise.unit == u.electron**2 / u.s**2
    assert wfi_mosaic.var_flat.dtype == np.float32
    assert type(wfi_mosaic.cal_logs[0]) == str

    # Test validation
    wfi_mosaic_model = datamodels.MosaicModel(wfi_mosaic)
    assert wfi_mosaic_model.validate() is None


def test_datamodel_info_search(capsys):
    wfi_science_raw = utils.mk_level1_science_raw(shape=(2, 8, 8))
    af = asdf.AsdfFile()
    af.tree = {"roman": wfi_science_raw}
    with datamodels.open(af) as dm:
        dm.info(max_rows=200)
        captured = capsys.readouterr()
        assert "optical_element" in captured.out
        result = dm.search("optical_element")
        assert "F158" in repr(result)
        assert result.node == "F158"


def test_datamodel_schema_info():
    wfi_science_raw = utils.mk_level1_science_raw(shape=(2, 8, 8))
    af = asdf.AsdfFile()
    af.tree = {"roman": wfi_science_raw}
    with datamodels.open(af) as dm:
        info = dm.schema_info("archive_catalog")
        assert info["roman"]["meta"]["aperture"] == {
            "name": {
                "archive_catalog": (
                    {
                        "datatype": "nvarchar(40)",
                        "destination": [
                            "ScienceCommon.aperture_name",
                            "GuideWindow.aperture_name",
                        ],
                    },
                    dm.meta.aperture.name,
                ),
            },
            "position_angle": {
                "archive_catalog": (
                    {
                        "datatype": "float",
                        "destination": [
                            "ScienceCommon.position_angle",
                            "GuideWindow.position_angle",
                        ],
                    },
                    30.0,
                )
            },
        }


def test_crds_parameters(tmp_path):
    # CRDS uses meta.exposure.start_time to compare to USEAFTER
    file_path = tmp_path / "testwfi_image.asdf"
    utils.mk_level2_image(filepath=file_path)
    with datamodels.open(file_path) as wfi_image:
        crds_pars = wfi_image.get_crds_parameters()
        assert "roman.meta.exposure.start_time" in crds_pars

    utils.mk_ramp(filepath=file_path)
    with datamodels.open(file_path) as ramp:
        crds_pars = ramp.get_crds_parameters()
        assert "roman.meta.exposure.start_time" in crds_pars


def test_model_validate_without_save():
    # regression test for rcal-538
    img = utils.mk_level2_image(shape=(8, 8))
    m = datamodels.ImageModel(img)

    # invalidate pointing without using the
    # data model/node api to avoid a validation
    # failure here
    m.meta["pointing"] = {}

    with pytest.raises(ValidationError):
        m.validate()


@pytest.mark.filterwarnings("ignore:ERFA function.*")
@pytest.mark.parametrize("node", datamodels.MODEL_REGISTRY.keys())
@pytest.mark.parametrize("correct, model", datamodels.MODEL_REGISTRY.items())
@pytest.mark.filterwarnings("ignore:This function assumes shape is 2D")
@pytest.mark.filterwarnings("ignore:Input shape must be 5D")
def test_model_only_init_with_correct_node(node, correct, model):
    """
    Datamodels should only be initializable with the correct node in the model_registry.
    This checks that it can be initiallized with the correct node, and that it cannot be
    with any other node.
    """
    img = utils.mk_node(node, shape=(2, 8, 8))
    with nullcontext() if node is correct else pytest.raises(ValidationError):
        model(img)


def test_ramp_from_science_raw():
    raw = datamodels.ScienceRawModel(utils.mk_level1_science_raw(shape=(2, 8, 8)))

    ramp = datamodels.RampModel.from_science_raw(raw)
    for key in ramp:
        if not hasattr(raw, key):
            continue

        ramp_value = getattr(ramp, key)
        raw_value = getattr(raw, key)
        if isinstance(ramp_value, np.ndarray):
            assert_array_equal(ramp_value, raw_value.astype(ramp_value.dtype))

        elif isinstance(ramp_value, stnode.DNode):
            assert_node_equal(ramp_value, raw_value)

        else:
            raise ValueError(f"Unexpected type {type(ramp_value)}, {key}")  # pragma: no cover


@pytest.mark.parametrize("model", datamodels.MODEL_REGISTRY.values())
@pytest.mark.filterwarnings("ignore:This function assumes shape is 2D")
@pytest.mark.filterwarnings("ignore:Input shape must be 5D")
def test_datamodel_construct_like_from_like(model):
    """
    This is a regression test for the issue reported issue #51.

    Namely, if one passes a datamodel instance to the constructor for the datamodel
    of the same type as the instance, an error should not be raised (#51 reports an
    error being raised).

    Based on the discussion in PR #52, this should return exactly the same instance object
    that was passed to the constructor. i.e. it should not return a copy of the instance.
    """

    # Create a model
    mdl = utils.mk_datamodel(model, shape=(2, 8, 8))

    # Modify _iscopy as it will be reset to False by initializer if called incorrectly
    mdl._iscopy = "foo"

    # Pass model instance to model constructor
    new_mdl = model(mdl)
    assert new_mdl is mdl
    assert new_mdl._iscopy == "foo"  # Verify that the constructor didn't override stuff
