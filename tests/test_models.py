import gc
import warnings
from contextlib import nullcontext
from copy import deepcopy

import asdf
import numpy as np
import pytest
from asdf.exceptions import ValidationError
from astropy import units as u
from astropy.modeling import Model
from astropy.table import Table
from numpy.testing import assert_array_equal

from roman_datamodels import datamodels, stnode, validate
from roman_datamodels import maker_utils as utils
from roman_datamodels.testing import assert_node_equal, assert_node_is_copy

from .conftest import MANIFESTS

EXPECTED_COMMON_REFERENCE = {"$ref": "asdf://stsci.edu/datamodels/roman/schemas/reference_files/ref_common-1.0.0"}

# Nodes for metadata schema that do not contain any archive_catalog keywords
NODES_LACKING_ARCHIVE_CATALOG = [
    stnode.CalLogs,
    stnode.OutlierDetection,
    stnode.MosaicAssociations,
    stnode.IndividualImageMeta,
    stnode.Resample,
    stnode.SkyBackground,
    stnode.SourceCatalog,
    stnode.WfiWcs,
]


def datamodel_names():
    names = []

    extension_manager = asdf.AsdfFile().extension_manager
    for manifest in MANIFESTS:
        for tag in manifest["tags"]:
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
@pytest.mark.filterwarnings("ignore:Input shape must be 1D")
@pytest.mark.filterwarnings("ignore:This function assumes shape is 2D")
@pytest.mark.filterwarnings("ignore:Input shape must be 4D")
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


@pytest.mark.parametrize("node, model", datamodels.MODEL_REGISTRY.items())
@pytest.mark.parametrize("method", ["info", "search", "schema_info"])
@pytest.mark.parametrize("nuke_env_var", ["true", "false"], indirect=True)
def test_empty_model_asdf_operations(node, model, method, nuke_env_var):
    """
    Test the decorator for asdf operations on models when the model is left truly empty.
    """
    mdl = model()
    assert isinstance(mdl._instance, node)

    # Check that the model does not have the asdf attribute set.
    assert mdl._asdf is None

    # Depending on the state for nuke_validation we either expect an error or a
    # warning to be raised.
    #    - error: when nuke_env_var == true
    #    - warning: when nuke_env_var == false
    msg = f"DataModel needs to have all its data flushed out before calling {method}"
    context = pytest.raises(ValueError, match=msg) if nuke_env_var[1] else pytest.warns(validate.ValidationWarning)

    # Execute the method we wish to test, and catch the expected error/warning.
    with context:
        getattr(mdl, method)()

    if nuke_env_var[1]:
        # If an error is raised (nuke_env_var == true), then the asdf attribute should
        #    fail to be set.
        assert mdl._asdf is None
    else:
        # In a warning is raised (nuke_env_var == false), then the asdf attribute should
        #    be set to something.
        assert mdl._asdf is not None


@pytest.mark.parametrize("node, model", datamodels.MODEL_REGISTRY.items())
@pytest.mark.parametrize("method", ["info", "search", "schema_info"])
def test_model_asdf_operations(node, model, method):
    """
    Test the decorator for asdf operations on models when an empty initial model
    which is then filled.
    """
    # Create an empty model
    mdl = model()
    assert isinstance(mdl._instance, node)

    # Check there model prior to filling raises an error.
    with pytest.raises(ValueError):
        getattr(mdl, method)()

    # Fill the model with data, but no asdf file is present
    mdl._instance = utils.mk_node(node)
    assert mdl._asdf is None

    # Run the method we wish to test (it should fail with warning or error
    # if something is broken)
    getattr(mdl, method)()

    # Show that mdl._asdf is now set
    assert mdl._asdf is not None


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
        af.tree["roman"].meta.origin = "STSCI/SOC"

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
    # Filename mismatch warning, because did not save through datamodel to_asdf method
    with pytest.warns(datamodels.FilenameMismatchWarning), datamodels.open(file_path) as model:
        assert model.meta.telescope == "XOMAN"
    asdf.get_config().validate_on_read = True


# RampFitOutput tests
def test_make_ramp():
    ramp = utils.mk_ramp(shape=(2, 8, 8))

    assert ramp.meta.exposure.type == "WFI_IMAGE"
    assert ramp.data.dtype == np.float32
    assert ramp.pixeldq.dtype == np.uint32
    assert ramp.pixeldq.shape == (8, 8)
    assert ramp.groupdq.dtype == np.uint8
    assert ramp.err.dtype == np.float32
    assert ramp.err.shape == (2, 8, 8)

    # Test validation
    ramp = datamodels.RampModel(ramp)
    assert ramp.validate() is None


# RampFitOutput tests
def test_make_ramp_fit_output():
    rampfitoutput = utils.mk_ramp_fit_output(shape=(2, 8, 8))

    assert rampfitoutput.meta.exposure.type == "WFI_IMAGE"
    assert rampfitoutput.slope.dtype == np.float32
    assert rampfitoutput.sigslope.dtype == np.float32
    assert rampfitoutput.yint.dtype == np.float32
    assert rampfitoutput.sigyint.dtype == np.float32
    assert rampfitoutput.pedestal.dtype == np.float32
    assert rampfitoutput.weights.dtype == np.float32
    assert rampfitoutput.crmag.dtype == np.float32
    assert rampfitoutput.var_poisson.dtype == np.float32
    assert rampfitoutput.var_rnoise.dtype == np.float32
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
    assert len(exposure.read_pattern) == exposure.nresultants
    assert exposure.read_pattern == [
        [1],
        [2, 3],
        [4],
        [5, 6, 7, 8],
        [9, 10],
        [11],
    ]
    assert (isinstance(rp, list) for rp in exposure.read_pattern)


# L1 Face Guide Window tests
def test_make_l1_face_guidewindow():
    shape = (12,)
    l1facegw = utils.mk_l1_face_guidewindow(shape=shape, mode="WSM")

    assert l1facegw.meta.optical_element == "F158"
    assert l1facegw.meta.guide_star_acq_num == -999999
    assert l1facegw.meta.fgs_modes_used == ["NOT_CONFIGURED"]
    assert l1facegw.face_data.delta.dtype == np.float32

    # Ensure WIM model lacks the WSM array set
    l1facegw_wim = utils.mk_l1_face_guidewindow(shape=(12,), mode="WIM")
    assert "wsm_edge_used" in l1facegw.meta
    assert "wsm_edge_used" not in l1facegw_wim.meta

    # Test validation
    l1facegw_model = datamodels.L1FaceGuidewindowModel(l1facegw)
    assert l1facegw_model.validate() is None


# Guide Window tests
def test_make_guidewindow():
    guidewindow = utils.mk_guidewindow(shape=(2, 2, 2, 2, 2))

    assert guidewindow.meta.exposure.type == "WFI_IMAGE"
    assert guidewindow.pedestal_frames.dtype == np.uint16
    assert guidewindow.signal_frames.dtype == np.uint16
    assert guidewindow.amp33.dtype == np.uint16
    assert guidewindow.pedestal_frames.shape == (2, 2, 2, 2, 2)
    assert guidewindow.signal_frames.shape == (2, 2, 2, 2, 2)
    assert guidewindow.amp33.shape == (2, 2, 2, 2, 2)

    # Test validation
    guidewindow_model = datamodels.GuidewindowModel(guidewindow)
    assert guidewindow_model.validate() is None


# L1 Guide Window tests
def test_make_l1_detector_guidewindow():
    l1detectorgw = utils.mk_l1_detector_guidewindow(shape=(2, 3, 4), mode="WSM")

    assert l1detectorgw.meta.instrument.name == "WFI"
    assert l1detectorgw.meta.guide_window.min_acq_xstart == -999999
    assert l1detectorgw.meta.guide_star.predicted_ra == -999999
    assert l1detectorgw.amp33.amp33_track_pedestals.dtype == np.uint16
    assert l1detectorgw.acq_data.pedestal_resultants.dtype == np.uint16
    assert l1detectorgw.track_data.pixel_offsets.dtype == np.uint16
    assert l1detectorgw.centroid.acq_centroid_quality.shape == (3, 4)
    assert l1detectorgw.edge_acq_data.pedestal_resultants.shape == (2, 3, 4)
    assert l1detectorgw.acq_data.reset_impacted_pairs.shape == (2,)

    # Ensure WIM model lacks the WSM array set
    l1detectorgw_wim = utils.mk_l1_detector_guidewindow(shape=(2, 3, 4), mode="WIM")
    assert "edge_acq_data" in l1detectorgw
    assert "edge_acq_data" not in l1detectorgw_wim

    # Test validation
    l1detectorgw_model = datamodels.L1DetectorGuidewindowModel(l1detectorgw)
    assert l1detectorgw_model.validate() is None


# AB Vega Offset Correction tests
def test_make_abvegaoffset():
    abvegaoffset = utils.mk_abvegaoffset()
    assert abvegaoffset.meta.reftype == "ABVEGAOFFSET"
    assert isinstance(abvegaoffset.data.GRISM["abvega_offset"], float)

    # Test validation
    abvegaoffset_model = datamodels.AbvegaoffsetRefModel(abvegaoffset)
    assert abvegaoffset_model.validate() is None


# Aperture Correction tests
def test_make_apcorr():
    apcorr = utils.mk_apcorr()
    assert apcorr.meta.reftype == "APCORR"
    assert isinstance(apcorr.data.DARK["sky_background_rin"], float)
    assert isinstance(apcorr.data.DARK["ap_corrections"], np.ndarray)
    assert isinstance(apcorr.data.DARK["ap_corrections"][0], float)

    # Test validation
    apcorr_model = datamodels.ApcorrRefModel(apcorr)
    assert apcorr_model.validate() is None


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
    assert dark.dark_slope.dtype == np.float32
    assert dark.dark_slope_error.dtype == np.float32
    assert dark.dark_slope_error.shape == (8, 8)

    # Test validation
    dark_model = datamodels.DarkRefModel(dark)
    assert dark_model.validate() is None


# Distortion tests
def test_make_distortion():
    distortion = utils.mk_distortion()
    assert distortion.meta.reftype == "DISTORTION"
    assert isinstance(distortion["coordinate_distortion_transform"], Model)

    # Test validation
    distortion_model = datamodels.DistortionRefModel(distortion)
    assert distortion_model.validate() is None


# ePSF tests
def test_make_epsf():
    epsf = utils.mk_epsf(shape=(2, 3, 4, 8, 8))
    assert epsf.meta.reftype == "EPSF"
    assert isinstance(epsf.meta["pixel_x"], list)
    assert isinstance(epsf.meta["pixel_x"][0], float)
    assert epsf["psf"].shape == (2, 3, 4, 8, 8)
    assert isinstance(epsf["psf"][0, 0, 0, 0, 0], float | np.float32)

    # Test validation
    epsf_model = datamodels.EpsfRefModel(epsf)
    assert epsf_model.validate() is None


# Gain tests
def test_make_gain():
    gain = utils.mk_gain(shape=(8, 8))
    assert gain.meta.reftype == "GAIN"
    assert gain.data.dtype == np.float32

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


# Ma Table tests
def test_make_matable():
    matable = utils.mk_matable(gw_table_ids=["GW0002"], sci_table_ids=["SCI0004", "SCI0005", "SCI0007", "SCI0008"], length=8)

    assert matable.meta.reftype == "MATABLE"
    assert isinstance(matable.guide_window_tables["GW0002"]["ma_table_name"], str)
    assert len(matable.science_tables["SCI0005"]["accumulated_exposure_time"]) == 8
    assert (isinstance(rp, list) for rp in matable.science_tables["SCI0004"]["science_read_pattern"])
    assert isinstance(matable.science_tables["SCI0008"]["science_read_pattern"][0][0], int)

    # Test validation
    matable_model = datamodels.MATableRefModel(matable)
    assert matable_model.validate() is None


# Pixel Area tests
def test_make_pixelarea():
    pixearea = utils.mk_pixelarea(shape=(8, 8))
    assert pixearea.meta.reftype == "AREA"
    assert pixearea.data.dtype == np.float32

    # Test validation
    pixearea_model = datamodels.PixelareaRefModel(pixearea)
    assert pixearea_model.validate() is None


# Read Noise tests
def test_make_readnoise():
    readnoise = utils.mk_readnoise(shape=(8, 8))
    assert readnoise.meta.reftype == "READNOISE"
    assert readnoise.data.dtype == np.float32

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
        readnoise2.data = "bad_data_value"
        with pytest.raises(ValidationError):
            readnoise2.validate()


def test_model_subscribable(tmp_path):
    """
    Test that __getitem__ exists
    """
    file_path = tmp_path / "testreadnoise.asdf"

    utils.mk_readnoise(shape=(8, 8), filepath=file_path)
    with datamodels.open(file_path) as readnoise:
        assert readnoise["data"].shape == (8, 8)
        assert readnoise.data is readnoise["data"]


# Saturation tests
def test_make_saturation():
    saturation = utils.mk_saturation(shape=(8, 8))
    assert saturation.meta.reftype == "SATURATION"
    assert saturation.dq.dtype == np.uint32
    assert saturation.data.dtype == np.float32

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


# Skycells tests
def test_make_skycells():
    skycells_ref = utils.mk_skycells()
    assert skycells_ref.projection_regions["index"][2] == 2


# WFI Photom tests
def test_make_wfi_img_photom():
    wfi_img_photom = utils.mk_wfi_img_photom()

    assert wfi_img_photom.meta.reftype == "PHOTOM"

    assert wfi_img_photom.phot_table.PRISM.photmjsr is None
    assert wfi_img_photom.phot_table.PRISM.uncertainty is None

    # Test validation
    wfi_img_photom_model = datamodels.WfiImgPhotomRefModel(wfi_img_photom)
    assert wfi_img_photom_model.validate() is None


# WFI Level 1 Science Raw tests
def test_make_level1_science_raw():
    shape = (2, 8, 8)
    wfi_science_raw = utils.mk_level1_science_raw(shape=shape, dq=True)

    assert wfi_science_raw.data.dtype == np.uint16

    # Test validation
    wfi_science_raw_model = datamodels.ScienceRawModel(wfi_science_raw)
    assert wfi_science_raw_model.validate() is None


# WFI Level 2 Image tests
def test_make_level2_image():
    wfi_image = utils.mk_level2_image(shape=(8, 8))

    assert wfi_image.data.dtype == np.float32
    assert wfi_image.dq.dtype == np.uint32
    assert wfi_image.err.dtype == np.float32
    assert wfi_image.var_poisson.dtype == np.float32
    assert wfi_image.var_rnoise.dtype == np.float32
    assert wfi_image.var_flat.dtype == np.float32
    assert isinstance(wfi_image.meta.cal_logs[0], str)

    # Test validation
    wfi_image_model = datamodels.ImageModel(wfi_image)
    assert wfi_image_model.validate() is None

    # Test validation
    assert wfi_image_model.validate() is None


# Test that attributes can be assigned object instances without raising exceptions
# unless they don't match the corresponding tag
def test_node_assignment():
    """Test round trip attribute access and assignment"""
    wfi_image = utils.mk_level2_image(shape=(8, 8))
    exposure = wfi_image.meta.exposure
    assert isinstance(exposure, stnode.DNode)
    wfi_image.meta.exposure = exposure
    assert isinstance(wfi_image.meta.exposure, stnode.DNode)
    # The following tests that supplying a LNode passes validation.
    rampmodel = datamodels.RampModel(utils.mk_ramp(shape=(9, 9, 2)))
    assert isinstance(rampmodel.meta.exposure.read_pattern[1:], stnode.LNode)
    rampmodel.meta.exposure.read_pattern = rampmodel.meta.exposure.read_pattern[1:]
    # Test that supplying a DNode passes validation
    darkmodel = datamodels.DarkRefModel(utils.mk_dark(shape=(2, 9, 9)))
    darkexp = darkmodel.meta.exposure
    assert isinstance(darkexp, stnode.DNode)
    darkexp.ngroups = darkexp.ngroups + 1
    assert darkexp.ngroups == 7
    darkmodel.meta.exposure = darkexp


# WFI Level 3 Mosaic tests
def test_make_level3_mosaic():
    wfi_mosaic = utils.mk_level3_mosaic(shape=(8, 8))

    assert wfi_mosaic.data.dtype == np.float32

    assert wfi_mosaic.err.dtype == np.float32
    assert wfi_mosaic.context.dtype == np.uint32
    assert wfi_mosaic.weight.dtype == np.float32
    assert wfi_mosaic.var_poisson.dtype == np.float32
    assert wfi_mosaic.var_rnoise.dtype == np.float32
    assert wfi_mosaic.var_flat.dtype == np.float32
    assert isinstance(wfi_mosaic.meta.cal_logs[0], str)

    # Test validation
    wfi_mosaic_model = datamodels.MosaicModel(wfi_mosaic)
    assert wfi_mosaic_model.validate() is None


# FPS tests
def test_make_fps():
    shape = (2, 8, 8)
    fps = utils.mk_fps(shape=shape)

    assert fps.data.dtype == np.uint16

    # Test validation
    fps_model = datamodels.FpsModel(fps)
    assert fps_model.validate() is None


# TVAC tests
def test_make_tvac():
    shape = (2, 8, 8)
    tvac = utils.mk_tvac(shape=shape)

    assert tvac.data.dtype == np.uint16
    assert tvac.data.unit == u.DN

    # Test validation
    tvac_model = datamodels.TvacModel(tvac)
    assert tvac_model.validate() is None


def test_make_image_source_catalog():
    source_catalog = utils.mk_image_source_catalog()
    source_catalog_model = datamodels.ImageSourceCatalogModel(source_catalog)

    assert isinstance(source_catalog_model.source_catalog, Table)


def test_make_forced_image_source_catalog():
    source_catalog = utils.mk_forced_image_source_catalog()
    source_catalog_model = datamodels.ForcedImageSourceCatalogModel(source_catalog)

    assert isinstance(source_catalog_model.source_catalog, Table)


def test_make_segmentation_map():
    segmentation_map = utils.mk_segmentation_map()
    segmentation_map_model = datamodels.SegmentationMapModel(segmentation_map)

    assert isinstance(segmentation_map_model.data, np.ndarray)


def test_make_mosaic_source_catalog():
    source_catalog = utils.mk_mosaic_source_catalog()
    source_catalog_model = datamodels.MosaicSourceCatalogModel(source_catalog)

    assert isinstance(source_catalog_model.source_catalog, Table)


def test_make_forced_mosaic_source_catalog():
    source_catalog = utils.mk_forced_mosaic_source_catalog()
    source_catalog_model = datamodels.ForcedMosaicSourceCatalogModel(source_catalog)

    assert isinstance(source_catalog_model.source_catalog, Table)


def test_make_multiband_source_catalog():
    source_catalog = utils.mk_multiband_source_catalog()
    source_catalog_model = datamodels.MultibandSourceCatalogModel(source_catalog)

    assert isinstance(source_catalog_model.source_catalog, Table)


def test_make_mosaic_segmentation_map():
    segmentation_map = utils.mk_mosaic_segmentation_map()
    segmentation_map_model = datamodels.MosaicSegmentationMapModel(segmentation_map)

    assert isinstance(segmentation_map_model.data, np.ndarray)


@pytest.mark.parametrize(
    "model_class",
    (
        datamodels.ImageSourceCatalogModel,
        datamodels.MosaicSourceCatalogModel,
        datamodels.ForcedImageSourceCatalogModel,
        datamodels.ForcedMosaicSourceCatalogModel,
        datamodels.MultibandSourceCatalogModel,
    ),
)
def test_get_column_description(model_class):
    model = model_class.create_fake_data()
    for column in model.source_catalog.columns.values():
        column_def = model.get_column_definition(column.name)
        assert column_def is not None
        if column.unit == "none":
            assert column_def["unit"] == "none"
        else:
            assert u.Unit(column_def["unit"]) == column.unit
        assert column_def["description"] == column.description
        assert np.dtype(column_def["datatype"]) == column.dtype


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


def test_datamodel_schema_info_values():
    wfi_science_raw = utils.mk_level1_science_raw(shape=(2, 8, 8))
    af = asdf.AsdfFile()
    af.tree = {"roman": wfi_science_raw}
    with datamodels.open(af) as dm:
        info = dm.schema_info("archive_catalog")
        assert info["roman"]["meta"]["pointing"] == {
            "ra_v1": {
                "archive_catalog": (
                    {
                        "datatype": "float",
                        "destination": [
                            "WFIExposure.ra_v1",
                            "GuideWindow.ra_v1",
                        ],
                    },
                    dm.meta.pointing.ra_v1,
                ),
            },
            "dec_v1": {
                "archive_catalog": (
                    {
                        "datatype": "float",
                        "destination": [
                            "WFIExposure.dec_v1",
                            "GuideWindow.dec_v1",
                        ],
                    },
                    dm.meta.pointing.dec_v1,
                )
            },
            "pa_v3": {
                "archive_catalog": (
                    {
                        "datatype": "float",
                        "destination": [
                            "WFIExposure.pa_v3",
                            "GuideWindow.pa_v3",
                        ],
                    },
                    dm.meta.pointing.pa_v3,
                ),
            },
            "target_aperture": {
                "archive_catalog": (
                    {
                        "datatype": "nvarchar(100)",
                        "destination": [
                            "WFIExposure.target_aperture",
                            "GuideWindow.target_aperture",
                        ],
                    },
                    dm.meta.pointing.target_aperture,
                )
            },
            "target_ra": {
                "archive_catalog": (
                    {
                        "datatype": "float",
                        "destination": [
                            "WFIExposure.target_ra",
                            "GuideWindow.target_ra",
                        ],
                    },
                    dm.meta.pointing.target_ra,
                ),
            },
            "target_dec": {
                "archive_catalog": (
                    {
                        "datatype": "float",
                        "destination": [
                            "WFIExposure.target_dec",
                            "GuideWindow.target_dec",
                        ],
                    },
                    dm.meta.pointing.target_dec,
                )
            },
            "pointing_engineering_source": {
                "archive_catalog": (
                    {
                        "datatype": "nvarchar(10)",
                        "destination": [
                            "WFIExposure.pointing_engineering_source",
                            "GuideWindow.pointing_engineering_source",
                        ],
                    },
                    dm.meta.pointing.pointing_engineering_source,
                )
            },
            "pa_aperture": {
                "archive_catalog": (
                    {
                        "datatype": "float",
                        "destination": [
                            "WFIExposure.pa_aperture",
                            "GuideWindow.pa_aperture",
                        ],
                    },
                    dm.meta.pointing.pa_aperture,
                ),
            },
        }


@pytest.mark.parametrize("name", datamodel_names())
def test_datamodel_schema_info_existence(name):
    # Loop over datamodels that have archive_catalog entries
    if not name.endswith("RefModel") and name != "AssociationsModel":
        method = getattr(datamodels, name)
        model = utils.mk_datamodel(method)
        info = model.schema_info("archive_catalog")
        for keyword in model.meta.keys():
            # Only DNodes or LNodes need to be canvassed
            if isinstance(model.meta[keyword], stnode.DNode | stnode.LNode):
                # Ignore metadata schemas that lack archive_catalog entries
                if type(model.meta[keyword]) not in NODES_LACKING_ARCHIVE_CATALOG:
                    assert keyword in info["roman"]["meta"]


@pytest.mark.parametrize("include_arrays", (True, False))
def test_to_flat_dict(include_arrays, tmp_path):
    file_path = tmp_path / "test.asdf"
    utils.mk_level2_image(filepath=file_path, shape=(8, 8))
    with datamodels.open(file_path) as model:
        if include_arrays:
            assert "roman.data" in model.to_flat_dict()
        else:
            assert "roman.data" not in model.to_flat_dict(include_arrays=False)


@pytest.mark.parametrize("mk_model", (utils.mk_level2_image, utils.mk_ramp))
def test_crds_parameters(mk_model, tmp_path):
    # CRDS uses meta.exposure.start_time to compare to USEAFTER
    file_path = tmp_path / "test.asdf"
    mk_model(filepath=file_path)
    with datamodels.open(file_path) as model:
        # patch on a value that is valid (a simple type)
        # but isn't under meta. Since it's not under meta
        # it shouldn't be in the crds_pars.
        model["test"] = 42
        crds_pars = model.get_crds_parameters()
        assert "roman.meta.exposure.start_time" in crds_pars
        assert "roman.cal_logs" not in crds_pars
        assert "roman.test" not in crds_pars


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
@pytest.mark.filterwarnings("ignore:Input shape must be 1D")
@pytest.mark.filterwarnings("ignore:This function assumes shape is 2D")
@pytest.mark.filterwarnings("ignore:Input shape must be 4D")
@pytest.mark.filterwarnings("ignore:Input shape must be 5D")
def test_model_only_init_with_correct_node(node, correct, model):
    """
    Datamodels should only be initializable with the correct node in the model_registry.
    This checks that it can be initialized with the correct node, and that it cannot be
    with any other node.
    """
    img = utils.mk_node(node, shape=(2, 8, 8))
    with nullcontext() if node is correct else pytest.raises(ValidationError):
        model(img)


@pytest.mark.parametrize(
    "mk_raw",
    [
        lambda: datamodels.ScienceRawModel(utils.mk_level1_science_raw(shape=(2, 8, 8), dq=True)),
        lambda: datamodels.TvacModel(utils.mk_tvac(shape=(2, 8, 8))),
        lambda: datamodels.FpsModel(utils.mk_fps(shape=(2, 8, 8))),
        lambda: datamodels.RampModel(utils.mk_ramp(shape=(2, 8, 8))),
    ],
)
def test_ramp_from_science_raw(mk_raw):
    raw = mk_raw()
    ramp = datamodels.RampModel.from_science_raw(raw)
    for key in ramp:
        if not hasattr(raw, key):
            continue

        ramp_value = getattr(ramp, key)
        raw_value = getattr(raw, key)
        if isinstance(ramp_value, np.ndarray):
            assert_array_equal(ramp_value, raw_value.astype(ramp_value.dtype))

        elif key == "meta":
            ramp_meta = ramp_value.to_flat_dict(include_arrays=False, recursive=True)
            raw_meta = raw_value.to_flat_dict(include_arrays=False, recursive=True)
            for meta_key in ramp_meta:
                if meta_key == "model_type":
                    ramp_value[meta_key] = ramp.__class__.__name__
                    raw_value[meta_key] = raw.__class__.__name__
                    continue
                elif meta_key == "cal_step":
                    continue
                if meta_key in raw_meta:
                    assert ramp_meta[meta_key] == raw_meta[meta_key]

        elif isinstance(ramp_value, stnode.DNode):
            assert_node_equal(ramp_value, raw_value)

        else:
            raise ValueError(f"Unexpected type {type(ramp_value)}, {key}")  # pragma: no cover

    # Check that resultantdq gets copied to groupdq
    if hasattr(raw, "resultantdq"):
        assert hasattr(ramp, "groupdq")
        assert not hasattr(ramp, "resultantdq")


def test_science_raw_from_tvac_raw_invalid_input():
    """Test for invalid input"""
    model = datamodels.RampModel(utils.mk_ramp())
    with pytest.raises(ValueError):
        _ = datamodels.ScienceRawModel.from_tvac_raw(model)


@pytest.mark.parametrize(
    "mk_tvac",
    [
        lambda: datamodels.ScienceRawModel(utils.mk_level1_science_raw(shape=(2, 8, 8))),
        lambda: datamodels.TvacModel(utils.mk_tvac(shape=(2, 8, 8))),
        lambda: datamodels.FpsModel(utils.mk_fps(shape=(2, 8, 8))),
    ],
)
def test_science_raw_from_tvac_raw(mk_tvac):
    """Test conversion from expected inputs"""
    tvac = mk_tvac()

    raw = datamodels.ScienceRawModel.from_tvac_raw(tvac)
    for key in raw:
        if not hasattr(tvac, key):
            continue

        raw_value = getattr(raw, key)
        tvac_value = getattr(tvac, key)
        if isinstance(raw_value, np.ndarray):
            assert_array_equal(raw_value, tvac_value.astype(raw_value.dtype))

        elif key == "meta":
            raw_meta = raw_value.to_flat_dict(include_arrays=False, recursive=True)
            tvac_meta = tvac_value.to_flat_dict(include_arrays=False, recursive=True)
            for meta_key in raw_meta:
                if meta_key == "model_type":
                    raw_value[meta_key] = raw.__class__.__name__
                    tvac_value[meta_key] = tvac.__class__.__name__
                    continue
                elif meta_key == "cal_step":
                    continue
                if meta_key in tvac_meta:
                    assert raw_meta[meta_key] == tvac_meta[meta_key]

        elif isinstance(raw_value, stnode.DNode):
            assert_node_equal(raw_value, tvac_value)

        else:
            raise ValueError(f"Unexpected type {type(raw_value)}, {key}")  # pragma: no cover

    # If tvac/fps, check that statistics are handled properly
    if isinstance(tvac, datamodels.TvacModel | datamodels.FpsModel):
        assert hasattr(raw, "extras")
        assert hasattr(raw.extras, "tvac")
        assert hasattr(raw.extras.tvac, "meta")
        assert hasattr(raw.extras.tvac.meta, "statistics")
        assert raw.extras.tvac.meta.statistics == tvac.meta.statistics


@pytest.mark.parametrize("model", datamodels.MODEL_REGISTRY.values())
@pytest.mark.filterwarnings("ignore:Input shape must be 1D")
@pytest.mark.filterwarnings("ignore:This function assumes shape is 2D")
@pytest.mark.filterwarnings("ignore:Input shape must be 4D")
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


def test_datamodel_save_filename(tmp_path):
    filename = tmp_path / "fancy_filename.asdf"
    ramp = utils.mk_datamodel(datamodels.RampModel, shape=(2, 8, 8))
    assert ramp.meta.filename != filename.name

    ramp.save(filename)
    assert ramp.meta.filename != filename.name

    with datamodels.open(filename) as new_ramp:
        assert new_ramp.meta.filename == filename.name


@pytest.mark.parametrize(
    "model_class, expect_success",
    [
        # FPS and TVAC datamodels need to be commented out
        # until translation methods are written for the pipeline
        # (datamodels.FpsModel, True),
        (datamodels.RampModel, True),
        (datamodels.ScienceRawModel, True),
        # (datamodels.TvacModel, True),
        (datamodels.MosaicModel, False),
    ],
)
def test_rampmodel_from_science_raw(tmp_path, model_class, expect_success):
    """Test creation of RampModel from raw science/tvac"""
    model = utils.mk_datamodel(
        model_class, meta={"calibration_software_version": "1.2.3", "exposure": {"read_pattern": [[1], [2], [3]]}}
    )
    if expect_success:
        filename = tmp_path / "fancy_filename.asdf"
        ramp = datamodels.RampModel.from_science_raw(model)

        assert ramp.meta.calibration_software_version == model.meta.calibration_software_version
        assert ramp.meta.exposure.read_pattern == model.meta.exposure.read_pattern
        assert ramp.validate() is None

        ramp.save(filename)
        with datamodels.open(filename) as new_ramp:
            assert new_ramp.meta.calibration_software_version == model.meta.calibration_software_version

    else:
        with pytest.raises((ValueError, ValidationError)):
            datamodels.RampModel.from_science_raw(model)


@pytest.mark.parametrize(
    "model_class",
    [datamodels.FpsModel, datamodels.RampModel, datamodels.ScienceRawModel, datamodels.TvacModel, datamodels.MosaicModel],
)
def test_model_assignment_access_types(model_class):
    """Test assignment and access of model keyword value via keys and dot notation"""
    # Test creation
    model = utils.mk_datamodel(
        model_class, meta={"calibration_software_version": "1.2.3", "exposure": {"read_pattern": [[1], [2], [3]]}}
    )

    assert model["meta"]["filename"] == model.meta["filename"]
    assert model["meta"]["filename"] == model.meta.filename
    assert model.meta.filename == model.meta["filename"]
    assert type(model["meta"]["filename"]) == type(model.meta["filename"])  # noqa: E721
    assert type(model["meta"]["filename"]) == type(model.meta.filename)  # noqa: E721
    assert type(model.meta.filename) == type(model.meta["filename"])  # noqa: E721

    # Test assignment
    model2 = utils.mk_datamodel(model_class, meta={"calibration_software_version": "4.5.6"})

    model.meta["filename"] = "Roman_keys_test.asdf"
    model2.meta.filename = "Roman_dot_test.asdf"

    assert model.validate() is None
    assert model2.validate() is None

    # Test assignment types
    assert type(model["meta"]["filename"]) == type(model2.meta["filename"])  # noqa: E721
    assert type(model["meta"]["filename"]) == type(model2.meta.filename)  # noqa: E721
    assert type(model.meta.filename) == type(model2.meta["filename"])  # noqa: E721


def test_default_array_compression(tmp_path):
    """
    Test that saving a model results in compressed arrays
    for default options.
    """
    fn = tmp_path / "foo.asdf"
    model = utils.mk_datamodel(datamodels.ImageModel)
    model.save(fn)
    with asdf.open(fn) as af:
        assert af.get_array_compression(af["roman"]["data"]) == "lz4"


@pytest.mark.parametrize("compression", [None, "bzp2"])
def test_array_compression_override(tmp_path, compression):
    """
    Test that providing a compression argument changes the
    array compression.
    """
    fn = tmp_path / "foo.asdf"
    model = utils.mk_datamodel(datamodels.ImageModel)
    model.save(fn, all_array_compression=compression)
    with asdf.open(fn) as af:
        assert af.get_array_compression(af["roman"]["data"]) == compression


@pytest.mark.parametrize("storage", [None, "inline", "internal", "external"])
def test_array_storage_override(tmp_path, storage):
    """
    Test that providing a compression argument changes the
    array compression.
    """
    fn = tmp_path / "foo.asdf"
    model = utils.mk_datamodel(datamodels.ImageModel, shape=(2, 2))
    model.save(fn, all_array_storage=storage)
    with asdf.open(fn) as af:
        assert af.get_array_storage(af["roman"]["data"]) == "internal" if storage is None else storage


def test_apcorr_none_array():
    """
    Check that ApcorrRefModel data arrays can be None.
    """
    m = utils.mk_datamodel(datamodels.ApcorrRefModel)
    # data uses a pattern property so no need to test all
    for name in ("ap_corrections", "ee_fractions", "ee_radii", "sky_background_rin", "sky_background_rout"):
        setattr(m.data.GRISM, name, None)
    assert m.validate() is None


def test_make_wfi_wcs():
    """
    Check create of WfiWcsModel.
    """
    m = utils.mk_datamodel(datamodels.WfiWcsModel)

    assert m.validate() is None


def test_wfi_wcs_from_wcsmodel():
    """Test basic WfiWcsModel creation"""
    model = datamodels.ImageModel(utils.mk_level2_image(shape=(8, 8)))

    # Give the model's WCS a bounding box.
    model.meta.wcs.bounding_box = ((-0.5, 4087.5), (-0.5, 4087.5))

    # Give the model some alignment results
    model.meta["wcs_fit_results"] = {
        "<rot>": 1.2078100852299566e-05,
        "<scale>": 1.0,
        "center": [-3.090428960153321, -18.122328864329525],
        "fitgeom": "rshift",
        "mae": 0.0017789920274088183,
        "matrix": [[0.9999999999999778, 2.108026272605592e-07], [-2.108026272605592e-07, 0.9999999999999778]],
        "nmatches": 109,
        "proper": True,
        "proper_rot": 1.2078100852299566e-05,
        "rmse": 0.0022859902707182554,
        "rot": [1.2078100852299566e-05, 1.2078100852299566e-05],
        "scale": [1.0, 1.0],
        "shift": [0.00017039070698617517, -0.00023752675967125825],
        "skew": 0.0,
        "status": "SUCCESS",
    }

    wfi_wcs = datamodels.WfiWcsModel.from_model_with_wcs(model)

    # Perform overall validation. No assert needed; `validate` will raise ValidationError
    wfi_wcs.validate()

    # Test meta copied from input model
    for key in wfi_wcs.meta:
        wfi_wcs_value = getattr(wfi_wcs.meta, key)
        model_value = getattr(model.meta, key)
        assert_node_equal(wfi_wcs_value, model_value)

    # Test wcs fidelity
    border = 4.0  # Default extra border for L1
    model_corner = model.meta.wcs.pixel_to_world(0.0, 0.0)
    wfi_wcs_corner = wfi_wcs.wcs_l1.pixel_to_world(border, border)  # Extra border due to being L1
    assert model_corner.separation(wfi_wcs_corner).value <= 1e-7

    model_bb = model.meta.wcs.bounding_box
    wfi_wcs_bb = wfi_wcs.wcs_l1.bounding_box
    assert model_bb[0][1] + 2 * border == wfi_wcs_bb[0][1]
    assert model_bb[1][1] + 2 * border == wfi_wcs_bb[1][1]


def test_wfi_wcs_no_wcs(caplog):
    """Test providing an ImageModel without a wcs produces a valid WfiWcsModel with no wcses."""
    model = datamodels.ImageModel(utils.mk_level2_image(shape=(8, 8)))
    model.meta.wcs = None

    wfi_wcs = datamodels.WfiWcsModel.from_model_with_wcs(model)
    assert wfi_wcs.validate() is None

    assert not hasattr(wfi_wcs, "wcs_l1")

    assert not hasattr(wfi_wcs, "wcs_l2")

    assert "Model has no WCS defined" in caplog.text


def test_deepcopy_after_use():
    """
    Test that nodes constructed from using models can be copied

    See: https://github.com/spacetelescope/roman_datamodels/issues/486
    """
    m = datamodels.ImageModel()
    m.meta = {}
    deepcopy(m.meta)


@pytest.mark.parametrize("model", datamodels.MODEL_REGISTRY.values())
def test_create_minimal(model):
    """Test that create_minimal produces a model instance"""
    m = model.create_minimal()
    assert isinstance(m, model)


@pytest.mark.parametrize("model", datamodels.MODEL_REGISTRY.values())
def test_create_fake_data(model):
    """Test that create_fake_data produces a valid model instance"""
    m = model.create_fake_data()
    assert isinstance(m, model)
    assert m.validate() is None


@pytest.mark.parametrize("model", datamodels.MODEL_REGISTRY.values())
def test_create_minimal_copies(model, tmp_path):
    """Test that create_minimal does not retain references to input"""
    fn = tmp_path / "test.asdf"
    fake = model.create_fake_data()
    fake.save(fn)
    with datamodels.open(fn) as opened_model:
        new_model = model.create_minimal(opened_model)
    del opened_model
    gc.collect(2)
    assert new_model.validate() is None


def test_deepcopy_is_deep():
    """
    Test that a deepcopy of a datamodel results in a deep copy.
    """
    model = datamodels.ImageModel(utils.mk_level2_image(shape=(8, 8)))
    model_copy = deepcopy(model)
    assert model_copy is not model
    assert model_copy.data is not model.data
    assert_node_is_copy(model_copy._instance, model._instance, True)


def test_model_dir():
    """
    Test that dir(model) returns attributes (to allow tab completion)
    """
    model = datamodels.ImageModel(utils.mk_level2_image(shape=(8, 8)))
    items = dir(model)
    assert "meta" in items
    # also make sure methods are present
    assert "to_flat_dict" in items
    # and nested items
    assert "exposure" in dir(model.meta)
