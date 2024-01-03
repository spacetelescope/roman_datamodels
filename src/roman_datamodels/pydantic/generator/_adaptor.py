from __future__ import annotations

from typing import TYPE_CHECKING

from datamodel_code_generator.imports import Import
from datamodel_code_generator.types import DataType

from ..adaptors._adaptor_tags import asdf_tags
from ..adaptors._astropy_quantity import AstropyQuantity
from ..adaptors._astropy_time import AstropyTime
from ..adaptors._astropy_unit import AstropyUnit
from ..adaptors._ndarray import NdArray

if TYPE_CHECKING:
    # Prevent a runtime import loop for the sake of type annotations
    from roman_datamodels.pydantic.generator._schema import RadSchemaObject


__all__ = ["has_adaptor", "adaptor_factory"]

FROM_ = ".".join(__name__.split(".")[:-1])  # string representing the import of adaptors


def get_tag_key(value):
    """
    Courtesy of https://stackoverflow.com/a/1176023
    """
    import re

    return re.sub(r"(?<!^)(?=[A-Z])", "_", value).upper()


IMPORT_ = {
    get_tag_key(name): name for name, value in locals().items() if value in (AstropyTime, AstropyUnit, AstropyQuantity, NdArray)
}

ASDF_TAGS = {tag.value for tag in asdf_tags}


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
    return obj.tag in ASDF_TAGS


def adaptor_factory(obj: RadSchemaObject, data_type: DataType) -> DataType:
    """
    Create the data type for the given tag

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
    # This can be converted to a match statement when min python is 3.10
    if obj.tag == asdf_tags.ASTROPY_TIME:
        name = IMPORT_[asdf_tags.ASTROPY_TIME.name]

        type_ = name
        import_ = name

    elif obj.tag == asdf_tags.ND_ARRAY:
        name = IMPORT_[asdf_tags.ND_ARRAY.name]

        type_, default_shape, import_ = _ndarray_factory(obj, name)
        type_ = f"{type_}, {tuple(default_shape)}"
        type_ = f"{name}[{type_}]"  # wrap type in NdArray annotation

    elif obj.tag == asdf_tags.ASTROPY_UNIT or obj.tag == asdf_tags.ASDF_UNIT:
        name = IMPORT_[asdf_tags.ASTROPY_UNIT.name]

        type_, import_ = _unit_factory(obj, name)
        type_ = f"{name}[{type_}]"  # wrap type in AstropyUnit annotation

    elif obj.tag == asdf_tags.ASTROPY_QUANTITY:
        name = IMPORT_[asdf_tags.ASTROPY_QUANTITY.name]

        type_, import_ = _quantity_factory(obj.properties, name)
        type_ = f"{name}[{type_}]"  # wrap type in AstropyQuantity annotation

    else:
        raise NotImplementedError(f"Unsupported tag: {obj.tag}")

    # Create the DataType object
    d_type = data_type.copy()  # needs copy so it doesn't modify the original type
    d_type.type = type_
    d_type.import_ = Import(from_=FROM_, import_=import_)

    return d_type


def _ndarray_factory(obj: RadSchemaObject, import_: str) -> tuple[str, list[int] | None, str]:
    """
    Factory to get the type and import for an ndarray

    Parameters
    ----------
    obj :
        The parsed schema object
    import_ : str
        The current import string

    Returns
    -------
    (
        dtype : str
            The argument to the `rad.pydantic.adaptors.NdArray` annotation, e.g, what
            goes in the `[]`.
        import_ : str
            The import string for the annotation modified to include any new imports
            necessary for ndarray.
    )
    """
    # When obj has tag, the dtype and ndim are in the "extras" entry
    extras = obj.extras

    dtype = extras.get("datatype", None)
    # datatype may not be specified, in which case we don't need to import numpy
    if dtype is not None:
        dtype = f"np.{dtype}"  # Turn schema info into python code snippet involving numpy
        import_ += ", np"

    return f"{dtype}, {extras.get('ndim', None)}", extras.get("default_shape", None), import_


def _unit_factory(obj: RadSchemaObject, import_: str) -> tuple[str, str]:
    """
    Factory to get the type and import for an astropy unit

    Parameters
    ----------
    obj :
        The parsed schema object
    import_ : str
        The current import string

    Returns
    -------
    (
        unit : str
            The argument to the `rad.pydantic.adaptors.AstropyUnit` annotation, e.g, what
            goes in the `[]`.
        import_ : str
            The import string for the annotation modified to include any new imports
            necessary for the unit.
    )
    """
    # it is possible for there to be no additional unit specification
    # it is also assumed that unit specification will be an enumerated list of
    # valid astropy unit string(s)
    if obj is not None and obj.enum is not None:
        import_ += ", Unit"

        # Transform the enum units into a python code snippet
        units = [f'Unit("{u}")' for u in obj.enum]

        # Reduce the units to a single unit if possible
        if len(units) == 1:
            obj = units[0]
        else:
            obj = f"({', '.join(units)})"
    else:
        obj = None

    return obj, import_


def _quantity_factory(obj: RadSchemaObject, import_: str) -> tuple[str, str]:
    """
    Factory to get the type and import for an astropy quantity

    Parameters
    ----------
    obj :
        The parsed schema object
    import_ : str
        The current import string

    Returns
    -------
    (
        unit : str
            The argument to the `rad.pydantic.adaptors.AstropyQuantity` annotation, e.g, what
            goes in the `[]`.
        import_ : str
            The import string for the annotation modified to include any new imports
            necessary for the quantity.
    )
    """
    default_shape = None

    # Scalar quantities are represented using only "datatype" and "unit", with no "value" key.
    # Non-scalar quantities are represented using "value" and "unit", with no "datatype" key.
    #   the "value" key is an ndarray representation
    if "datatype" in obj:
        import_ += ", np"

        # Scalar quantities have datatype defined as an enum and ndim = 0
        value = f"np.{obj['datatype'].enum[0]}, 0"  # scalar ndim = 0
    else:
        # Treat the value as an ndarray
        value = obj.get("value", "None, None")
        if value is not None:
            value, default_shape, import_ = _ndarray_factory(value, import_)

    unit = obj.get("unit", None)
    unit, import_ = _unit_factory(unit, import_)

    value = f"{value}, {unit}"
    if default_shape is not None:
        value = f"{value}, {tuple(default_shape)}"

    return value, import_
