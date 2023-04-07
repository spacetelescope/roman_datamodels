from copy import copy

import pytest

from roman_datamodels.stuserdict import STUserDict


def test_init():
    input_1 = {"a": 1, "b": 2, "c": 3}
    input_2 = {"first": 1, "second": 2, "third": 3, "b": 3}
    input_3 = {0: "first", 1: "second"}
    input_4 = {b"test": 344, "0": True, "b": 3}

    user_dict_1 = STUserDict(input_1)
    user_dict_2 = STUserDict(input_1, **input_2)
    user_dict_3 = STUserDict(**input_1)
    with pytest.warns(DeprecationWarning, match=r"Passing 'dict' as keyword argument is deprecated"):
        user_dict_4 = STUserDict(dict=input_1)

    with pytest.raises(TypeError):
        STUserDict(**input_3)

    with pytest.raises(TypeError):
        STUserDict(**input_4)

    with pytest.raises(TypeError):
        STUserDict(input_1, **input_4)

    with pytest.raises(TypeError):
        STUserDict(input_1, input_4)

    assert user_dict_1 == input_1

    assert user_dict_2 == {**input_1, **input_2}
    assert user_dict_2 != user_dict_1

    assert user_dict_3 == input_1
    assert user_dict_3 == user_dict_1

    assert user_dict_4 == input_1


def test_datamodel():
    input_1 = {"a": 1, "b": 2, "c": 3}
    input_2 = {"first": 1, "second": 2, "third": 3, "b": 3}

    user_dict_1 = STUserDict(**input_1)
    user_dict_2 = STUserDict(input_1, **input_2)

    assert len(user_dict_1) == 3
    assert list(user_dict_1) == list(input_1)
    assert user_dict_1["b"] == 2

    assert len(user_dict_2) == 6
    assert list(user_dict_2) == list({**input_1, **input_2})
    assert user_dict_2["b"] == 3

    with pytest.raises(KeyError):
        user_dict_1["test"]

    user_dict_1["c"] = 4
    user_dict_1["test"] = "test value"

    assert user_dict_1["c"] == 4
    assert "test" in user_dict_1
    assert user_dict_1["test"] == "test value"

    del user_dict_1["test"]

    assert "test" not in user_dict_1


def test_copy():
    input_1 = {"a": 1, "b": 2, "c": 3}
    input_2 = {"first": 1, "second": 2, "third": 3, "b": 3}

    user_dict_1 = STUserDict(**input_1)
    user_dict_2 = STUserDict(input_1, **input_2)

    user_dict_3 = copy(user_dict_1)
    user_dict_4 = user_dict_2.copy()

    assert user_dict_3 == user_dict_1
    assert user_dict_3 != user_dict_2

    assert user_dict_3 is not user_dict_1
    assert user_dict_3._data is not user_dict_1._data

    assert user_dict_4 == user_dict_2
    assert user_dict_4 != user_dict_1

    assert user_dict_4 is not user_dict_2
    assert user_dict_4._data is not user_dict_2._data


def test_from_keys():
    keys_1 = ["a", "b", "c"]

    user_dict_1 = STUserDict.fromkeys(keys_1)
    user_dict_2 = STUserDict.fromkeys(keys_1, value=1)

    assert list(user_dict_1) == list(user_dict_2)
    assert user_dict_1 != user_dict_2
