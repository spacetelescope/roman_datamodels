"""
This contains the logic to turn schema information related to third party types
that have Pydatnic adaptors into the python code using those adaptors.

    Effectively, this module acts as a parser of the third-party "tagged" schema
    information into python code snippets which can be used in the generated code.
"""
from __future__ import annotations

__all__ = ["has_adaptor", "adaptor_factory"]

from typing import TYPE_CHECKING

from datamodel_code_generator.imports import Import
from datamodel_code_generator.types import DataType

from roman_datamodels.core import adaptors

from ._utils import remove_uri_version

if TYPE_CHECKING:
    # Prevent a runtime import loop for the sake of type annotations
    from ._schema import RadSchemaObject


FROM_ = adaptors.__name__  # string representing the import of adaptors

ASDF_TAGS = set()
for adaptor_tags in adaptors.ADAPTORS.keys():
    ASDF_TAGS.update(adaptor_tags)


def has_adaptor(obj: RadSchemaObject) -> bool:
    """
    Determine if we have an adaptor for the given tag

    Parameters
    ----------
    obj :
        The parsed schema object

    Returns
    -------
    if the tag is supported via an adaptor.
    """
    if obj.tag is None:
        return False

    return remove_uri_version(obj.tag) in ASDF_TAGS


def adaptor_factory(obj: RadSchemaObject, data_type: DataType) -> DataType:
    """
    Create the data type for the given tag

    Note this works by generating two variables:
        type_ : str
            The string which will be written exactly as the adaptor's representation
            in the generated code.
        import_ : str
            A comma separated list of imports from `roman_datamodels.core.adaptors` which
            are needed in the generated code in order to import what is needed by `type_`.

    Parameters
    ----------
    obj :
        The parsed schema object
    data_type : DataType
        DataType template to modify

    Returns
    -------
    DataType object with type and import_ set so that the strings can be used as
    real python code.
    """
    tag = remove_uri_version(obj.tag)

    for adaptor_tags, adaptor in adaptors.ADAPTORS.items():
        if tag in adaptor_tags:
            adaptor_gen = adaptor.code_generator(obj)
            break
    else:
        # Use of this function should be gated by has_adaptor
        raise NotImplementedError(f"Unsupported tag: {obj.tag}")

    # Create the DataType object
    #    Note this needs to be a copy so we don't back-modify the original
    d_type = data_type.model_copy()

    # Set the type, which will be the code snippet as a string which will be exactly
    #    what is written in the generated code for the annotation in this case.
    d_type.type = adaptor_gen.type_

    # from_ and import_ are strings such that the import added into the form is of the form
    #   from <from_> import <import_>
    # These are the imports needed to support the type code snippet above.
    d_type.import_ = Import(from_=FROM_, import_=adaptor_gen.import_)

    return d_type
