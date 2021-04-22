from asdf.tags.core import NDArrayType
import numpy as np
from numpy.testing import assert_array_equal

from ..stnode import TaggedObjectNode


def assert_node_equal(node1, node2):
    """
    Assert equality between two nodes, with special handling for numpy
    arrays.

    Parameters
    ----------
    node1 : TaggedObjectNode
        First node to compare.
    node2 : TaggedObjectNode
        Second node to compare.

    Raises
    ------
    AssertionError
        If nodes are not equal.
    """
    __tracebackhide__ = True

    assert node1.__class__ is node2.__class__
    assert set(node1.keys()) == set(node2.keys())

    for key, value1 in node1.items():
        value2 = node2[key]

        if isinstance(value1, TaggedObjectNode):
            assert_node_equal(value1, value2)
        elif isinstance(value1, (np.ndarray, NDArrayType)):
            assert_array_equal(value1, value2)
        else:
            assert value1 == value2
