"""
Basic utility functions used in the core sub-package
"""
from __future__ import annotations

__all__ = ["annotation_type", "field_name", "merge_dicts"]

from inspect import isclass
from typing import Any, get_args


def annotation_type(annotation: type) -> type:
    """Recursively discover the actual type of an annotation"""

    if isclass(annotation):
        return annotation

    # Required for Python 3.10 support because Any is not a "class" in python < 3.11
    if annotation is Any:
        return object

    return annotation_type(get_args(annotation)[0])


def field_name(field_name: str) -> str:
    """
    Remove the trailing underscore from a field name if it exists

    This is because a trailing underscore is added to any field name that conflicts
    with a Python keyword, but the schemas do not have the trailing underscore.
    """
    return field_name[:-1] if field_name.endswith("_") else field_name


def merge_dicts(base_dict: dict[str, Any], new_dict: dict[str, Any]) -> dict[str, Any]:
    """
    Merge two dicts together, recursively merging sub-dicts
    """
    # Loop over the new_dict and merge it into the base_dict
    for key, value in new_dict.items():
        if key in base_dict and isinstance(value, dict):
            # If the new_dict key is present, recursively merge the data down.
            if isinstance(base_dict[key], dict):
                # _merge_dicts needs base_dict to be an actual dict
                base_dict[key] = merge_dicts(base_dict[key], value)
            elif not isinstance(base_dict[key], dict) and not isinstance(value, dict):
                # This is where we are updating a plane value
                base_dict[key] = value
            else:
                # Something went wrong here
                raise ValueError(f"Cannot merge {type(base_dict[key])} and {type(value)}")
        else:
            # If the new_dict key is not present, just set it.
            #    We do allow extras, so this can set these if necessary
            base_dict[key] = value

    return base_dict
