"""
This module contains base models for all data models which need extended functionality.

    To extend an automatically generated model, it needs to be tagged, and a subclass of
    `ExtendedDataModel` needs to be created with _schema_uri set to the schema URI of the
    underlying model.

We will enforce the convention that the name of the extended model is the name of the underlying model
prefixed with an underscore.  This is to avoid name collisions with the underlying model, and make
it clear that the model is an extension of the underlying model.
"""
from __future__ import annotations

__all__ = ["ExtendedDataModel"]

from typing import Annotated, Any, ClassVar

import astropy.units as u
from pydantic import Field, field_validator

from ._model import DataModel


class ExtendedDataModel(DataModel):
    """
    Base class for all data models which need extended functionality.
        This is intended to act as a base class only.
    """

    @classmethod
    def model_from_schema_uri(cls, schema_uri: str) -> type[DataModel]:
        """Grab a subclass of this model corresponding to the schema_uri."""

        for subclass in cls.__subclasses__():
            if subclass._schema_uri == schema_uri:
                return subclass

        return DataModel


class _WfiMode(ExtendedDataModel):
    _schema_uri: ClassVar[str] = "asdf://stsci.edu/datamodels/roman/schemas/wfi_mode-1.0.0"

    _grating_optical_elements: ClassVar[frozenset[str]] = frozenset({"GRISM", "PRISM"})

    @property
    def filter(self) -> str | None:
        """The filter used for the observation."""
        return self.optical_element if self.optical_element not in self._grating_optical_elements else None

    @property
    def grating(self) -> str | None:
        """The grating used for the observation."""
        return self.optical_element if self.optical_element in self._grating_optical_elements else None


class _RampModel(ExtendedDataModel):
    _schema_uri: ClassVar[str] = "asdf://stsci.edu/datamodels/roman/schemas/data_products/ramp-1.0.0"

    # The data array which needs to be coerced to the correct dtype has to be annotated now, so that
    #    Pydantic can compute this model correctly. This will be overridden by the generated model.
    data: Annotated[Any, Field()]

    @field_validator("data", mode="before")
    @classmethod
    def _coerce_data_dtype(cls, quantity: u.Quantity):
        """
        Coerce the data array to be the correct dtype, this may force a data copy.

            This uses a Pydantic "before" field_validator, which takes in the value of the field
            in question during model instance construction BEFORE Pydantic attempts to validate
            the field. It then must return the value which will be used for the field. This enables
            use to coerce the data array to the correct dtype before Pydantic attempts to validate.
        """
        # Find the annotated dtype
        dtype = cls.model_fields["data"].metadata[0].dtype

        if isinstance(quantity, u.Quantity) and quantity.dtype != dtype:
            quantity = quantity.astype(dtype)

        return quantity

    @classmethod
    def from_science_raw(cls, model: DataModel, **kwargs) -> _RampModel:
        """
        Construct a RampModel from a ScienceRawModel

        Parameters
        ----------
        model : ScienceRawModel or RampModel
            The input science raw model (a RampModel will also work)

        **kwargs :
            Any additional keyword arguments to be passed to the RampModel default constructor.
        """
        # If one already has a RampModel, just return it back
        if isinstance(model, cls):
            return model

        # Use model_dump to generate override data from the old model, then pass to make_default
        return cls.make_default(data=model.model_dump(), **kwargs)


class _AssociationsModel(ExtendedDataModel):
    _schema_uri: ClassVar[str] = "asdf://stsci.edu/datamodels/roman/schemas/data_products/associations-1.0.0"

    @classmethod
    def is_association(cls, asn_data) -> bool:
        """
        Test if an object is an association by checking for required fields

        Parameters
        ----------
        asn_data :
            The data to be tested.
        """
        return isinstance(asn_data, dict) and "asn_id" in asn_data and "asn_pool" in asn_data


class _LinearityRefModel(ExtendedDataModel):
    _schema_uri: ClassVar[str] = "asdf://stsci.edu/datamodels/roman/schemas/reference_files/linearity-1.0.0"

    def get_primary_array_name(self):
        """
        Returns the name "primary" array for this model, which is "coeffs".
        """
        return "coeffs"


class _InverselinearityRefModel(ExtendedDataModel):
    _schema_uri: ClassVar[str] = "asdf://stsci.edu/datamodels/roman/schemas/reference_files/inverselinearity-1.0.0"

    def get_primary_array_name(self):
        """
        Returns the name "primary" array for this model, which is "coeffs".
        """
        return "coeffs"


class _MaskRefModel(ExtendedDataModel):
    _schema_uri: ClassVar[str] = "asdf://stsci.edu/datamodels/roman/schemas/reference_files/mask-1.0.0"

    def get_primary_array_name(self):
        """
        Returns the name "primary" array for this model, which is "dq".
        """
        return "dq"
