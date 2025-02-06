import warnings
from contextlib import nullcontext

import asdf
import numpy as np
import pytest
from asdf.exceptions import ValidationError
from astropy import units as u
from astropy.modeling import Model
from astropy.table import QTable, Table
from numpy.testing import assert_array_equal

from roman_datamodels import datamodels, nodes, stnode

# from roman_datamodels import maker_utils as utils
from roman_datamodels.nodes.datamodels.wfi_science_raw import WfiScienceRaw
from roman_datamodels.testing import assert_node_equal

from .conftest import MANIFESTS

EXPECTED_COMMON_REFERENCE = {"$ref": "asdf://stsci.edu/datamodels/roman/schemas/reference_files/ref_common-1.0.0"}

# Nodes for metadata schema that do not contain any archive_catalog keywords
NODES_LACKING_ARCHIVE_CATALOG = [
    nodes.CalLogs,
    nodes.OutlierDetection,
    nodes.MosaicAssociations,
    nodes.IndividualImageMeta,
    nodes.Resample,
    nodes.SkyBackground,
    nodes.SourceCatalog,
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


@pytest.mark.usefixtures("use_testing_shape")
@pytest.mark.parametrize("model", stnode.RDM_NODE_REGISTRY.datamodels.values())
def test_node_type_matches_model(model):
    """
    Test that the _node_type listed for each model is what is listed in the schema
    """
    model = model()
    node = model.node_type()
    schema = node.asdf_schema
    name = schema.schema["datamodel_name"]

    assert type(model).__name__ == name


@pytest.mark.filterwarnings("ignore:ERFA function.*")
@pytest.mark.parametrize("model", stnode.RDM_NODE_REGISTRY.datamodels.values())
def test_model_schemas(model):
    asdf.schema.load_schema(model.asdf_schema_uri)


@pytest.mark.parametrize("node, model", stnode.RDM_NODE_REGISTRY.node_datamodel_mapping.items())
@pytest.mark.parametrize("method", ["info", "search", "schema_info"])
def test_model_asdf_operations(node, model, method):
    """
    Test the decorator for asdf operations on models when an empty initial model
    which is then filled.
    """
    # Create an empty model
    mdl = model()
    assert isinstance(mdl, node)
    assert mdl._asdf is None

    # Run the method we wish to test (it should fail with warning or error
    # if something is broken)
    getattr(mdl, method)()

    # Show that mdl._asdf is now set
    assert mdl._asdf is not None


# Testing core schema
@pytest.mark.usefixtures("use_testing_shape")
def test_core_schema(tmp_path):
    # Set temporary asdf file
    file_path = tmp_path / "test.asdf"

    wfi_image = nodes.WfiImage()
    with asdf.AsdfFile() as af:
        af.tree = {"roman": wfi_image}

        # Test telescope name
        # # ValueError instead of Validation error due to issuing from enum
        with pytest.raises(ValueError):
            af.tree["roman"].meta.telescope = "NOTROMAN"

        # Setting via __setitem__ avoids automatic wrapping
        af.tree["roman"].meta["telescope"] = "NOTROMAN"
        # ValueError instead of Validation error due to issuing from enum
        with pytest.raises(ValueError):
            af.write_to(file_path)
        af.tree["roman"].meta.telescope = "ROMAN"
        # Test origin name
        with pytest.raises(ValueError):
            # See note above for explanation of why both
            # statements are included in the context here.
            af.tree["roman"].meta.origin = "NOTSTSCI"
        af.tree["roman"].meta["origin"] = "NOTIPAC/SSC"
        with pytest.raises(ValueError):
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
        # use _data to avoid automatic wrapping, enum will trigger an error
        assert model.meta._data["telescope"] == "XOMAN"
    asdf.get_config().validate_on_read = True


# RampFitOutput tests
@pytest.mark.usefixtures("use_testing_shape")
def test_make_ramp():
    ramp = nodes.Ramp()

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
@pytest.mark.usefixtures("use_testing_shape")
def test_make_ramp_fit_output():
    rampfitoutput = nodes.RampFitOutput()

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
@pytest.mark.usefixtures("use_testing_shape")
def test_make_msos_stack():
    msos_stack = nodes.MsosStack()

    assert msos_stack.meta.exposure.type == "WFI_IMAGE"
    assert isinstance(msos_stack.meta.image_list, str)

    assert msos_stack.data.dtype == np.float64
    assert msos_stack.uncertainty.dtype == np.float64
    assert msos_stack.mask.dtype == np.uint8
    assert msos_stack.coverage.dtype == np.uint8

    datamodel = datamodels.MsosStackModel(msos_stack)
    assert datamodel.validate() is None


# Associations tests
@pytest.mark.usefixtures("use_testing_shape")
def test_make_associations():
    association = nodes.Associations()
    member_shapes = association.testing_array_shape

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
    exposure = nodes.Exposure()
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


# Guide Window tests
@pytest.mark.usefixtures("use_testing_shape")
def test_make_guidewindow():
    guidewindow = nodes.Guidewindow()

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


# AB Vega Offset Correction tests
@pytest.mark.usefixtures("use_testing_shape")
def test_make_abvegaoffset():
    abvegaoffset = nodes.AbvegaoffsetRef()
    assert abvegaoffset.meta.reftype == "ABVEGAOFFSET"
    assert isinstance(abvegaoffset.data.GRISM.abvega_offset, float)

    # Test validation
    abvegaoffset_model = datamodels.AbvegaoffsetRefModel(abvegaoffset)
    assert abvegaoffset_model.validate() is None


# Aperture Correction tests
@pytest.mark.usefixtures("use_testing_shape")
def test_make_apcorr():
    apcorr = nodes.ApcorrRef()
    assert apcorr.meta.reftype == "APCORR"
    assert isinstance(apcorr.data.DARK.sky_background_rin, float)
    assert isinstance(apcorr.data.DARK.ap_corrections, np.ndarray)
    assert isinstance(apcorr.data.DARK.ap_corrections[0], float)

    # Test validation
    apcorr_model = datamodels.ApcorrRefModel(apcorr)
    assert apcorr_model.validate() is None


# Flat tests
@pytest.mark.usefixtures("use_testing_shape")
def test_make_flat():
    flat = nodes.FlatRef()
    assert flat.meta.reftype == "FLAT"
    assert flat.data.dtype == np.float32
    assert flat.dq.dtype == np.uint32
    assert flat.dq.shape == (8, 8)
    assert flat.err.dtype == np.float32

    # Test validation
    flat_model = datamodels.FlatRefModel(flat)
    assert flat_model.validate() is None


@pytest.mark.usefixtures("use_testing_shape")
def test_flat_model(tmp_path):
    # Set temporary asdf file
    file_path = tmp_path / "test.asdf"

    flatref = nodes.FlatRef()
    flatref.meta.instrument.optical_element = "F158"

    # Testing flat file asdf file
    with asdf.AsdfFile() as af:
        af.tree = {"roman": flatref}
        af.write_to(file_path)

        # Test that asdf file opens properly
        with datamodels.open(file_path) as model:
            with warnings.catch_warnings():
                model.validate()

            # Confirm that asdf file is opened as flat file model
            assert isinstance(model, datamodels.FlatRefModel)


# Dark Current tests
@pytest.mark.usefixtures("use_testing_shape")
def test_make_dark():
    dark = nodes.DarkRef()
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
@pytest.mark.usefixtures("use_testing_shape")
def test_make_distortion():
    distortion = nodes.DistortionRef()
    assert distortion.meta.reftype == "DISTORTION"
    assert isinstance(distortion.coordinate_distortion_transform, Model)

    # Test validation
    distortion_model = datamodels.DistortionRefModel(distortion)
    assert distortion_model.validate() is None


# ePSF tests
@pytest.mark.usefixtures("use_testing_shape")
def test_make_epsf():
    epsf = nodes.EpsfRef()
    assert epsf.meta.reftype == "EPSF"
    assert isinstance(epsf.meta.pixel_x, stnode.LNode)
    assert isinstance(epsf.meta.pixel_x[0], float)
    assert epsf.psf.shape == epsf.testing_array_shape
    assert isinstance(epsf.psf[0, 0, 0, 0, 0], float | np.float32)

    # Test validation
    epsf_model = datamodels.EpsfRefModel(epsf)
    assert epsf_model.validate() is None


# Gain tests
@pytest.mark.usefixtures("use_testing_shape")
def test_make_gain():
    gain = nodes.GainRef()
    assert gain.meta.reftype == "GAIN"
    assert gain.data.dtype == np.float32

    # Test validation
    gain_model = datamodels.GainRefModel(gain)
    assert gain_model.validate() is None


# Gain tests
@pytest.mark.usefixtures("use_testing_shape")
def test_make_ipc():
    ipc = nodes.IpcRef()
    assert ipc.meta.reftype == "IPC"
    assert ipc.data.dtype == np.float32
    assert ipc.data[1, 1] == 1.0
    assert np.sum(ipc.data) == 1.0

    # Test validation
    ipc_model = datamodels.IpcRefModel(ipc)
    assert ipc_model.validate() is None


# Linearity tests
@pytest.mark.usefixtures("use_testing_shape")
def test_make_linearity():
    linearity = nodes.LinearityRef()
    assert linearity.meta.reftype == "LINEARITY"
    assert linearity.coeffs.dtype == np.float32
    assert linearity.dq.dtype == np.uint32

    # Test validation
    linearity_model = datamodels.LinearityRefModel(linearity)
    assert linearity_model.validate() is None


# Inverselinearity tests
@pytest.mark.usefixtures("use_testing_shape")
def test_make_inverselinearity():
    inverselinearity = nodes.InverselinearityRef()
    assert inverselinearity.meta.reftype == "INVERSELINEARITY"
    assert inverselinearity.coeffs.dtype == np.float32
    assert inverselinearity.dq.dtype == np.uint32

    # Test validation
    inverselinearity_model = datamodels.InverselinearityRefModel(inverselinearity)
    assert inverselinearity_model.validate() is None


# Mask tests
@pytest.mark.usefixtures("use_testing_shape")
def test_make_mask():
    mask = nodes.MaskRef()
    assert mask.meta.reftype == "MASK"
    assert mask.dq.dtype == np.uint32

    # Test validation
    mask_model = datamodels.MaskRefModel(mask)
    assert mask_model.validate() is None


# Pixel Area tests
@pytest.mark.usefixtures("use_testing_shape")
def test_make_pixelarea():
    pixelarea = nodes.PixelareaRef()
    assert pixelarea.meta.reftype == "AREA"
    assert pixelarea.data.dtype == np.float32

    # Test validation
    pixelarea_model = datamodels.PixelareaRefModel(pixelarea)
    assert pixelarea_model.validate() is None


# Read Noise tests
@pytest.mark.usefixtures("use_testing_shape")
def test_make_readnoise():
    readnoise = nodes.ReadnoiseRef()
    assert readnoise.meta.reftype == "READNOISE"
    assert readnoise.data.dtype == np.float32

    # Test validation
    readnoise_model = datamodels.ReadnoiseRefModel(readnoise)
    assert readnoise_model.validate() is None


@pytest.mark.usefixtures("use_testing_shape")
def test_add_model_attribute(tmp_path):
    # First make test reference file
    file_path = tmp_path / "testreadnoise.asdf"
    file_path2 = tmp_path / "testreadnoise2.asdf"

    datamodels.ReadnoiseRefModel().to_asdf(file_path)
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


@pytest.mark.usefixtures("use_testing_shape")
def test_model_subscribable(tmp_path):
    """
    Test that __getitem__ exists
    """
    file_path = tmp_path / "testreadnoise.asdf"

    datamodels.ReadnoiseRefModel().to_asdf(file_path)
    with datamodels.open(file_path) as readnoise:
        assert readnoise["data"].shape == (8, 8)
        assert readnoise.data is readnoise["data"]


# Saturation tests
@pytest.mark.usefixtures("use_testing_shape")
def test_make_saturation():
    saturation = nodes.SaturationRef()
    assert saturation.meta.reftype == "SATURATION"
    assert saturation.dq.dtype == np.uint32
    assert saturation.data.dtype == np.float32

    # Test validation
    saturation_model = datamodels.SaturationRefModel(saturation)
    assert saturation_model.validate() is None


# Super Bias tests
@pytest.mark.usefixtures("use_testing_shape")
def test_make_superbias():
    superbias = nodes.SuperbiasRef()
    assert superbias.meta.reftype == "BIAS"
    assert superbias.data.dtype == np.float32
    assert superbias.err.dtype == np.float32
    assert superbias.dq.dtype == np.uint32
    assert superbias.dq.shape == (8, 8)

    # Test validation
    superbias_model = datamodels.SuperbiasRefModel(superbias)
    assert superbias_model.validate() is None


# Refpix tests
@pytest.mark.usefixtures("use_testing_shape")
def test_make_refpix():
    refpix = nodes.RefpixRef()
    assert refpix.meta.reftype == "REFPIX"

    assert refpix.gamma.dtype == np.complex128
    assert refpix.zeta.dtype == np.complex128
    assert refpix.alpha.dtype == np.complex128

    assert refpix.gamma.shape == (32, 840)
    assert refpix.zeta.shape == (32, 840)
    assert refpix.alpha.shape == (32, 840)


# WFI Photom tests
@pytest.mark.usefixtures("use_testing_shape")
def test_make_wfi_img_photom():
    wfi_img_photom = nodes.WfiImgPhotomRef()

    assert wfi_img_photom.meta.reftype == "PHOTOM"

    assert wfi_img_photom.phot_table.PRISM.photmjsr is None
    assert wfi_img_photom.phot_table.PRISM.uncertainty is None

    # Test validation
    wfi_img_photom_model = datamodels.WfiImgPhotomRefModel(wfi_img_photom)
    assert wfi_img_photom_model.validate() is None


# WFI Level 1 Science Raw tests
@pytest.mark.usefixtures("use_testing_shape")
def test_make_level1_science_raw():
    wfi_science_raw = nodes.WfiScienceRaw()

    assert wfi_science_raw.data.dtype == np.uint16

    # Test validation
    wfi_science_raw_model = datamodels.ScienceRawModel(wfi_science_raw)
    assert wfi_science_raw_model.validate() is None


# WFI Level 2 Image tests
@pytest.mark.usefixtures("use_testing_shape")
def test_make_level2_image():
    wfi_image = nodes.WfiImage()

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
@pytest.mark.usefixtures("use_testing_shape")
def test_node_assignment():
    """Test round trip attribute access and assignment"""
    wfi_image = nodes.WfiImage()
    exposure = wfi_image.meta.exposure
    assert isinstance(exposure, stnode.DNode)
    wfi_image.meta.exposure = exposure
    assert isinstance(wfi_image.meta.exposure, stnode.DNode)
    # The following tests that supplying a LNode passes validation.
    rampmodel = datamodels.RampModel()
    assert isinstance(rampmodel.meta.exposure.read_pattern[1:], stnode.LNode)
    rampmodel.meta.exposure.read_pattern = rampmodel.meta.exposure.read_pattern[1:]
    # Test that supplying a DNode passes validation
    darkmodel = datamodels.DarkRefModel()
    darkexp = darkmodel.meta.exposure
    assert isinstance(darkexp, stnode.DNode)


# WFI Level 3 Mosaic tests
@pytest.mark.usefixtures("use_testing_shape")
def test_make_level3_mosaic():
    wfi_mosaic = nodes.WfiMosaic()

    assert wfi_mosaic.data.dtype == np.float32
    assert wfi_mosaic.data.shape == (8, 8)

    assert wfi_mosaic.err.dtype == np.float32
    assert wfi_mosaic.context.dtype == np.uint32
    assert wfi_mosaic.weight.dtype == np.float32
    assert wfi_mosaic.var_poisson.dtype == np.float32
    assert wfi_mosaic.var_rnoise.dtype == np.float32
    assert wfi_mosaic.var_flat.dtype == np.float32
    assert isinstance(wfi_mosaic.cal_logs[0], str)

    # Test validation
    wfi_mosaic_model = datamodels.MosaicModel(wfi_mosaic)
    assert wfi_mosaic_model.validate() is None


# WFI Level 3 Mosaic tests
@pytest.mark.usefixtures("use_testing_shape")
def test_append_individual_image_meta_level3_mosaic():
    wfi_mosaic_model = datamodels.MosaicModel()

    wfi_image1 = nodes.WfiImage()
    wfi_image1.flush(stnode.FlushOptions.EXTRA, recurse=True)
    wfi_image2 = nodes.WfiImage()
    wfi_image2.flush(stnode.FlushOptions.EXTRA, recurse=True)
    wfi_image3 = nodes.WfiImage()
    wfi_image3.flush(stnode.FlushOptions.EXTRA, recurse=True)

    wfi_image1.meta.program.investigator_name = "Nancy"
    wfi_image2.meta.program.investigator_name = "Grace"
    wfi_image3.meta.program.investigator_name = "Roman"
    wfi_image3_model = datamodels.ImageModel(wfi_image3)

    wfi_mosaic_model.append_individual_image_meta(wfi_image1.meta)
    wfi_mosaic_model.append_individual_image_meta(wfi_image2.meta.to_flat_dict())
    wfi_mosaic_model.append_individual_image_meta(wfi_image3_model.meta)

    # Test that basic is a QTable
    assert isinstance(wfi_mosaic_model.meta.individual_image_meta.basic, QTable)

    # Test that each image entry in the instrument table contains the same instrument name
    assert wfi_mosaic_model.meta.individual_image_meta.instrument["name"][0] == "WFI"
    assert (
        wfi_mosaic_model.meta.individual_image_meta.instrument["name"][0]
        == wfi_mosaic_model.meta.individual_image_meta.instrument["name"][1]
    )
    assert (
        wfi_mosaic_model.meta.individual_image_meta.instrument["name"][1]
        == wfi_mosaic_model.meta.individual_image_meta.instrument["name"][2]
    )

    # Test that each image entry in the program table contains the correct (different) PI name
    assert wfi_mosaic_model.meta.individual_image_meta.program["investigator_name"][0] == "Nancy"
    assert wfi_mosaic_model.meta.individual_image_meta.program["investigator_name"][1] == "Grace"
    assert wfi_mosaic_model.meta.individual_image_meta.program["investigator_name"][2] == "Roman"

    # Test that the mosaic validates with IIM filled
    assert wfi_mosaic_model.validate() is None


# FPS tests
@pytest.mark.usefixtures("use_testing_shape")
def test_make_fps():
    fps = nodes.Fps()

    assert fps.data.dtype == np.uint16
    assert fps.data.shape == (2, 8, 8)

    # Test validation
    fps_model = datamodels.FpsModel(fps)
    assert fps_model.validate() is None


# TVAC tests
@pytest.mark.usefixtures("use_testing_shape")
def test_make_tvac():
    tvac = nodes.Tvac()

    assert tvac.data.dtype == np.uint16
    assert tvac.data.unit == u.DN
    assert tvac.data.shape == (2, 8, 8)

    # Test validation
    tvac_model = datamodels.TvacModel(tvac)
    assert tvac_model.validate() is None


@pytest.mark.usefixtures("use_testing_shape")
def test_make_image_source_catalog():
    source_catalog = nodes.ImageSourceCatalog()
    source_catalog_model = datamodels.ImageSourceCatalogModel(source_catalog)

    assert isinstance(source_catalog_model.source_catalog, Table)


@pytest.mark.usefixtures("use_testing_shape")
def test_make_segmentation_map():
    segmentation_map = nodes.SegmentationMap()
    segmentation_map_model = datamodels.SegmentationMapModel(segmentation_map)

    assert isinstance(segmentation_map_model.data, np.ndarray)


@pytest.mark.usefixtures("use_testing_shape")
def test_make_mosaic_source_catalog():
    source_catalog = nodes.MosaicSourceCatalog()
    source_catalog_model = datamodels.MosaicSourceCatalogModel(source_catalog)

    assert isinstance(source_catalog_model.source_catalog, Table)


@pytest.mark.usefixtures("use_testing_shape")
def test_make_mosaic_segmentation_map():
    segmentation_map = nodes.MosaicSegmentationMap()
    segmentation_map_model = datamodels.MosaicSegmentationMapModel(segmentation_map)

    assert isinstance(segmentation_map_model.data, np.ndarray)


@pytest.mark.usefixtures("use_testing_shape")
def test_datamodel_info_search(capsys):
    wfi_science_raw = nodes.WfiScienceRaw()
    af = asdf.AsdfFile()
    af.tree = {"roman": wfi_science_raw}
    with datamodels.open(af) as dm:
        dm.info(max_rows=200)
        captured = capsys.readouterr()
        assert "optical_element" in captured.out
        result = dm.search("optical_element")
        assert "F158" in repr(result)
        assert result.node == "F158"


@pytest.mark.usefixtures("use_testing_shape")
def test_datamodel_schema_info_values():
    wfi_science_raw = WfiScienceRaw()
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
        }


@pytest.mark.parametrize("name", datamodel_names())
def test_datamodel_schema_info_existence(name):
    # Loop over datamodels that have archive_catalog entries
    if not name.endswith("RefModel") and name != "AssociationsModel":
        model = getattr(datamodels, name)()
        model.flush(stnode.FlushOptions.EXTRA, recurse=True)
        info = model.schema_info("archive_catalog")
        for keyword, value in model.meta.items():
            # Only DNodes or LNodes need to be canvassed
            if isinstance(value, stnode.DNode | stnode.LNode) and isinstance(value, stnode.TagMixin):
                # Ignore metadata schemas that lack archive_catalog entries
                if type(model.meta[keyword]) not in NODES_LACKING_ARCHIVE_CATALOG:
                    assert keyword in info["roman"]["meta"]


@pytest.mark.usefixtures("use_testing_shape")
@pytest.mark.parametrize("include_arrays", (True, False))
def test_to_flat_dict(include_arrays, tmp_path):
    file_path = tmp_path / "test.asdf"
    datamodels.ImageModel().to_asdf(file_path)
    with datamodels.open(file_path) as model:
        if include_arrays:
            assert "roman.data" in model.to_flat_dict()
        else:
            assert "roman.data" not in model.to_flat_dict(include_arrays=False)


@pytest.mark.usefixtures("use_testing_shape")
@pytest.mark.parametrize("model", (datamodels.ImageModel, datamodels.RampModel))
def test_crds_parameters(model, tmp_path):
    # CRDS uses meta.exposure.start_time to compare to USEAFTER
    file_path = tmp_path / "test.asdf"
    model().to_asdf(file_path)
    with datamodels.open(file_path) as model:
        # patch on a value that is valid (a simple type)
        # but isn't under meta. Since it's not under meta
        # it shouldn't be in the crds_pars.
        model["test"] = 42
        crds_pars = model.get_crds_parameters()
        assert "roman.meta.exposure.start_time" in crds_pars
        assert "roman.cal_logs" not in crds_pars
        assert "roman.test" not in crds_pars


@pytest.mark.usefixtures("use_testing_shape")
def test_model_validate_without_save(tmp_path):
    # regression test for rcal-538
    m = datamodels.ImageModel()

    # Insert actual bad value
    m.meta.pointing.ra_v1 = "5"

    with pytest.raises(ValidationError):
        m.validate()


@pytest.mark.usefixtures("use_testing_shape")
@pytest.mark.filterwarnings("ignore:ERFA function.*")
@pytest.mark.parametrize("node", stnode.RDM_NODE_REGISTRY.node_datamodel_mapping.keys())
@pytest.mark.parametrize("correct, model", stnode.RDM_NODE_REGISTRY.node_datamodel_mapping.items())
def test_model_only_init_with_correct_node(node, correct, model):
    """
    Datamodels should only be initializable with the correct node in the model_registry.
    This checks that it can be initialized with the correct node, and that it cannot be
    with any other node.
    """
    img = node()
    with nullcontext() if node is correct else pytest.raises(ValidationError):
        model(img)


@pytest.mark.usefixtures("use_testing_shape")
def test_ramp_from_science_raw():
    raw = datamodels.ScienceRawModel()

    ramp = datamodels.RampModel.from_science_raw(raw)
    for key in ramp:
        if not hasattr(raw, key):
            continue

        ramp_value = getattr(ramp, key)
        raw_value = getattr(raw, key)
        if isinstance(ramp_value, np.ndarray):
            assert_array_equal(ramp_value, raw_value.astype(ramp_value.dtype))

        elif key == "meta":
            for meta_key in ramp_value:
                if meta_key == "model_type":
                    ramp_value[meta_key] = type(ramp).__name__
                    raw_value[meta_key] = type(raw).__name__
                    continue
                elif meta_key == "cal_step":
                    continue
                assert_node_equal(ramp_value[meta_key], raw_value[meta_key])

        elif isinstance(ramp_value, stnode.DNode):
            assert_node_equal(ramp_value, raw_value)

        else:
            raise ValueError(f"Unexpected type {type(ramp_value)}, {key}")  # pragma: no cover


@pytest.mark.usefixtures("use_testing_shape")
@pytest.mark.parametrize("model", stnode.RDM_NODE_REGISTRY.node_datamodel_mapping.values())
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
    mdl = model()

    # Modify _iscopy as it will be reset to False by initializer if called incorrectly
    mdl._is_copy = "foo"

    # Pass model instance to model constructor
    new_mdl = model(mdl)
    assert new_mdl is mdl
    assert new_mdl._is_copy == "foo"  # Verify that the constructor didn't override stuff


@pytest.mark.usefixtures("use_testing_shape")
def test_datamodel_save_filename(tmp_path):
    filename = tmp_path / "fancy_filename.asdf"
    ramp = datamodels.RampModel()
    assert ramp.meta.filename != filename.name

    ramp.save(filename)
    assert ramp.meta.filename != filename.name

    with datamodels.open(filename) as new_ramp:
        assert new_ramp.meta.filename == filename.name


@pytest.mark.usefixtures("use_testing_shape")
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
    model = model_class({"meta": {"calibration_software_version": "1.2.3", "exposure": {"read_pattern": [[1], [2], [3]]}}})
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


@pytest.mark.usefixtures("use_testing_shape")
@pytest.mark.parametrize(
    "model_class",
    [datamodels.FpsModel, datamodels.RampModel, datamodels.ScienceRawModel, datamodels.TvacModel, datamodels.MosaicModel],
)
def test_model_assignment_access_types(model_class):
    """Test assignment and access of model keyword value via keys and dot notation"""
    # Test creation
    model = model_class({"meta": {"calibration_software_version": "1.2.3", "exposure": {"read_pattern": [[1], [2], [3]]}}})
    _ = model.meta  # ensure that meta is wrapped

    assert model["meta"]["filename"] == model.meta["filename"]
    assert model["meta"]["filename"] == model.meta.filename
    assert model.meta.filename == model.meta["filename"]
    assert type(model["meta"]["filename"]) is type(model.meta["filename"])
    assert type(model["meta"]["filename"]) is type(model.meta.filename)
    assert type(model.meta.filename) is type(model.meta["filename"])

    # Test assignment
    model2 = model_class({"meta": {"calibration_software_version": "4.5.6"}})

    model.meta["filename"] = "Roman_keys_test.asdf"
    model2.meta.filename = "Roman_dot_test.asdf"

    # assert model.validate() is None
    assert model2.validate() is None

    # Test assignment types
    assert type(model["meta"]["filename"]) is type(model2.meta["filename"])
    assert type(model["meta"]["filename"]) is type(model2.meta.filename)
    assert type(model.meta.filename) is type(model2.meta["filename"])


def test_default_array_compression(tmp_path):
    """
    Test that saving a model results in compressed arrays
    for default options.
    """
    fn = tmp_path / "foo.asdf"
    model = datamodels.ImageModel()
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
    model = datamodels.ImageModel()
    model.save(fn, all_array_compression=compression)
    with asdf.open(fn) as af:
        assert af.get_array_compression(af["roman"]["data"]) == compression
