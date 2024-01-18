"""
Define a Pydantic adaptor for a GWCS WCS.
"""
from __future__ import annotations

__all__ = ["GwcsWcs"]

from typing import TYPE_CHECKING, Annotated, Any, ClassVar

import astropy.units as u
from astropy import coordinates
from astropy.modeling import models
from gwcs import coordinate_frames
from gwcs.wcs import WCS
from pydantic import GetCoreSchemaHandler, GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema

from ._base import Adaptor, AdaptorGen

if TYPE_CHECKING:
    from roman_datamodels.generator._schema import RadSchemaObject


class GwcsWcs(Adaptor):
    """
    The pydantic adaptor for a GWCS WCS.

    This does not allow any constraints on the WCS, it basically does an isinstance check.
    """

    _tags: ClassVar[tuple[str]] = ("tag:stsci.edu:gwcs/wcs-*",)

    @classmethod
    def factory(cls, **kwargs) -> type:
        """
        Generate a new GwcsWcs type constrained to the values given.

        Parameters
        ----------
        kwargs
            The values to constrain the type to.

        Returns
        -------
        The new type.
        """

        return cls

    @classmethod
    def __class_getitem__(cls, factory: None) -> type:
        """Make this consistent with the other adaptors."""

        return Annotated[WCS, cls.factory()]

    @classmethod
    def make_default(cls, **kwargs) -> WCS:
        """
        Create a default instance of a WCS
            Taken from the example in the GWCS documentation

        Returns
        -------
        The a WCS with no arguments
        """

        pixelshift = models.Shift(-500) & models.Shift(-500)
        pixelscale = models.Scale(0.1 / 3600.0) & models.Scale(0.1 / 3600.0)  # 0.1 arcsec/pixel
        tangent_projection = models.Pix2Sky_TAN()
        celestial_rotation = models.RotateNative2Celestial(30.0, 45.0, 180.0)

        det2sky = pixelshift | pixelscale | tangent_projection | celestial_rotation

        detector_frame = coordinate_frames.Frame2D(name="detector", axes_names=("x", "y"), unit=(u.pix, u.pix))
        sky_frame = coordinate_frames.CelestialFrame(reference_frame=coordinates.ICRS(), name="icrs", unit=(u.deg, u.deg))
        return WCS(
            [
                (detector_frame, det2sky),
                (sky_frame, None),
            ]
        )

    @classmethod
    def code_generator(cls, obj: RadSchemaObject) -> AdaptorGen:
        """Create a representation of this adaptor for the schema generator."""
        name = cls.__name__

        # This is the code for the adaptor
        #    GwcsWcs[None]
        return AdaptorGen(type_=f"{name}[None]", import_=name)

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _source_type: Any,
        _handler: GetCoreSchemaHandler,
    ) -> core_schema.CoreSchema:
        """
        Specify the pydantic_core schema for a GWCS WCS.
            This is what is used to validate a model field against its annotation.
        """

        return core_schema.json_or_python_schema(
            json_schema=core_schema.any_schema(),
            python_schema=core_schema.is_instance_schema(WCS),
            serialization=core_schema.plain_serializer_function_ser_schema(lambda value: value),
        )

    @classmethod
    def __get_pydantic_json_schema__(
        cls,
        _core_schema: core_schema.CoreSchema,
        handler: GetJsonSchemaHandler,
    ) -> JsonSchemaValue:
        """
        This enables Pydantic to generate a JsonSchema for the annotation
            This is to allow us to create single monolithic JsonSchemas for each
            data product if we wish.
        """
        return {
            "title": None,
            "tag": GwcsWcs._tags[0],
        }
