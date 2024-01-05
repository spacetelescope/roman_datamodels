"""
Base class for all RomanDataModels

Note this contains only the methods needed to support all RomanDataModels whether
they can be directly serialized to ASDF (tagged) or not.
"""
from __future__ import annotations

import abc
import warnings
from collections.abc import Generator
from contextlib import contextmanager
from datetime import datetime
from enum import Enum
from inspect import isclass
from typing import Any, get_args, get_origin

import numpy as np
from astropy.modeling import models
from astropy.time import Time
from pydantic import BaseModel, ConfigDict, RootModel
from pydantic.fields import FieldInfo
from pydantic_core import PydanticUndefined

from .adaptors import get_adaptor
from .metadata import Archive, Archives


class BaseRomanDataModel(BaseModel, abc.ABC):
    model_config = ConfigDict(
        # model_* is a protected namespace for Pydantic, so we have to remove that protection
        # because Basic.model_type is a field we want to use
        protected_namespaces=(),
        # Store the values from an enum not the enum instance
        use_enum_values=True,
        # Allow the model to be populated by field name even if it is aliased.
        #    this is need because pass is a Python syntax word, but it is used as a field name
        #    in the observation schema.
        populate_by_name=True,
        # Allow extra fields to be added to the model
        extra="allow",
        # Validate values when they are set
        validate_assignment=True,
        revalidate_instances="always",
    )

    @abc.abstractproperty
    def schema_uri(cls) -> str:
        ...

    def to_asdf_tree(self) -> dict[str, Any]:
        """
        Convert to an ASDF tree, stopping at tags

        Returns
        -------
        An ASDF tree (dict) representation of this model, it
        """

        # Avoid circular import
        from roman_datamodels.datamodels.datamodel import RomanDataModel

        def recurse_tree(field: Any) -> Any:
            """
            Find the sub-tree for a field
                Note, we do not recurse into tagged models because that will be handled by ASDF

            Parameters
            ----------
            field : Any
                The field to recurse into

            Returns
            -------
            The sub tree for the field
            """
            # Recurse into sub-RomanDataModels that are not TaggedDataModels (so ASDF can tag them)
            if isinstance(field, BaseRomanDataModel) and not isinstance(field, RomanDataModel):
                return field.to_asdf_tree()

            # Recurse into sub-RootModels
            if isinstance(field, RootModel) and (not hasattr(field, "_tag_uri") or field._tag_uri is None):
                return field.root

            # Recurse into sub-dicts
            if isinstance(field, dict):
                return {key: recurse_tree(value) for key, value in field.items()}

            # Recurse into sub-lists
            if isinstance(field, list):
                return [recurse_tree(value) for value in field]

            # Handle enumerations
            if isinstance(field, Enum):
                return field.value

            # Return field if it has no nested data to be serialized
            return field

        # Convert to a dict using built-in Pydantic tricks
        tree = dict(self)
        # loop over loop over the results and recurse into sub-trees converting
        #    as needed
        for field_name, field in tree.items():
            tree[field_name] = recurse_tree(field)

        # Handle the case that we have a conflicting keyword with Python
        return {_field_name(field_name): field for field_name, field in tree.items()}

    @classmethod
    def get_archive_metadata(cls) -> dict[str, Archive | Archives]:
        """Get the archive data for this model"""

        def get_archive(extra: dict[str, Any]) -> Archive:
            """
            Create an archive object

            Parameters
            ----------
            extra : dict[str, Any]
                The json_schema_extra data for a field

            Returns
            -------
            An archive model for this field (it may have no information in it)
            """
            return Archive(**({} if extra is None else extra))

        metadata = {}

        # loop over the fields in this model
        for field_name, field in cls.model_fields.items():
            field_name = _field_name(field_name)

            # Build archive metadata for this field
            if (archive := get_archive(field.json_schema_extra)).has_info:
                metadata[field_name] = archive
                continue  # If there is archive metadata, we are done

            # Recurse into sub-models
            field_type = _annotation_type(field.annotation)

            # Handle the case of field being a RomanDataModel
            #    Note that we do not add the archive metadata if the model has no archive metadata
            if issubclass(field_type, BaseRomanDataModel) and (archive := field_type.get_archive_metadata()):
                metadata[field_name] = archive

            # Handle the case we have a root model
            #    Currently only used for the cal_logs field
            elif issubclass(field_type, RootModel):
                # RootModels will encode their archive metadata in the root field
                extra = field_type.model_fields["root"].json_schema_extra
                if (archive := get_archive(extra)).has_info:
                    metadata[field_name] = archive

        return metadata

    @classmethod
    def make_default(cls, **kwargs) -> BaseRomanDataModel:
        """
        Create a default instance of this model

        Parameters
        ----------
        **kwargs :
            The arguments which can be passed down into the specific default value
            construction logic.

        Returns
        -------
        A constructed version of the model using defaults
        """

        def special_cases(field_name: str) -> Any:
            """
            Handle the special cases for fields that cannot be easily handled by
            the general logic.
            """
            # Read pattern is a list of lists of integers which significantly complicates
            # the generalized logic to implement, it is easier to just hard code it
            if field_name == "read_pattern":
                return [[1], [2, 3], [4], [5, 6, 7, 8], [9, 10], [11]]

            # The cal_logs is currently the only RootModel, it also requires significant
            # complications to implement the general logic, so we hard code it
            if field_name == "cal_logs":
                return [
                    "2021-11-15T09:15:07.12Z :: FlatFieldStep :: INFO :: Completed",
                    "2021-11-15T10:22.55.55Z :: RampFittingStep :: WARNING :: Wow, lots of Cosmic Rays detected",
                ]

            # The p_exptype field is a string, but it has to follow a regular expression
            #  so it cannot be the nominal string default
            if field_name == "p_exptype":
                return "WFI_IMAGE|WFI_GRISM|WFI_PRISM|"

            # The coordinate_distortion_transform field is a compound model, but it is not
            #     currently directly specified in the schemas, so we hard code it for now.
            if field_name == "coordinate_distortion_transform":
                return models.Shift(1) & models.Shift(2)

            return None

        def get_default(field_type: type, **kwargs) -> Any:
            """
            Handle getting the default values for fields
            """

            # Recurse into sub-models
            if issubclass(field_type, BaseRomanDataModel):
                return field_type.make_default(**kwargs)

            # Set default numerical scalars
            if field_type is float or field_type is int:
                return -999999

            # Set default strings
            if field_type is str:
                return "dummy value"

            # Set default booleans
            if field_type is bool:
                return False

            # Choose the first value from an enumeration
            if issubclass(field_type, Enum):
                return next(field_type.__iter__()).value

            return None

        def default_list(field: FieldInfo, **kwargs) -> list:
            """
            Handle default values for lists
            """
            # Loop over the types listed in the annotation to get the default values
            return [get_default(type_, **kwargs) for type_ in get_args(field.annotation)]

        def default_dict(field: FieldInfo, field_name: str, **kwargs) -> dict:
            """
            Handle default values for dicts
            """
            key_type, value_type = get_args(field.annotation)
            keys = (get_default(key_type, **kwargs),)

            # phot_table is a special case because it follows a regular expression,
            #    currently the generator does not encode this into the Pydantic Model
            #    but it is still checked by ASDF during serialization. So we encode
            #    all the normal expected values here. This will be required even if
            #    the generator is updated to encode the regular expression as it will
            #    not be default strings.
            if field_name == "phot_table":
                keys = ("F062", "F087", "F106", "F129", "F146", "F158", "F184", "F213", "GRISM", "PRISM", "DARK")

            # Loop over the keys generating a default for each value
            return {key: get_default(value_type, **kwargs) for key in keys}

        # Build a dict of default values
        defaults = {}
        for field_name, field in cls.model_fields.items():
            field_name = _field_name(field_name)

            # Only bother setting defaults for required fields
            if field.is_required():
                # Check if the field has a default value defined by Pydantic,
                #    if so, use that. That value can technically be set in the
                #    schema via the `default` keyword, but ASDF discourages doing so.
                # The default is set to PydanticUndefined if there is no default
                if field.default is not PydanticUndefined:
                    defaults[field_name] = field.default
                    continue

                # Handle the case of fields that are defined via a PydanticAdaptor
                if (adaptor := get_adaptor(field)) is not None:
                    defaults[field_name] = adaptor.make_default(**kwargs)
                    continue

                # Handle the special cases that cannot be easily handled by the general logic
                if (value := special_cases(field_name)) is not None:
                    defaults[field_name] = value
                    continue

                # Handle the list/dict cases
                if isclass(origin := get_origin(field.annotation)):
                    if issubclass(origin, dict):
                        defaults[field_name] = default_dict(field, field_name, **kwargs)
                        continue

                    if issubclass(origin, list):
                        defaults[field_name] = default_list(field, **kwargs)
                        continue

                # Handle all other cases
                if (value := get_default(_annotation_type(field.annotation), **kwargs)) is not None:
                    defaults[field_name] = value
                    continue

        return cls(**defaults)

    def to_flat_dict(self, include_arrays: bool = True) -> dict[str, Any]:
        """
        Get a flattened dictionary representation of the model.
        """

        def convert_value(value: Any) -> Any:
            """Convert times into strings and leave everything else alone"""
            if isinstance(value, datetime):
                return value.isoformat()

            if isinstance(value, Time):
                return str(value)

            return value

        return {
            name: convert_value(value) for name, value in self.flat_items() if include_arrays or not isinstance(value, np.ndarray)
        }

    def flat_items(self) -> Generator[tuple[str, Any], None, None]:
        def recurse(field: Any, path=None) -> Generator[tuple[str, Any], None, None]:
            if path is None:
                path = []

            # Recurse into sub-RomanDataModels that are not TaggedDataModels (so ASDF can tag them)
            if isinstance(field, BaseRomanDataModel):
                for field_name, value in field:
                    yield from recurse(value, path + [field_name])

            # Recurse into sub-RootModels
            elif isinstance(field, RootModel):
                yield from recurse(field.root, path)

            # Recurse into sub-dicts
            elif isinstance(field, dict):
                for key, value in field.items():
                    yield from recurse(value, path + [key])

            # Recurse into sub-lists
            elif isinstance(field, list):
                for index, value in enumerate(field):
                    yield from recurse(value, path + [index])

            # Handle enumerations
            elif isinstance(field, Enum):
                yield from recurse(field.value, path)

            # Return field if it has no nested data to be serialized
            else:
                yield (".".join(str(name) for name in path), field)

        yield from recurse(self)

    @contextmanager
    def pause_validation(self, *, revalidate_on_exit: bool = True) -> None:
        """Context manager to pause validation of the model within the context."""
        self.model_config["validate_assignment"] = False
        self.model_config["revalidate_instances"] = "never"

        try:
            yield
        finally:
            self.model_config["validate_assignment"] = True
            self.model_config["revalidate_instances"] = "always"

            if revalidate_on_exit:
                self.model_validate(self)

    def __getitem__(self, item: str) -> Any:
        return getattr(self, item)

    def __setitem__(self, key: str, value: Any) -> None:
        warnings.warn(
            "RomanDataModel.__setitem__ circumvents validation, and does not re-validate the model. "
            "This can lead to an invalid model for serialization. Thus this should not be used in "
            "production code.",
            RuntimeWarning,
        )
        with self.pause_validation(revalidate_on_exit=False):
            setattr(self, key, value)

    def __contains__(self, item: str) -> bool:
        return item in self.model_fields or item in self.model_extra


def _annotation_type(annotation: type) -> type:
    """Recursively discover the actual type of an annotation"""

    if isclass(annotation):
        return annotation

    # Required for Python 3.10 support because Any is not a "class" in python < 3.11
    if annotation is Any:
        return object

    return _annotation_type(get_args(annotation)[0])


def _field_name(field_name: str) -> str:
    """
    Remove the trailing underscore from a field name if it exists

    This is because a trailing underscore is added to any field name that conflicts
    with a Python keyword, but the schemas do not have the trailing underscore.
    """
    return field_name[:-1] if field_name.endswith("_") else field_name
