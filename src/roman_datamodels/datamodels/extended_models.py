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

from typing import ClassVar

from .datamodel import RomanDataModel

__all__ = ["RomanExtendedDataModel"]


class RomanExtendedDataModel(RomanDataModel):
    """
    Base class for all data models which need extended functionality.
        This is intended to act as a base class only.
    """

    @classmethod
    def model_from_schema_uri(cls, schema_uri: str) -> type[RomanDataModel]:
        """Grab a subclass of this model corresponding to the schema_uri."""

        for subclass in cls.__subclasses__():
            if subclass._schema_uri == schema_uri:
                return subclass

        return RomanDataModel


class _WfiMode(RomanExtendedDataModel):
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


class _RampModel(RomanExtendedDataModel):
    _schema_uri: ClassVar[str] = "asdf://stsci.edu/datamodels/roman/schemas/data_products/ramp-1.0.0"

    @classmethod
    def from_science_raw(cls, model) -> _RampModel:
        """
        Construct a RampModel from a ScienceRawModel

        Parameters
        ----------
        model : ScienceRawModel or RampModel
            The input science raw model (a RampModel will also work)
        """
        raise NotImplementedError("This method is not implemented yet, but will be.")


class _AssociationsModel(RomanExtendedDataModel):
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


class _LinearityRefModel(RomanExtendedDataModel):
    _schema_uri: ClassVar[str] = "asdf://stsci.edu/datamodels/roman/schemas/reference_files/linearity-1.0.0"

    def get_primary_array_name(self):
        """
        Returns the name "primary" array for this model, which is "coeffs".
        """
        return "coeffs"


class _InverselinearityRefModel(RomanExtendedDataModel):
    _schema_uri: ClassVar[str] = "asdf://stsci.edu/datamodels/roman/schemas/reference_files/inverselinearity-1.0.0"

    def get_primary_array_name(self):
        """
        Returns the name "primary" array for this model, which is "coeffs".
        """
        return "coeffs"


class _MaskRefModel(RomanExtendedDataModel):
    _schema_uri: ClassVar[str] = "asdf://stsci.edu/datamodels/roman/schemas/reference_files/mask-1.0.0"

    def get_primary_array_name(self):
        """
        Returns the name "primary" array for this model, which is "dq".
        """
        return "dq"
