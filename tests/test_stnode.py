import os
from contextlib import nullcontext

import asdf
import pytest

from roman_datamodels import datamodels, nodes, stnode, validate
from roman_datamodels.testing import assert_node_is_copy


@pytest.mark.usefixtures("use_testing_shape")
@pytest.mark.parametrize(
    "node_cls", [cls for cls in stnode.RDM_NODE_REGISTRY.object_nodes.values() if not issubclass(cls, datamodels.DataModel)]
)
def test_copy(node_cls):
    """Demonstrate nodes can copy themselves, but don't always deepcopy."""
    node = node_cls()
    node.flush(stnode.FlushOptions.EXTRA)
    assert node._data is not None
    node_copy = node.copy()

    # Assert the copy is shallow:
    assert_node_is_copy(node, node_copy, deepcopy=False)


@pytest.mark.usefixtures("use_testing_shape")
@pytest.mark.parametrize("node_cls", stnode.RDM_NODE_REGISTRY.datamodels.values())
def test_deepcopy_model(node_cls):
    model = node_cls()
    model.flush(stnode.FlushOptions.EXTRA, recurse=True)
    model_copy = model.copy()
    assert model is not model_copy

    assert_node_is_copy(model, model_copy, deepcopy=True)


@pytest.mark.usefixtures("use_testing_shape")
def test_wfi_mode():
    """
    The WfiMode class includes special properties that map optical_element
    values to grating or filter.
    """
    node = nodes.WfiMode({"optical_element": "GRISM"})
    assert node.optical_element == "GRISM"
    assert node.grating == "GRISM"
    assert node.filter is None
    assert isinstance(node, stnode.DNode)

    node = nodes.WfiMode({"optical_element": "PRISM"})
    assert node.optical_element == "PRISM"
    assert node.grating == "PRISM"
    assert node.filter is None
    assert isinstance(node, stnode.DNode)

    node = nodes.WfiMode({"optical_element": "F129"})
    assert node.optical_element == "F129"
    assert node.grating is None
    assert node.filter == "F129"
    assert isinstance(node, stnode.DNode)


@pytest.mark.usefixtures("use_testing_shape")
def test_info(capsys):
    node = nodes.WfiMode({"optical_element": "GRISM", "detector": "WFI18", "name": "WFI"})
    tree = dict(wfimode=node)
    af = asdf.AsdfFile(tree)
    af.info()
    captured = capsys.readouterr()
    assert "optical_element" in captured.out
    assert "GRISM" in captured.out


@pytest.mark.usefixtures("use_testing_shape")
def test_schema_info():
    node = nodes.WfiMode({"optical_element": "GRISM", "detector": "WFI18", "name": "WFI"})
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


# Test that a currently undefined attribute can be assigned using dot notation
# so long as the attribute is defined in the corresponding schema.
@pytest.mark.usefixtures("use_testing_shape")
def test_node_new_attribute_assignment():
    exp = nodes.Exposure()
    exp.nresultants = 5
    assert exp.nresultants == 5
    # Test patternProperties attribute case

    photmod = nodes.WfiImgPhotomRef()
    phottab = photmod.phot_table
    newphottab = {"F062": phottab["F062"]}
    photmod.phot_table = newphottab
    photmod.phot_table.F213 = phottab["F213"]
    with pytest.raises(AttributeError):
        photmod.phot_table.F214 = phottab["F213"]


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


@pytest.mark.usefixtures("use_testing_shape")
@pytest.mark.parametrize("nuke_env_var", VALIDATION_CASES, indirect=True)
def test_nuke_validation(nuke_env_var, tmp_path):
    context = pytest.raises(asdf.ValidationError) if nuke_env_var[1] else pytest.warns(validate.ValidationWarning)

    # Break model without outside validation
    mdl = datamodels.WfiImgPhotomRefModel()
    mdl["phot_table"] = "THIS IS NOT VALID"

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


@pytest.mark.usefixtures("use_testing_shape")
@pytest.mark.parametrize("model", [mdl for mdl in stnode.RDM_NODE_REGISTRY.datamodels.values() if "Ref" not in mdl.__name__])
def test_node_representation(model):
    """
    Regression test for #244.

    The DNode object was lacking the __repr__ method, which is used to return
    the representation of the object. The reported issue was with ``mdl.meta.instrument``,
    so that is directly checked here.
    """
    mdl = model()
    mdl.flush(stnode.FlushOptions.EXTRA, recurse=True)

    if hasattr(mdl, "meta"):
        if isinstance(mdl, datamodels.MosaicModel | datamodels.MosaicSegmentationMapModel | datamodels.MosaicSourceCatalogModel):
            assert repr(mdl.meta.basic) == repr(
                {
                    "instrument": "WFI",
                    "location_name": stnode.NOSTR,
                    "max_exposure_time": stnode.NONUM,
                    "mean_exposure_time": stnode.NONUM,
                    "optical_element": "F158",
                    "pass": stnode.NOINT,
                    "product_type": stnode.NOSTR,
                    "program": stnode.NOINT,
                    "segment": stnode.NOINT,
                    "survey": stnode.NOSTR,
                    "time_first_mjd": stnode.NONUM,
                    "time_last_mjd": stnode.NONUM,
                    "time_mean_mjd": stnode.NONUM,
                    "visit": stnode.NOINT,
                }
            )
            model_types = {
                datamodels.MosaicModel: "MosaicModel",
                datamodels.MosaicSegmentationMapModel: "MosaicSegmentationMapModel",
                datamodels.MosaicSourceCatalogModel: "MosaicSourceCatalogModel",
            }
            assert mdl.meta.model_type == model_types[type(mdl)]
            assert mdl.meta.telescope == "ROMAN"
            assert mdl.meta.filename == stnode.NOFN
        elif isinstance(mdl, datamodels.SegmentationMapModel | datamodels.ImageSourceCatalogModel):
            assert mdl.meta.optical_element == "F158"
        else:
            assert repr(mdl.meta.instrument) == repr(
                {
                    "detector": "WFI01",
                    "name": "WFI",
                    "optical_element": "F158",
                }
            )
