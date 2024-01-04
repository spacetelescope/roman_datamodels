"""
Defines the schema object for the RAD schema.
"""
from __future__ import annotations

from typing import Any

from datamodel_code_generator.parser.jsonschema import JsonSchemaObject

from roman_datamodels.datamodels.datamodel import TaggedDataModel

from ._utils import get_manifest_maps

__all__ = ["RadSchemaObject"]


class RadSchemaObject(JsonSchemaObject):
    """Modifications to the JsonSchemaObject to support reading Rad schemas"""

    # These all have to be redefined so that Pydantic recursively uses the RadSchemaObject
    # and not the JsonSchemaObject
    items: list[RadSchemaObject] | RadSchemaObject | bool | None = None
    additionalProperties: RadSchemaObject | bool | None = None
    patternProperties: dict[str, RadSchemaObject] | None = None
    oneOf: list[RadSchemaObject] = []
    anyOf: list[RadSchemaObject] = []
    allOf: list[RadSchemaObject] = []
    properties: dict[str, RadSchemaObject | bool] | None = None

    # Additions to support ASDF schemas
    id: str | None = None  # ASDF uses an old draft of JSON Schema, $id is now the standard
    tag: str | None = None  # recover the tag information
    tag_uri: str | None = None  # Add in the tag_uri information

    def model_post_init(self, __context: Any) -> None:
        """Custom post processing for RadSchemaObject"""

        manifest_maps = get_manifest_maps()

        # Turn tags into references
        if self.tag is not None:
            if self.tag in manifest_maps.tag_to_uri:
                if self.ref is not None:
                    raise ValueError("Cannot set both tag and ref")

                self.ref = manifest_maps.tag_to_uri[self.tag]

        # Set the tag_uri if it has one
        if self.id is not None:
            if self.id in manifest_maps.uri_to_tag:
                self.tag_uri = manifest_maps.uri_to_tag[self.id]
                self.custom_base_path = f"{TaggedDataModel.__module__}.{TaggedDataModel.__name__}"


RadSchemaObject.model_rebuild()
