from __future__ import annotations

import inspect
import string
import warnings
from typing import get_args, get_type_hints

import _stnode as stubs
import astropy.units as u
import numpy as np
from astropy.time import Time

from roman_datamodels import stnode
from roman_datamodels._typing import enums

NODE_CLASSES_BY_NAME = {cls.__name__: cls for cls in stnode.NODE_CLASSES}
STUB_CLASSES_BY_NAME = {name: cls for name, cls in inspect.getmembers(stubs, inspect.isclass)}
ENUM_CLASSES_BY_NAME = {name: cls for name, cls in inspect.getmembers(enums, inspect.isclass)}

SCALAR_CLASSES_BY_NAME = {cls.__name__: cls for cls in stnode.NODE_CLASSES if issubclass(cls, stnode.TaggedScalarNode)}


RNG = np.random.default_rng()
LOW = -1e3
HIGH = 1e3
STRING_LENGTH = 32
TIME_0 = 1577836800.0  # unix date: 2020-01-01
TIME_1 = 1893456000.0  # unix date: 2030-01-01
LIST_0 = 0
LIST_1 = 10

_HEX_ALPHABET = np.array(list(string.hexdigits))


DEFAULT_SHAPES = {
    1: (4096,),
    2: (4096, 4096),
    3: (2, 4096, 4096),
    4: (2, 4, 4096, 4096),
    5: (2, 8, 16, 32, 32),
}


def create_array(value):
    """
    Create from array type hint description
    """
    args = get_args(value)
    return RNG.uniform(low=LOW, high=HIGH, size=DEFAULT_SHAPES[args[0]]).astype(args[1])


def create_quantity(value):
    """
    Create from quantity type hint description
    """
    args = get_args(value)
    array = create_array(args[0])
    return u.Quantity(array, unit=args[1], dtype=array.dtype)


def create_lnode(value):
    """
    Create from LNode type hint description
    """
    args = get_args(value)
    return [create_hint(args[0]) for _ in range(RNG.integers(low=LIST_0, high=LIST_1))]


def create_int(value):
    """
    Create from int type hint description
    """
    return int(RNG.integers(low=LOW, high=HIGH))


def create_float(value):
    """
    Create from float type hint description
    """
    return float(RNG.uniform(low=LOW, high=HIGH))


def create_string(value):
    """
    Create from string type hint description
    """
    return str(RNG.choice(_HEX_ALPHABET, size=STRING_LENGTH).view(f"U{STRING_LENGTH}")[0])


def create_bool(value):
    """
    Create from bool type hint description
    """
    return bool(RNG.integers(0, 2))


def create_time(value):
    """
    Create from Time hint description
    """

    # Some of these times are beyond the accuracy of astropy.time due to unknown
    # leap second corrections (future), so astropy emits a warning. We don't care
    # as we are just generating times in the mission window.
    with warnings.catch_warnings():
        return Time(RNG.uniform(low=TIME_0, high=TIME_1), format="unix")


# Map of type hints to creation functions
SELECT_BASE = {
    "ndarray": create_array,
    "Quantity": create_quantity,
    "int": create_int,
    "float": create_float,
    "str": create_string,
    "bool": create_bool,
    "Time": create_time,
    "LNode": create_lnode,
}


def create_hint(value):
    """
    Create from a base type hint
    """
    if comp := SELECT_BASE.get(value.__name__, None):
        return comp(value)

    raise ValueError(f"Cannot create type: {value}")


def create_enum(value):
    """
    Create from the enum class
    """
    return RNG.choice([str(val) for val in value])


def create_scalar_class(value):
    """
    Create from a TaggedScalarNode class
    """
    base_cls = value.__bases__[0]

    # Enumerated scalar values
    if base_cls.__name__ in ENUM_CLASSES_BY_NAME:
        return create_enum(ENUM_CLASSES_BY_NAME[base_cls.__name__])

    return create_hint(base_cls)


def create_sub_tree(value):
    """
    Create fill out the sub-tree of a node
    """
    if tree := create_stub(value):
        return tree

    return create_hint(value)


def create_tree(cls):
    """
    Fill out the tree of a node
    """
    return {name: create_sub_tree(value) for name, value in get_type_hints(cls).items()}


def create_stub_class(value):
    """
    Create from a Stub "node" class
    """
    name = value.__name__
    tree = create_tree(value)

    # Construct a Node if it exists
    if name in NODE_CLASSES_BY_NAME:
        return NODE_CLASSES_BY_NAME[name](tree)

    return tree


def create_stub(value):
    """
    Create full Node version of its TypeStub
    """
    name = value.__name__

    if name in SCALAR_CLASSES_BY_NAME:
        return create_scalar_class(SCALAR_CLASSES_BY_NAME[name])

    if name in STUB_CLASSES_BY_NAME:
        return create_stub_class(STUB_CLASSES_BY_NAME[name])

    if name in ENUM_CLASSES_BY_NAME:
        return create_enum(ENUM_CLASSES_BY_NAME[name])

    return None
