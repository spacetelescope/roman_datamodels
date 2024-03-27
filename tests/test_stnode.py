import os
from contextlib import nullcontext

import asdf
import astropy.units as u
import pytest
from asdf.exceptions import ValidationError

from roman_datamodels import datamodels
from roman_datamodels import maker_utils
from roman_datamodels import maker_utils as utils
from roman_datamodels import stnode, validate
from roman_datamodels.testing import assert_node_equal, assert_node_is_copy, wraps_hashable

from .conftest import MANIFEST


@pytest.mark.parametrize("tag", MANIFEST["tags"])
def test_generated_node_classes(tag):
    class_name = stnode._factories.class_name_from_tag_uri(tag["tag_uri"])
    node_class = getattr(stnode, class_name)

    assert issubclass(node_class, (stnode.TaggedObjectNode, stnode.TaggedListNode, stnode.TaggedScalarNode))
    assert node_class._tag == tag["tag_uri"]
    assert tag["description"] in node_class.__doc__
    assert tag["tag_uri"] in node_class.__doc__
    assert node_class.__module__ == stnode.__name__
    assert hasattr(stnode, node_class.__name__)


@pytest.mark.parametrize("node_class", stnode.NODE_CLASSES)
@pytest.mark.filterwarnings("ignore:This function assumes shape is 2D")
@pytest.mark.filterwarnings("ignore:Input shape must be 5D")
def test_copy(node_class):
    """Demonstrate nodes can copy themselves, but don't always deepcopy."""
    node = maker_utils.mk_node(node_class, shape=(8, 8, 8))
    node_copy = node.copy()

    # Assert the copy is shallow:
    assert_node_is_copy(node, node_copy, deepcopy=False)

    # If the node only wraps hashable values, then it should "deepcopy" itself because
    # the immutable values cannot actually be copied. In the case, where there is an
    # unhashable value, then the node should not deepcopy itself.
    with nullcontext() if wraps_hashable(node) else pytest.raises(AssertionError):
        assert_node_is_copy(node, node_copy, deepcopy=True)


@pytest.mark.parametrize("node_class", datamodels.MODEL_REGISTRY.keys())
@pytest.mark.filterwarnings("ignore:This function assumes shape is 2D")
@pytest.mark.filterwarnings("ignore:Input shape must be 5D")
def test_deepcopy_model(node_class):
    node = maker_utils.mk_node(node_class, shape=(8, 8, 8))
    model = datamodels.MODEL_REGISTRY[node_class](node)
    model_copy = model.copy()

    # There is no assert equal for models, but the data inside is what we care about.
    # this is stored under the _instance attribute. We can assert those instances are
    # deep copies of each other.
    assert_node_is_copy(model._instance, model_copy._instance, deepcopy=True)


def test_wfi_mode():
    """
    The WfiMode class includes special properties that map optical_element
    values to grating or filter.
    """
    node = stnode.WfiMode({"optical_element": "GRISM"})
    assert node.optical_element == "GRISM"
    assert node.grating == "GRISM"
    assert node.filter is None
    assert isinstance(node, stnode.DNode)
    assert isinstance(node, stnode._mixins.WfiModeMixin)

    node = stnode.WfiMode({"optical_element": "PRISM"})
    assert node.optical_element == "PRISM"
    assert node.grating == "PRISM"
    assert node.filter is None
    assert isinstance(node, stnode.DNode)
    assert isinstance(node, stnode._mixins.WfiModeMixin)

    node = stnode.WfiMode({"optical_element": "F129"})
    assert node.optical_element == "F129"
    assert node.grating is None
    assert node.filter == "F129"
    assert isinstance(node, stnode.DNode)
    assert isinstance(node, stnode._mixins.WfiModeMixin)


@pytest.mark.parametrize("node_class", stnode.NODE_CLASSES)
@pytest.mark.filterwarnings("ignore:This function assumes shape is 2D")
@pytest.mark.filterwarnings("ignore:Input shape must be 5D")
def test_serialization(node_class, tmp_path):
    file_path = tmp_path / "test.asdf"

    node = maker_utils.mk_node(node_class, shape=(8, 8, 8))
    with asdf.AsdfFile() as af:
        af["node"] = node
        af.write_to(file_path)

    with asdf.open(file_path) as af:
        assert_node_equal(af["node"], node)


def test_info(capsys):
    node = stnode.WfiMode({"optical_element": "GRISM", "detector": "WFI18", "name": "WFI"})
    tree = dict(wfimode=node)
    af = asdf.AsdfFile(tree)
    af.info()
    captured = capsys.readouterr()
    assert "optical_element" in captured.out
    assert "GRISM" in captured.out


def test_schema_info():
    node = stnode.WfiMode({"optical_element": "GRISM", "detector": "WFI18", "name": "WFI"})
    tree = dict(wfimode=node)
    af = asdf.AsdfFile(tree)

    info = af.schema_info("archive_catalog")
    assert info == {
        "wfimode": {
            "detector": {
                "archive_catalog": (
                    {
                        "datatype": "nvarchar(10)",
                        "destination": ["WFIExposure.detector", "GuideWindow.detector", "WFICommon.detector"],
                    },
                    "WFI18",
                )
            },
            "name": {
                "archive_catalog": (
                    {
                        "datatype": "nvarchar(5)",
                        "destination": [
                            "WFIExposure.instrument_name",
                            "GuideWindow.instrument_name",
                            "WFICommon.instrument_name",
                        ],
                    },
                    "WFI",
                )
            },
            "optical_element": {
                "archive_catalog": (
                    {
                        "datatype": "nvarchar(20)",
                        "destination": [
                            "WFIExposure.optical_element",
                            "GuideWindow.optical_element",
                            "WFICommon.optical_element",
                        ],
                    },
                    "GRISM",
                )
            },
        }
    }


def test_set_pattern_properties():
    """
    Regression test for patternProperties not being validated
    """

    # This model uses includes a patternProperty
    mdl = maker_utils.mk_wfi_img_photom()

    # This should be invalid because it is not a quantity
    with pytest.raises(asdf.ValidationError):
        mdl.phot_table.F062.photmjsr = 3.14
    with pytest.raises(asdf.ValidationError):
        mdl.phot_table.F062.uncertainty = 3.14
    with pytest.raises(asdf.ValidationError):
        mdl.phot_table.F062.pixelareasr = 3.14

    # This is invalid be cause it is not a scalar
    with pytest.raises(asdf.ValidationError):
        mdl.phot_table.F062.photmjsr = [37.0] * (u.MJy / u.sr)
    with pytest.raises(asdf.ValidationError):
        mdl.phot_table.F062.uncertainty = [37.0] * (u.MJy / u.sr)
    with pytest.raises(asdf.ValidationError):
        mdl.phot_table.F062.pixelareasr = [37.0] * u.sr

    # This should be invalid because it has the wrong unit
    with pytest.raises(asdf.ValidationError):
        mdl.phot_table.F062.photmjsr = 3.14 * u.m
    with pytest.raises(asdf.ValidationError):
        mdl.phot_table.F062.uncertainty = 3.14 * u.m
    with pytest.raises(asdf.ValidationError):
        mdl.phot_table.F062.pixelareasr = 3.14 * u.m

    # Test some valid values (including the rest of the patternProperties)
    mdl.phot_table.F062.photmjsr = 3.14 * (u.MJy / u.sr)
    mdl.phot_table.F062.uncertainty = 0.1 * (u.MJy / u.sr)
    mdl.phot_table.F062.pixelareasr = 37.0 * u.sr

    # Test it can be None (including the rest of the patternProperties)
    mdl.phot_table.F062.photmjsr = None
    mdl.phot_table.F062.uncertainty = None
    mdl.phot_table.F062.pixelareasr = None


# Test that a currently undefined attribute can be assigned using dot notation
# so long as the attribute is defined in the corresponding schema.
def test_node_new_attribute_assignment():
    exp = stnode.Exposure()
    with pytest.raises(AttributeError):
        exp.bozo = 0
    exp.ngroups = 5
    assert exp.ngroups == 5
    # Test patternProperties attribute case
    photmod = utils.mk_wfi_img_photom()
    phottab = photmod.phot_table
    newphottab = {"F062": phottab["F062"]}
    photmod.phot_table = newphottab
    photmod.phot_table.F213 = phottab["F213"]
    with pytest.raises(AttributeError):
        photmod.phot_table.F214 = phottab["F213"]
    with pytest.raises(ValidationError):
        photmod.phot_table.F106 = 0


VALIDATION_CASES = ("true", "yes", "1", "True", "Yes", "TrUe", "YeS", "foo", "Bar", "BaZ")


@pytest.mark.parametrize("nuke_env_var", VALIDATION_CASES, indirect=True)
def test_will_validate(nuke_env_var):
    # Test the fixture passed the value of the environment variable
    value = nuke_env_var[0]
    assert os.getenv(validate.ROMAN_VALIDATE) == value

    # Test the validate property
    truth = nuke_env_var[1]
    context = nullcontext() if truth else pytest.warns(validate.ValidationWarning)

    with context:
        assert validate.will_validate() is truth

    # Try all uppercase
    os.environ[validate.ROMAN_VALIDATE] = value.upper()
    with context:
        assert validate.will_validate() is truth

    # Try all lowercase
    os.environ[validate.ROMAN_VALIDATE] = value.lower()
    with context:
        assert validate.will_validate() is truth

    # Remove the environment variable to test the default value
    del os.environ[validate.ROMAN_VALIDATE]
    assert os.getenv(validate.ROMAN_VALIDATE) is None
    assert validate.will_validate() is True


@pytest.mark.parametrize("nuke_env_var", VALIDATION_CASES, indirect=True)
def test_nuke_validation(nuke_env_var, tmp_path):
    context = pytest.raises(asdf.ValidationError) if nuke_env_var[1] else pytest.warns(validate.ValidationWarning)

    # Create a broken DNode object
    mdl = maker_utils.mk_wfi_img_photom()
    mdl["phot_table"] = "THIS IS NOT VALID"
    with context:
        datamodels.WfiImgPhotomRefModel(mdl)

    # __setattr__ a broken value
    mdl = maker_utils.mk_wfi_img_photom()
    with context:
        mdl.phot_table = "THIS IS NOT VALID"

    # Break model without outside validation
    with nullcontext() if nuke_env_var[1] else pytest.warns(validate.ValidationWarning):
        mdl = datamodels.WfiImgPhotomRefModel(maker_utils.mk_wfi_img_photom())
    mdl._instance["phot_table"] = "THIS IS NOT VALID"

    # Broken can be written to file
    broken_save = tmp_path / "broken_save.asdf"
    with context:
        mdl.save(broken_save)
    assert os.path.isfile(broken_save) is not nuke_env_var[1]

    broken_to_asdf = tmp_path / "broken_to_asdf.asdf"
    with context:
        mdl.to_asdf(broken_to_asdf)
    assert os.path.isfile(broken_to_asdf) is not nuke_env_var[1]

    # Create a broken file for reading if needed
    if nuke_env_var[1]:
        os.environ[validate.ROMAN_VALIDATE] = "false"
        with pytest.warns(validate.ValidationWarning):
            mdl.save(broken_save)
            mdl.to_asdf(broken_to_asdf)
        os.environ[validate.ROMAN_VALIDATE] = nuke_env_var[0]

    # Read broken files with datamodel object
    with context:
        datamodels.WfiImgPhotomRefModel(broken_save)
    with context:
        datamodels.WfiImgPhotomRefModel(broken_to_asdf)

    # True to read broken files with rdm.open
    with context:
        with datamodels.open(broken_save):
            pass
    with context:
        with datamodels.open(broken_to_asdf):
            pass


@pytest.mark.parametrize("nuke_env_strict_var", VALIDATION_CASES, indirect=True)
def test_will_strict_validate(nuke_env_strict_var):
    # Test the fixture passed the value of the environment variable
    assert os.getenv(validate.ROMAN_STRICT_VALIDATION) == nuke_env_strict_var

    # Test the validate property
    truth = nuke_env_strict_var.lower() in ["true", "yes", "1"]
    context = nullcontext() if truth else pytest.warns(validate.ValidationWarning)

    with context:
        assert validate.will_strict_validate() is truth

    # Try all uppercase
    os.environ[validate.ROMAN_STRICT_VALIDATION] = nuke_env_strict_var.upper()
    with context:
        assert validate.will_strict_validate() is truth

    # Try all lowercase
    os.environ[validate.ROMAN_STRICT_VALIDATION] = nuke_env_strict_var.lower()
    with context:
        assert validate.will_strict_validate() is truth

    # Remove the environment variable to test the default value
    del os.environ[validate.ROMAN_STRICT_VALIDATION]
    assert os.getenv(validate.ROMAN_STRICT_VALIDATION) is None
    assert validate.will_strict_validate() is True


@pytest.mark.parametrize("model", [mdl for mdl in datamodels.MODEL_REGISTRY.values() if "Ref" not in mdl.__name__])
def test_node_representation(model):
    """
    Regression test for #244.

    The DNode object was lacking the __repr__ method, which is used to return
    the representation of the object. The reported issue was with ``mdl.meta.instrument``,
    so that is directly checked here.
    """
    mdl = maker_utils.mk_datamodel(model)

    if hasattr(mdl, "meta"):
        if isinstance(mdl, (datamodels.MosaicModel, datamodels.MosaicSegmentationMapModel, datamodels.MosaicSourceCatalogModel)):
            assert repr(mdl.meta.basic) == repr(
                {
                    "time_first_mjd": -999999,
                    "time_last_mjd": -999999,
                    "time_mean_mjd": -999999,
                    "max_exposure_time": -999999,
                    "mean_exposure_time": -999999,
                    "visit": -999999,
                    "segment": -999999,
                    "pass": -999999,
                    "program": "dummy value",
                    "survey": "dummy value",
                    "optical_element": "F158",
                    "instrument": "WFI",
                    "location_name": "dummy value",
                    "product_type": "dummy value",
                }
            )
            model_types = {
                datamodels.MosaicModel: "MosaicModel",
                datamodels.MosaicSegmentationMapModel: "MosaicSegmentationMapModel",
                datamodels.MosaicSourceCatalogModel: "MosaicSourceCatalogModel",
            }
            assert mdl.meta.model_type == model_types[type(mdl)]
            assert mdl.meta.telescope == "ROMAN"
            assert mdl.meta.filename == "dummy value"
        elif isinstance(mdl, (datamodels.SegmentationMapModel, datamodels.SourceCatalogModel)):
            assert mdl.meta.optical_element == "F158"
        else:
            assert repr(mdl.meta.instrument) == repr(
                {
                    "name": "WFI",
                    "detector": "WFI01",
                    "optical_element": "F158",
                }
            )
