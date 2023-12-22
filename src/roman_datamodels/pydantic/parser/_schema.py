from __future__ import annotations

from functools import lru_cache
from typing import Any, NamedTuple

import yaml
from asdf.config import get_config
from datamodel_code_generator.parser.jsonschema import JsonSchemaObject

__all__ = ["RadSchemaObject"]


class ManifestMaps(NamedTuple):
    tag_to_uri: dict[str, str]
    uri_to_tag: dict[str, str]


# Modify this to eventually deal with multiple manifests
@lru_cache
def get_manifest_maps() -> ManifestMaps:
    manager = get_config().resource_manager

    for resource in manager._resource_mappings:
        if resource.package_name == "rad" and resource.delegate.uri_prefix.endswith("manifests"):
            resource_map = resource.delegate

            uri = f"{resource_map.uri_prefix}/datamodels-1.0"

            tag_to_uri_map = {tag["tag_uri"]: tag["schema_uri"] for tag in yaml.safe_load(resource_map[uri])["tags"]}
            uri_to_tag_map = {}
            for tag_uri, schema_uri in tag_to_uri_map.items():
                if schema_uri in uri_to_tag_map:
                    raise ValueError(f"Duplicate schema_uri: {schema_uri}")

                uri_to_tag_map[schema_uri] = tag_uri

            return ManifestMaps(tag_to_uri_map, uri_to_tag_map)


class RadSchemaObject(JsonSchemaObject):
    """Modifications to the JsonSchemaObject to support reading Rad schemas"""

    items: list[RadSchemaObject] | RadSchemaObject | bool | None = None
    additionalProperties: RadSchemaObject | bool | None = None
    patternProperties: dict[str, RadSchemaObject] | None = None
    oneOf: list[RadSchemaObject] = []
    anyOf: list[RadSchemaObject] = []
    allOf: list[RadSchemaObject] = []
    properties: dict[str, RadSchemaObject | bool] | None = None
    id: str | None = None
    tag: str | None = None
    astropy_type: str | None = None
    tag_uri: str | None = None

    def model_post_init(self, __context: Any) -> None:
        """Custom post processing for RadSchemaObject"""

        manifest_maps = get_manifest_maps()

        # Turn tags into references
        if self.tag is not None:
            if self.tag in manifest_maps.tag_to_uri:
                if self.ref is not None:
                    raise ValueError("Cannot set both tag and ref")

                self.ref = manifest_maps.tag_to_uri[self.tag]

        # Handle external reference (this is a bit of a hack)
        if self.astropy_type is not None:
            self.custom_type_path = self.astropy_type
            self.allOf = []

        # Set the tag_uri if it has one
        if self.id is not None:
            if self.id in manifest_maps.uri_to_tag:
                self.tag_uri = manifest_maps.uri_to_tag[self.id]


RadSchemaObject.model_rebuild()
