"""
Utilities used by the code generator
"""
from __future__ import annotations

__all__ = [
    "remove_uri_version",
    "class_name_from_uri",
    "get_manifest_maps",
    "get_rad_schema_path",
    "class_name_from_module",
]

from functools import lru_cache
from pathlib import Path
from typing import TYPE_CHECKING, NamedTuple

import yaml
from asdf.config import get_config

from roman_datamodels.core._utils import remove_uri_version

if TYPE_CHECKING:
    from rad.integration import RadResourceMapping


def _base_class_name(name: str) -> str:
    """
    Turn the name into a CamelCase class name (removes "/" if necessary)

    Parameters
    ----------
    name: str
        The base name to turn into a class name

    Returns
    -------
    A CamelCase class name
    """
    return "".join([p.capitalize() for p in name.split("/")[-1].split("_")])


def _class_name_suffix(base_name: str) -> str:
    # Mark reference file models as RefModel (keeps things in line with legacy Roman code)
    if "reference_files" in base_name:
        return "RefModel"

    # Mark data product models as Model (keeps things in line with legacy Roman code)
    if "data_products" in base_name:
        return "Model"

    return ""


def class_name_from_uri(uri: str) -> str:
    """
    Turn the uri/id into a valid python class name

    Parameters
    ----------
    uri: str
        The uri/id of the schema

    Returns
    -------
    The class name for the schema
    """
    uri = remove_uri_version(uri)

    return _base_class_name(uri) + _class_name_suffix(uri)


def class_name_from_module(package: str, module: str) -> str:
    """
    Turn the module and name into a valid python class name

    Parameters
    ----------
    package: str
        The name of the package containing the module
    module: str
        The name of the module containing the datamodel

    Returns
    -------
    The class name for the schema
    """
    return _base_class_name(module) + _class_name_suffix(package)


def get_rad_resource_map(suffix: str) -> RadResourceMapping:
    """
    Get the resource mapping for RAD corresponding to the given suffix

    Parameters
    ----------
    suffix: str
        Determines the type of resources in the resource mapping. This should be
            - "manifests" for the schema manifests
            - "schemas" for the latest version of the schemas
            - "schemas-<version>" for the schemas with <version> being a fixed version.

    Returns
    -------
    RadResourceMapping registered for RAD under the asdf.resource entry point
    """
    manager = get_config().resource_manager

    # We have to access the private mappings because the public interface doesn't
    # expose the resources via their registered name.
    for resource in manager._resource_mappings:
        # RAD is registered under the "rad" name in the entry points for its ASDF
        #   resources.
        if resource.package_name == "rad":
            # RAD defines a special resource mapping for its schemas and manifests,
            #    so that we can access additional information about the schemas via
            #    a public interface.
            resource_map: RadResourceMapping = resource.delegate

            # There will be two resources, one for the schemas and one for the manifests.
            #   We want the one for the manifests.
            if resource_map.uri_prefix.endswith(suffix):
                return resource_map


class ManifestMaps(NamedTuple):
    tag_to_uri: dict[str, str]
    uri_to_tag: dict[str, str]


@lru_cache
def get_manifest_maps(version: str | None = None) -> ManifestMaps:
    """
    Get the tag to uri and uri to tag mappings from the RAD schema manifest

    Parameters
    ----------
    version: str, optional
        The version string for the schemas we are interested. If not provided it
        will be assumed to be "1.0"

    Returns
    -------
    ManifestMaps
        A tuple containing the tag to uri and uri to tag mappings
            tag_to_uri: dict[str, str]
                key: tag_uri
                value: schema_uri
            uri_to_tag: dict[str, str]
                key: schema_uri
                value: tag_uri
    """
    version = version or "1.0"

    resource_map = get_rad_resource_map("manifests")
    uri = f"{resource_map.uri_prefix}/datamodels-{version}"

    tag_to_uri_map = {}
    uri_to_tag_map = {}
    # Read the manifest and build the maps
    for tag in yaml.safe_load(resource_map[uri])["tags"]:
        tag_to_uri_map[tag["tag_uri"]] = tag["schema_uri"]

        # Multiple tags can point to the same schema, but for RAD
        #   we are assuming that the schema_uri is unique for each
        #   tag.
        if tag["schema_uri"] in uri_to_tag_map:
            raise ValueError(f"Duplicate schema_uri: {tag['schema_uri']}")
        uri_to_tag_map[tag["schema_uri"]] = tag["tag_uri"]

    return ManifestMaps(tag_to_uri_map, uri_to_tag_map)


def get_rad_schema_path(version: str | None = None) -> Path:
    """
    Get the path to the RAD schema for the given suffix

    Parameters
    ----------
    version: str, optional
        The version string for the schemas we are interested. If not provided it
        is assumed to be the latest version

    Returns
    -------
    Path
        The path to the RAD schema
    """
    suffix = "schemas"
    if version is not None:
        suffix += f"-{version}"

    resource_map = get_rad_resource_map(suffix)
    return resource_map.root
