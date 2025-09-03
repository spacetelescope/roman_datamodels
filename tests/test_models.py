import gc
from contextlib import nullcontext
from copy import deepcopy

import asdf
import numpy as np
import pytest
from asdf.exceptions import ValidationError
from astropy import units as u
from astropy.time import Time
from numpy.testing import assert_array_equal

from roman_datamodels import datamodels, stnode, validate
from roman_datamodels.testing import assert_node_equal, assert_node_is_copy

from .conftest import MANIFESTS

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
def test_node_type_matches_model(model):
    """
    Test that the _node_type listed for each model is what is listed in the schema
    """
    node_type = model._node_type
    node = node_type.create_fake_data()
    schema = node.get_schema()
    name = schema["datamodel_name"]

    assert model.__name__ == name


@pytest.mark.parametrize("model", datamodels.MODEL_REGISTRY.values())
def test_model_schemas(model):
    instance = model.create_fake_data()
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
    mdl._instance = node.create_fake_data()
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

    wfi_image = stnode.WfiImage.create_fake_data(shape=(8, 8))
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


def test_add_model_attribute(tmp_path):
    # First make test reference file
    file_path = tmp_path / "testreadnoise.asdf"
    file_path2 = tmp_path / "testreadnoise2.asdf"

    readnoise = datamodels.ReadnoiseRefModel.create_fake_data()
    readnoise.save(file_path)

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

    readnoise = datamodels.ReadnoiseRefModel.create_fake_data(shape=(8, 8))
    readnoise.save(file_path)
    with datamodels.open(file_path) as readnoise:
        assert readnoise["data"].shape == (8, 8)
        assert readnoise.data is readnoise["data"]


# Test that attributes can be assigned object instances without raising exceptions
# unless they don't match the corresponding tag
def test_node_assignment():
    """Test round trip attribute access and assignment"""
    wfi_image = datamodels.ImageModel.create_fake_data()
    exposure = wfi_image.meta.exposure
    assert isinstance(exposure, stnode.DNode)
    wfi_image.meta.exposure = exposure
    assert isinstance(wfi_image.meta.exposure, stnode.DNode)

    # The following tests that supplying a LNode passes validation.
    rampmodel = datamodels.RampModel.create_fake_data()
    rampmodel.meta.exposure.read_pattern = [1, 2, 3]
    assert isinstance(rampmodel.meta.exposure.read_pattern[1:], stnode.LNode)

    # Test that supplying a DNode passes validation
    darkmodel = datamodels.DarkRefModel.create_fake_data()
    darkexp = darkmodel.meta.exposure
    assert isinstance(darkexp, stnode.DNode)


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
    dm = datamodels.ScienceRawModel.create_fake_data()
    dm.info(max_rows=200)
    captured = capsys.readouterr()
    assert "optical_element" in captured.out
    result = dm.search("optical_element")
    assert dm.meta.instrument.optical_element in repr(result)
    assert result.node == dm.meta.instrument.optical_element


def test_datamodel_schema_info_values():
    dm = datamodels.ScienceRawModel.create_fake_data()
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


@pytest.mark.parametrize(
    "name", (name for name in datamodel_names() if not name.startswith("Fps") and not name.startswith("Tvac"))
)
def test_datamodel_schema_info_existence(name):
    # Loop over datamodels that have archive_catalog entries
    if not name.endswith("RefModel") and name != "AssociationsModel":
        model_class = getattr(datamodels, name)
        model = model_class.create_fake_data()
        info = model.schema_info("archive_catalog")
        for keyword in model.meta.keys():
            # Only DNodes or LNodes need to be canvassed
            if isinstance(model.meta[keyword], stnode.DNode | stnode.LNode):
                # Ignore metadata schemas that lack archive_catalog entries
                if type(model.meta[keyword]) not in NODES_LACKING_ARCHIVE_CATALOG:
                    assert keyword in info["roman"]["meta"]


@pytest.mark.parametrize("include_arrays", (True, False))
def test_to_flat_dict(include_arrays):
    model = datamodels.ImageModel.create_fake_data()
    if include_arrays:
        assert "roman.data" in model.to_flat_dict()
    else:
        assert "roman.data" not in model.to_flat_dict(include_arrays=False)


@pytest.mark.parametrize("model_class", (datamodels.ImageModel, datamodels.RampModel))
def test_crds_parameters(model_class):
    # CRDS uses meta.exposure.start_time to compare to USEAFTER
    model = model_class.create_fake_data()
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
    m = datamodels.ImageModel.create_fake_data(shape=(8, 8))

    # invalidate pointing without using the
    # data model/node api to avoid a validation
    # failure here
    m.meta["pointing"] = {}

    with pytest.raises(ValidationError):
        m.validate()


@pytest.mark.filterwarnings("ignore:ERFA function.*")
@pytest.mark.parametrize("node_class", datamodels.MODEL_REGISTRY.keys())
@pytest.mark.parametrize("correct, model", datamodels.MODEL_REGISTRY.items())
def test_model_only_init_with_correct_node(node_class, correct, model):
    """
    Datamodels should only be initializable with the correct node in the model_registry.
    This checks that it can be initialized with the correct node, and that it cannot be
    with any other node.
    """
    node = node_class.create_fake_data()
    with nullcontext() if node_class is correct else pytest.raises(ValidationError):
        model(node).validate()


@pytest.mark.parametrize(
    "mk_raw",
    [
        lambda: datamodels.ScienceRawModel.create_fake_data(shape=(2, 8, 8)),
        lambda: datamodels.TvacModel.create_fake_data(shape=(2, 8, 8)),
        lambda: datamodels.FpsModel.create_fake_data(shape=(2, 8, 8)),
        lambda: datamodels.RampModel.create_fake_data(shape=(2, 8, 8)),
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
    model = datamodels.RampModel.create_fake_data()
    with pytest.raises(ValueError):
        _ = datamodels.ScienceRawModel.from_tvac_raw(model)


@pytest.mark.parametrize(
    "mk_tvac",
    [
        lambda: datamodels.ScienceRawModel.create_fake_data(shape=(2, 8, 8)),
        lambda: datamodels.TvacModel.create_fake_data(shape=(2, 8, 8)),
        lambda: datamodels.FpsModel.create_fake_data(shape=(2, 8, 8)),
    ],
)
def test_science_raw_from_tvac_raw(mk_tvac):
    """Test conversion from expected inputs"""
    tvac = mk_tvac()
    tvac.meta.statistics = {"mean_counts_per_second": 1}

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


@pytest.mark.parametrize("model_class", datamodels.MODEL_REGISTRY.values())
def test_datamodel_construct_like_from_like(model_class):
    """
    This is a regression test for the issue reported issue #51.

    Namely, if one passes a datamodel instance to the constructor for the datamodel
    of the same type as the instance, an error should not be raised (#51 reports an
    error being raised).

    Based on the discussion in PR #52, this should return exactly the same instance object
    that was passed to the constructor. i.e. it should not return a copy of the instance.
    """

    # Create a model
    model = model_class.create_fake_data()

    # Modify _iscopy as it will be reset to False by initializer if called incorrectly
    model._iscopy = "foo"

    # Pass model instance to model constructor
    new_model = model_class(model)
    assert new_model is model
    assert new_model._iscopy == "foo"  # Verify that the constructor didn't override stuff


def test_datamodel_save_filename(tmp_path):
    """Test that the filename is updated on the saved datamodel"""
    filename = tmp_path / "fancy_filename.asdf"
    ramp = datamodels.RampModel.create_fake_data()
    assert ramp.meta.filename != filename.name

    ramp.save(filename)
    assert ramp.meta.filename != filename.name

    with datamodels.open(filename) as new_ramp:
        assert new_ramp.meta.filename == filename.name


def test_datamodel_save_file_date(tmp_path, monkeypatch):
    """Test that the file date is updated on the saved datamodel"""

    def mock_time_now():
        return Time("2025-01-01T00:00:00.0", format="isot", scale="utc")

    monkeypatch.setattr(Time, "now", mock_time_now)

    filename = tmp_path / "test.asdf"

    ramp = datamodels.RampModel.create_fake_data()
    assert ramp.meta.file_date == Time("2020-01-01T00:00:00.0", format="isot", scale="utc")

    ramp.save(filename)
    # Check that the file date has not been changed on the current model
    assert ramp.meta.file_date == Time("2020-01-01T00:00:00.0", format="isot", scale="utc")

    # Check that the file date has been updated in the saved model
    with datamodels.open(filename) as new_ramp:
        assert new_ramp.meta.file_date != Time("2020-01-01T00:00:00.0", format="isot", scale="utc")
        assert new_ramp.meta.file_date == Time.now()


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
def test_rampmodel_from_science_raw(model_class, expect_success):
    """Test creation of RampModel from raw science/tvac"""
    model = model_class.create_fake_data(
        defaults={"meta": {"calibration_software_version": "1.2.3", "exposure": {"read_pattern": [[1], [2], [3]]}}}
    )
    if expect_success:
        ramp = datamodels.RampModel.from_science_raw(model)

        assert ramp.meta.calibration_software_version == model.meta.calibration_software_version
        assert ramp.meta.exposure.read_pattern == model.meta.exposure.read_pattern
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
    model = model_class.create_fake_data(
        defaults={"meta": {"calibration_software_version": "1.2.3", "exposure": {"read_pattern": [[1], [2], [3]]}}}
    )

    assert model["meta"]["filename"] == model.meta["filename"]
    assert model["meta"]["filename"] == model.meta.filename
    assert model.meta.filename == model.meta["filename"]
    assert type(model["meta"]["filename"]) == type(model.meta["filename"])  # noqa: E721
    assert type(model["meta"]["filename"]) == type(model.meta.filename)  # noqa: E721
    assert type(model.meta.filename) == type(model.meta["filename"])  # noqa: E721

    # Test assignment
    model2 = model_class.create_fake_data(defaults={"meta": {"calibration_software_version": "4.5.6"}})

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
    model = datamodels.ImageModel.create_fake_data()
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
    model = datamodels.ImageModel.create_fake_data()
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
    model = datamodels.ImageModel.create_fake_data(shape=(2, 2))
    model.save(fn, all_array_storage=storage)
    with asdf.open(fn) as af:
        assert af.get_array_storage(af["roman"]["data"]) == "internal" if storage is None else storage


def test_apcorr_none_array():
    """
    Check that ApcorrRefModel data arrays can be None.
    """
    m = datamodels.ApcorrRefModel.create_fake_data()
    m.data.GRISM = {}
    # data uses a pattern property so no need to test all
    for name in ("ap_corrections", "ee_fractions", "ee_radii", "sky_background_rin", "sky_background_rout"):
        setattr(m.data.GRISM, name, None)
    assert m.validate() is None


def test_wfi_wcs_from_wcsmodel():
    """Test basic WfiWcsModel creation"""
    model = datamodels.ImageModel.create_fake_data()

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
    model = datamodels.ImageModel.create_fake_data()
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
    model = datamodels.ImageModel.create_fake_data()
    model_copy = deepcopy(model)
    assert model_copy is not model
    assert model_copy.data is not model.data
    assert_node_is_copy(model_copy._instance, model._instance, True)


def test_model_dir():
    """
    Test that dir(model) returns attributes (to allow tab completion)
    """
    model = datamodels.ImageModel.create_fake_data()
    items = dir(model)
    assert "meta" in items
    # also make sure methods are present
    assert "to_flat_dict" in items
    # and nested items
    assert "exposure" in dir(model.meta)


def test_create_from_model_conversion():
    """
    Use create_from_model to convert from one model type to another.
    Check that extra attributes are preserved.
    """
    raw = datamodels.ScienceRawModel.create_fake_data()
    raw.meta.foo = 1
    ramp = datamodels.RampModel.create_from_model(raw)
    assert isinstance(ramp, datamodels.RampModel)
    assert ramp.meta.foo == 1


def test_create_from_model_dict():
    """
    Use create_from_model to construct a model from a non-model (dict).
    """
    model = datamodels.ImageModel.create_from_model({"meta": {"observation": {"visit": 42}}})
    assert isinstance(model, datamodels.ImageModel)
    assert isinstance(model.meta.observation, stnode.Observation)
    assert model.meta.observation.visit == 42


def test_create_from_model_old_tags():
    """
    Use create_from_model to update tags from old to new/default versions.
    """
    old_model_tag = "asdf://stsci.edu/datamodels/roman/tags/wfi_image-1.2.0"
    old_observation_tag = "asdf://stsci.edu/datamodels/roman/tags/observation-1.0.0"
    new_model_tag = stnode.WfiImage._default_tag
    new_observation_tag = stnode.Observation._default_tag

    # check tags aren't defaults (which is required for this test)
    assert old_model_tag != new_model_tag
    assert old_observation_tag != new_observation_tag

    old_model = datamodels.ImageModel.create_fake_data()
    old_model._instance._read_tag = old_model_tag
    old_model.meta.observation._read_tag = old_observation_tag

    converted = datamodels.ImageModel.create_from_model(old_model)
    assert converted.tag == new_model_tag
    assert converted.meta.observation.tag == new_observation_tag
