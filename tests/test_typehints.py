import asdf
import pytest
from astropy.time import Time

from roman_datamodels import nodes
from roman_datamodels.stnode import core, rad
from roman_datamodels.testing import assert_node_equal


class TypeguardExample(core.DNode):
    @rad.field
    def good(self) -> int:
        """This should not raise an error"""
        return 1

    @rad.field
    def bad(self) -> int:
        """This should raise an error"""
        return "1"


@pytest.mark.usefixtures("enable_typeguard")
def test_typeguard_is_functioning():
    """
    Test that the decorator has loaded up the typeguard module.
    -> This smokes out if typeguard is not getting picked up during testing.
    """
    from typeguard import TypeCheckError

    assert core.get_config().typeguard_enabled is True

    instance = TypeguardExample()
    assert instance.good == 1

    with pytest.raises(TypeCheckError):
        _ = instance.bad


def test_typeguard_decorator():
    """
    This checks that we don't get an error when typeguard is not enabled.
    -> This smokes out getting a typeguard error when it is not enabled.
    """
    assert core.get_config().typeguard_enabled is False

    instance = TypeguardExample()
    assert instance.good == 1  # always fine
    assert instance.bad == "1"  # should fail if typeguard is enabled


@pytest.mark.usefixtures("enable_typeguard")
@pytest.mark.parametrize("node_cls", rad.RDM_NODE_REGISTRY.object_nodes.values())
def test_type_annotations(node_cls):
    """
    This will test all @fields's in the given node class.
        -> flush(EXTRA) will cause all of the fields to have their default values set.
        -> test_check_defaults_against_schemas will check that the default values are valid relative
           to the RAD schemas
    """
    instance = node_cls()
    instance.flush(flush=core.FlushOptions.EXTRA)


@pytest.mark.usefixtures("use_testing_shape")
@pytest.mark.parametrize("node_cls", rad.RDM_NODE_REGISTRY.tagged_registry.values())
def test_check_defaults_against_schemas(tmp_path, node_cls):
    """
    Test that the default values for all fields in a given node class are valid relative to the RAD schemas.
        -> with test_type_annoations this confirms that all the annotations are correct

    This is one of the most important tests for the nodes it integrates a lot of core functionality and
    checks into one test. It does the following:
        0. Check that the node can be instanticated relatively empty (except for tagged scalars)
        1. The node is identifying its required fields correctly.
        2. Tests that all of the required fields have a default value.
        3. Tests the serialization process creates required fields as needed
           during serialization itself
        4. Tests that the node with default values can be serialized to asdf
           -> This in particular tests that the default values have the correct type.
           -> Combined passes here with passes of `test_type_annotations` ensures
              that the listed type annotations for the fields are correct.
        5. Tests that the serialized node can be read back in.
        6. Tests that all the untagged nodes and wrappers get properly re-wrapped
           as they are accessed.
    """

    # The tagged scalars require us to pass in a value
    if issubclass(node_cls, Time):
        instance = node_cls(Time("2020-01-01T00:00:00.0", format="isot", scale="utc"))
    elif node_cls is nodes.Origin or node_cls is nodes.FpsOrigin or node_cls is nodes.TvacOrigin:
        instance = node_cls.STSCI
    elif node_cls is nodes.Telescope or node_cls is nodes.FpsTelescope or node_cls is nodes.TvacTelescope:
        instance = node_cls.ROMAN

    # All the non-scalar tagged nodes can simply be instantiated as they will auto fill
    else:
        instance = node_cls()

    # Set an instance into an asdf file object
    af = asdf.AsdfFile()
    af["roman"] = instance

    # Run asdf serialization and write to a file
    filepath = tmp_path / "test.asdf"
    af.write_to(filepath)

    # Deserialize the file and check that the node is equal to the original
    with asdf.open(filepath) as af:
        # Note that this will require the lazy re-wrapping of non-tagged nodes
        assert_node_equal(instance, af["roman"])
