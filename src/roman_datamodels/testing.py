import gwcs
import numpy as np
from asdf.tags.core import NDArrayType
from astropy.modeling import Model
from astropy.table import Table
from numpy.testing import assert_array_equal

from .stnode import DNode, TaggedListNode, TaggedObjectNode, TaggedScalarNode

__all__ = ["assert_node_equal", "assert_node_is_copy", "wraps_hashable"]


def assert_node_equal(node1, node2):
    """
    Assert equality between two nodes, with special handling for numpy
    arrays.

    Parameters
    ----------
    node1 : `roman_datamodels.stnode.TaggedObjectNode`
        First node to compare.
    node2 : `roman_datamodels.stnode.TaggedObjectNode`
        Second node to compare.

    Raises
    ------
    AssertionError
        If nodes are not equal.
    """
    __tracebackhide__ = True

    assert node1.__class__ is node2.__class__
    if isinstance(node1, DNode):
        assert set(node1.keys()) == set(node2.keys())

        for key in node1:
            value1 = getattr(node1, key)
            value2 = getattr(node2, key)
            _assert_value_equal(value1, value2)
    elif isinstance(node1, TaggedListNode):
        assert len(node1) == len(node2)

        for value1, value2 in zip(node1, node2):
            _assert_value_equal(value1, value2)
    elif isinstance(node1, TaggedScalarNode):
        value1 = node1.__class__.__bases__[0](node1)
        value2 = node2.__class__.__bases__[0](node2)

        assert value1 == value2
    else:
        raise RuntimeError(f"Unhandled node class: {node1.__class__.__name__}")


def _assert_value_equal(value1, value2):
    if isinstance(value1, (TaggedObjectNode, TaggedListNode, TaggedScalarNode, DNode)):
        assert_node_equal(value1, value2)
    elif isinstance(value1, (np.ndarray, NDArrayType)):
        assert_array_equal(value1, value2)
    elif isinstance(value1, Model):
        assert_model_equal(value1, value2)
    elif isinstance(value1, Table):
        assert (value1 == value2).all()
    elif isinstance(value1, gwcs.WCS):
        return True
    else:
        assert value1 == value2


def assert_node_is_copy(node1, node2, deepcopy=False):
    """
    Assert that two nodes are a copy of each other, with special handling for
    deep copies.

    Parameters
    ----------
    node1 : `roman_datamodels.stnode.TaggedObjectNode`
        First node to compare.
    node2 : `roman_datamodels.stnode.TaggedObjectNode`
        Second node to compare.

    Raises
    ------
    AssertionError
        If nodes are the same object.
    """
    __tracebackhide__ = True
    assert_node_equal(node1, node2)

    if isinstance(node1, TaggedObjectNode):
        for key, value1 in node1.items():
            value2 = node2[key]
            _assert_value_is_copy(value1, value2, deepcopy=deepcopy)
    elif isinstance(node1, TaggedListNode):
        for value1, value2 in zip(node1, node2):
            _assert_value_is_copy(value1, value2, deepcopy=deepcopy)
    elif isinstance(node1, TaggedScalarNode):
        value1 = node1.__class__.__bases__[0](node1)
        value2 = node2.__class__.__bases__[0](node2)

        assert value1 is not value2
    else:
        raise RuntimeError(f"Unhandled node class: {node1.__class__.__name__}")


def _assert_value_is_copy(value1, value2, deepcopy=False):
    if deepcopy:
        if isinstance(value1, (TaggedObjectNode, TaggedListNode, TaggedScalarNode)):
            assert_node_is_copy(value1, value2)
        elif isinstance(value1, Model):
            assert value1 is not value2
        else:
            # Hashable objects cannot be copied as they are immutable.
            try:
                hash(value1)
            except TypeError:
                assert value1 is not value2
            else:
                assert value1 is value2
    else:
        # No copy was made in the shallow case.
        assert value1 is value2


def wraps_hashable(node):
    """
    Determine if the node wraps only hashable objects.
    """
    __tracebackhide__ = True

    if isinstance(node, TaggedObjectNode):
        return all(_wraps_hashable(value) for value in node.values())

    elif isinstance(node, TaggedListNode):
        return all(_wraps_hashable(value) for value in node)

    elif isinstance(node, TaggedScalarNode):
        return _wraps_hashable(node.__class__.__bases__[0](node))

    else:
        raise RuntimeError(f"Unhandled node class: {node.__class__.__name__}")


def _wraps_hashable(value):
    if isinstance(value, (TaggedObjectNode, TaggedListNode, TaggedScalarNode)):
        return wraps_hashable(value)

    # Immutable types are usually hashable
    try:
        hash(value)
    except TypeError:
        return False

    return True


def assert_model_equal(a, b):
    """
    Assert that two model instances are equivalent.
    """
    if a is None and b is None:
        return

    assert a.__class__ == b.__class__

    assert a.name == b.name
    assert a.inputs == b.inputs
    assert a.input_units == b.input_units
    assert a.outputs == b.outputs
    assert a.input_units_allow_dimensionless == b.input_units_allow_dimensionless
    assert a.input_units_equivalencies == b.input_units_equivalencies

    assert_array_equal(a.parameters, b.parameters)

    try:
        a_bounding_box = a.bounding_box
    except NotImplementedError:
        a_bounding_box = None

    try:
        b_bounding_box = b.bounding_box
    except NotImplementedError:
        b_bounding_box = None

    assert a_bounding_box == b_bounding_box

    assert a.fixed == b.fixed
    assert a.bounds == b.bounds

    assert_model_equal(a._user_inverse, b._user_inverse)
