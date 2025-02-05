from __future__ import annotations

import threading
from collections import ChainMap
from itertools import chain
from textwrap import indent
from typing import Any

from ..core import NodeKeyMixin, get_config, lazyproperty

__all__ = ["SCHEMA_REGISTRY", "RadSchema"]


class _SchemaRegistry:
    """
    Registry for schema objects
    """

    def __init__(self) -> None:
        self._schemas: dict[str, RadSchema] = {}
        self._lock = threading.RLock()

    def _add_schema(self, uri: str) -> None:
        """
        Add schema to the registry
        """
        if uri in self._schemas:
            raise ValueError(f"Schema {uri} already exists")

        self._schemas[uri] = RadSchema.from_uri(uri)

    def get_schema(self, uri: str) -> RadSchema:
        """
        Get schema for schema marked node
        """
        with self._lock:
            if uri not in self._schemas:
                self._add_schema(uri)

            return self._schemas[uri]


SCHEMA_REGISTRY = _SchemaRegistry()


class RadSchema(NodeKeyMixin):
    def __init__(self, schema: dict[str, Any]) -> None:
        self._schema = schema

    @classmethod
    def get_schema(cls, uri: str) -> dict[str, Any]:
        return get_config().get_schema(uri)

    @classmethod
    def from_uri(cls, uri: str) -> RadSchema:
        return cls(get_config().get_schema(uri))

    @lazyproperty
    def schema(self) -> dict[str, Any]:
        """Access schema, so its read-only"""
        return self._schema

    @lazyproperty
    def title(self) -> str:
        """Title of the schema"""
        if isinstance(self.schema, dict):
            title: str = self.schema.get("title", "")
            return title

        # Fall back if schema is not a dict
        return ""  # type: ignore[unreachable]

    @lazyproperty
    def description(self) -> str:
        """Description of the schema"""
        if isinstance(self.schema, dict):
            description: str = self.schema.get("description", "")
            return description

        # Fall back if schema is not a dict
        return ""  # type: ignore[unreachable]

    @lazyproperty
    def docstring(self) -> str:
        """Generate a docstring from the schema"""
        docstring = f"{self.title}"
        if self.description:
            docstring += f"\n\n{indent(self.description, '    ')}"

        return docstring

    def __repr__(self) -> str:
        return repr(self.schema)

    def _get_key(self, key: str, schema: dict[str, Any]) -> list[dict[str, Any]]:
        """
        Get the sub-schema for the field
            -> Recursive search the schema for the field

        Parameters
        ----------
        key : str
            Either "required" or "properties" to get the keys for.
        schema : dict
            The schema to get the field sub-schema from from.
            -> public form of this method will pass self.schema in to initiate
               the recursive search

        Returns
        -------
        list[dict]
            List of raw sub-schemas
        """

        # Grab the field if it exists immediately
        if key in schema:
            return [schema[key]]

        # Handle the case where the schema has a type listing
        #
        if "type" in schema:
            match schema["type"]:
                # The schema is an object, so we need to search through the properties
                # There are two possibilities we support currently:
                #   - "properties" listing of fields
                #   - "patternProperties" listing of fields
                case "object":
                    if key in schema:
                        return [schema[key]]

                    if "patternProperties" in schema:
                        pattern_schema = schema["patternProperties"]

                        required = []
                        for sub_schema in pattern_schema.values():
                            required.extend(self._get_key(key, sub_schema))

                        return required

                # The object is an array so now we need to look at the items
                # schema.
                case "array":
                    if "items" in schema:
                        return self._get_key(key, schema["items"])

        # If this is using an "allOf" combiner, then we need to search through that
        # list of schemas
        if "allOf" in schema:
            required = []
            for sub_schema in schema["allOf"]:
                required.extend(self._get_key(key, sub_schema))

            return required

        # If this has a $ref, then we need to search through that schema next
        if "$ref" in schema:
            return self._get_key(key, self.get_schema(schema["$ref"]))

        # Fall back and raise an error if we can't find the field
        return []

    def get_key(self, key: str) -> list[dict[str, Any]]:
        """
        Get the sub-schema for the field
            -> Public method to initiate the recursive search

            Note the result of this will need to be post-processed
            to be useful either by chain or ChainMap

        Parameters
        ----------
        key : str
            Either "required" or "properties" to get the keys for.

        Returns
        -------
        list[dict]
            List of raw sub-schemas
        """
        return self._get_key(key, self.schema)

    @lazyproperty
    def required(self) -> set[str]:
        return set(self._to_field_key(key) for key in list(chain(*self.get_key("required"))))

    @lazyproperty
    def property_order(self) -> tuple[str, ...]:
        return tuple(self._to_field_key(key) for key in list(chain(*self.get_key("propertyOrder"))))

    @lazyproperty
    def fields(self) -> dict[str, RadSchema]:
        return {self._to_field_key(key): RadSchema(value) for key, value in ChainMap(*self.get_key("properties")).items()}

    @lazyproperty
    def archive_catalog(self) -> dict[str, RadSchema]:
        """Pull the archive_catalog data from the schema"""
        archive_catalog = {}
        for field, schema in self.fields.items():
            sub_schema = dict(ChainMap(*schema.get_key("archive_catalog")))
            if sub_schema:
                archive_catalog[field] = RadSchema(sub_schema)

        return archive_catalog

    @lazyproperty
    def sdf(self) -> dict[str, RadSchema]:
        """Pull the sdf data schema from the schema"""
        sdf = {}
        for field, schema in self.fields.items():
            sub_schema = dict(ChainMap(*schema.get_key("sdf")))
            if sub_schema:
                sdf[field] = RadSchema(sub_schema)

        return sdf
