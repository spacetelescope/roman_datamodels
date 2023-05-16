from __future__ import annotations

import importlib.util as util
import inspect
import string
import sys
import warnings
from pathlib import Path
from typing import get_args, get_type_hints

try:
    import _stnode as stubs
except ModuleNotFoundError:
    name = "roman_datamodels._typing._stnode"
    path = Path(__file__).parent / "_stnode.py"
    spec = util.spec_from_file_location(name, path)
    stubs = util.module_from_spec(spec)
    if name not in sys.modules:
        sys.modules[name] = stubs
    else:
        raise ImportError(f"Could not find module {name}")
    spec.loader.exec_module(stubs)

import astropy.units as u
import numpy as np
from astropy.modeling.models import Shift
from astropy.time import Time

from roman_datamodels import stnode
from roman_datamodels._typing import enums

NODE_CLASSES_BY_NAME = {cls.__name__: cls for cls in stnode.NODE_CLASSES}
STUB_CLASSES_BY_NAME = {name: cls for name, cls in inspect.getmembers(stubs, inspect.isclass)}
ENUM_CLASSES_BY_NAME = {name: cls for name, cls in inspect.getmembers(enums, inspect.isclass)}
SCALAR_CLASSES_BY_NAME = {cls.__name__: cls for cls in stnode.NODE_CLASSES if issubclass(cls, stnode.TaggedScalarNode)}
LIST_CLASSES_BY_NAME = {cls.__name__: cls for cls in stnode.NODE_CLASSES if issubclass(cls, stnode.TaggedListNode)}


RNG = np.random.default_rng()
LOW = -1e3
HIGH = 1e3
STRING_LENGTH = 32
TIME_0 = 1577836800.0  # unix date: 2020-01-01
TIME_1 = 1893456000.0  # unix date: 2030-01-01
LIST_0 = 1
LIST_1 = 10

RANDOM_DEFAULT = True
NONUM = -999999
NOSTR = "dummy value"

_HEX_ALPHABET = np.array(list(string.hexdigits))


DEFAULT_SHAPES = {
    1: (4096,),
    2: (4096, 4096),
    3: (2, 4096, 4096),
    4: (2, 4, 4096, 4096),
    5: (2, 8, 16, 32, 32),
}

REPLACE_NAME = {
    "pass_": "pass",
}


def create_array(value, random=None):
    """
    Create from array type hint description
    """
    random = RANDOM_DEFAULT if random is None else random

    args = get_args(value)
    if random:
        return RNG.uniform(low=LOW, high=HIGH, size=DEFAULT_SHAPES[args[0]]).astype(args[1])

    return np.zeros(DEFAULT_SHAPES[args[0]], dtype=args[1])


def create_quantity(value, random=None):
    """
    Create from quantity type hint description
    """
    random = RANDOM_DEFAULT if random is None else random

    args = get_args(value)
    array = create_array(args[0], random)
    return u.Quantity(array, unit=args[1], dtype=array.dtype)


def create_lnode(value, random=None):
    """
    Create from LNode type hint description
    """
    random = RANDOM_DEFAULT if random is None else random

    args = get_args(value)
    if random:
        return [create_hint(args[0], random) for _ in range(RNG.integers(low=LIST_0, high=LIST_1))]

    return [create_hint(args[0], random) for _ in range(LIST_1)]


def create_list_class(value, random=None):
    """
    Create an LNode based class
    """
    random = RANDOM_DEFAULT if random is None else random

    if random:
        return value([create_string(value) for _ in range(RNG.integers(low=LIST_0, high=LIST_1))])

    return value(
        [
            "2021-11-15T09:15:07.12Z :: FlatFieldStep :: INFO :: Completed",
            "2021-11-15T10:22.55.55Z :: RampFittingStep :: WARNING :: Wow, lots of Cosmic Rays detected",
        ]
    )


def create_optional(value, random=None):
    """
    Create from optional (meaning has value or is None) type hint description
    """
    random = RANDOM_DEFAULT if random is None else random

    args = get_args(value)
    if random and bool(RNG.integers(0, 2)):
        return None

    return create_hint(args[0], random)


def create_annotated(value, random=None):
    """
    Create from annotated type hint
    """
    random = RANDOM_DEFAULT if random is None else random

    args = get_args(value)

    if issubclass(args[0], u.Quantity):
        return u.Quantity(create_float(value, random), unit=args[1])

    if args[0].__name__ in ENUM_CLASSES_BY_NAME:
        if random:
            components = [create_enum(args[0]) for _ in range(RNG.integers(low=LIST_0, high=LIST_1))]

            return f"{args[1].join(components)}{args[1]}"

        return "WFI_IMAGE|WFI_GRISM|WFI_PRISM|"

    raise ValueError(f"Cannot handle annotated type: {value} {args}")


def create_int(value, random=None):
    """
    Create from int type hint description
    """
    random = RANDOM_DEFAULT if random is None else random

    if random:
        return int(RNG.integers(low=LOW, high=HIGH))

    return int(NONUM)


def create_float(value, random=None):
    """
    Create from float type hint description
    """
    random = RANDOM_DEFAULT if random is None else random

    if random:
        return float(RNG.uniform(low=LOW, high=HIGH))

    return float(NONUM)


def create_string(value, random=None):
    """
    Create from string type hint description
    """
    random = RANDOM_DEFAULT if random is None else random

    if random:
        return str(RNG.choice(_HEX_ALPHABET, size=STRING_LENGTH).view(f"U{STRING_LENGTH}")[0])

    return str(NOSTR)


def create_bool(value, random=None):
    """
    Create from bool type hint description
    """
    random = RANDOM_DEFAULT if random is None else random

    if random:
        return bool(RNG.integers(0, 2))

    return True


def create_time(value, random=None):
    """
    Create from Time hint description
    """
    random = RANDOM_DEFAULT if random is None else random

    if random:
        # Some of these times are beyond the accuracy of astropy.time due to unknown
        # leap second corrections (future), so astropy emits a warning. We don't care
        # as we are just generating times in the mission window.
        with warnings.catch_warnings():
            return Time(RNG.uniform(low=TIME_0, high=TIME_1), format="unix")

    return Time("2020-01-01T00:00:00.0", format="isot", scale="utc")


def create_unit(value, random=None):
    """
    Get the unit from the type hint
    """

    return get_args(value)[0]


def create_model(value, random=None):
    """
    Create a model from the type hint
    """
    random = RANDOM_DEFAULT if random is None else random

    if random:
        return Shift(create_float(value)) & Shift(create_float(value))

    return Shift(0.4) & Shift(3.14)


def create_product(value, random=None):
    """
    Create an association product from the type hint
    """
    random = RANDOM_DEFAULT if random is None else random

    if random:
        return {
            "name": create_string(value),
            "members": [create_string(value) for _ in range(RNG.integers(low=LIST_0, high=LIST_1))],
        }

    return {"name": "NAME", "members": [str(NOSTR) for _ in range(LIST_1)]}


def create_enum(value, random=None):
    """
    Create from the enum class
    """
    random = RANDOM_DEFAULT if random is None else random

    values = [str(val) for val in value]
    if random:
        return RNG.choice(values)

    return values[0]


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
    "Optional": create_optional,
    "Annotated": create_annotated,
    "Unit": create_unit,
    "Model": create_model,
    "_AssociationProduct": create_product,
}


def create_hint(value, random):
    """
    Create from a base type hint
    """
    if comp := SELECT_BASE.get(value.__name__, None):
        return comp(value, random)

    raise ValueError(f"Cannot create type: {value}, {value.__name__}, {get_args(value)}")


def create_scalar_class(value, random):
    """
    Create from a TaggedScalarNode class
    """
    base_cls = value.__bases__[0]

    # Enumerated scalar values
    if value.__name__ in ENUM_CLASSES_BY_NAME:
        return value(create_enum(ENUM_CLASSES_BY_NAME[value.__name__]))

    return value(create_hint(base_cls, random))


def create_sub_tree(value, random):
    """
    Create fill out the sub-tree of a node
    """
    if tree := create_stub(value, random):
        return tree

    return create_hint(value, random)


def create_tree(cls, random):
    """
    Fill out the tree of a node
    """
    return {
        REPLACE_NAME.get(name, name): create_sub_tree(value, random)
        for name, value in get_type_hints(cls, include_extras=True).items()
    }


def create_stub_class(value, random):
    """
    Create from a Stub "node" class
    """
    name = value.__name__
    tree = create_tree(value, random)

    # Construct a Node if it exists
    if name in NODE_CLASSES_BY_NAME:
        return NODE_CLASSES_BY_NAME[name](tree)

    return tree


def create_stub(value, random=None):
    """
    Create full Node version of its TypeStub
    """
    name = value.__name__

    if name in SCALAR_CLASSES_BY_NAME:
        return create_scalar_class(SCALAR_CLASSES_BY_NAME[name], random)

    if name in LIST_CLASSES_BY_NAME:
        return create_list_class(LIST_CLASSES_BY_NAME[name], random)

    if name in STUB_CLASSES_BY_NAME:
        return create_stub_class(STUB_CLASSES_BY_NAME[name], random)

    if name in ENUM_CLASSES_BY_NAME:
        return create_enum(ENUM_CLASSES_BY_NAME[name], random)

    return None
