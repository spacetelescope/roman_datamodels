from __future__ import annotations

from functools import cache
from re import match
from typing import Any

from asdf import get_config, schema
from semantic_version import Version

from ._registry import REGISTRY, ManifestTagEntry

__all__ = ["class_name_from_tag_uri", "docstring_from_tag", "get_latest_schema", "get_schema_from_tag"]


def _name_from_tag_uri(tag_uri: str) -> str:
    """
    Compute the name of the schema from the tag_uri.

    Parameters
    ----------
    tag_uri : str
        The tag_uri to find the name from
    """
    tag_uri_split = tag_uri.split("/")[-1].split("-")[0]
    if "/tvac/" in tag_uri and "tvac" not in tag_uri_split:
        tag_uri_split = "tvac_" + tag_uri.split("/")[-1].split("-")[0]
    elif "/fps/" in tag_uri and "fps" not in tag_uri_split:
        tag_uri_split = "fps_" + tag_uri.split("/")[-1].split("-")[0]
    return tag_uri_split


def class_name_from_tag_uri(tag_uri: str) -> str:
    """
    Construct the class name for the STNode class from the tag_uri

    Parameters
    ----------
    tag_uri : str
        The tag_uri found in the RAD manifest

    Returns
    -------
    value : str
        string name for the class
    """
    tag_name = _name_from_tag_uri(tag_uri)
    class_name = "".join([p.capitalize() for p in tag_name.split("_")])
    if tag_uri.startswith("asdf://stsci.edu/datamodels/roman/tags/reference_files/"):
        class_name += "Ref"

    return class_name


def docstring_from_tag(entry: ManifestTagEntry) -> str:
    """
    Read the docstring (if it exists) from the RAD manifest and generate a docstring
        for the dynamically generated class.

    Parameters
    ----------
    tag_def: dict
        A tag entry from the RAD manifest

    Returns
    -------
    value : str
        A docstring for the class based on the tag
    """
    docstring = f"{entry['description']}\n\n" if "description" in entry else ""

    return docstring + f"Class generated from tag '{entry['tag_uri']}'"


@cache
def get_latest_schema(uri: str) -> tuple[str, dict[str, Any]]:
    """
    Get the latest version of a schema by URI (or partial URI).
    """

    if "-" in uri:
        uri_prefix, version = uri.rsplit("-", 1)
        latest_uri = uri
    else:
        uri_prefix = uri
        version = "0.0.0"
        latest_uri = None

    uri_prefix += "-"
    current_version = Version(version)
    for schema_uri in get_config().resource_manager:
        if schema_uri.startswith(uri_prefix) and (new_version := Version(schema_uri.rsplit("-", 1)[-1])) > current_version:
            current_version = new_version
            latest_uri = schema_uri

    if latest_uri is None:
        raise ValueError(f"No schema found for {uri}")

    return latest_uri, schema.load_schema(latest_uri, resolve_references=True)


@cache
def get_schema_from_tag(tag):
    """
    Look up and load ASDF's schema corresponding to the tag_uri.

    Parameters
    ----------
    tag : str
        The tag_uri of the schema to load.
    """
    return schema.load_schema(REGISTRY.tag.schema[tag], resolve_references=True)


class _MissingKeywordType:
    """Special value to indicate a keyword was not found in a schema"""

    def __bool__(self):
        return False


MISSING_KEYWORD = _MissingKeywordType()


def get_keyword(schema, key):
    """
    Search a schema for value for a given a keyword.

    Parameters
    ----------
    schema : dict
        The schema (with all references resolved) to search.

    key : str
        The keyword to use for the search.

    Returns
    -------
    value : Any or _MISSING_KEYWORD
        The value for the keyword or _MISSING_KEYWORD if not found.
    """
    if key in schema:
        return schema[key]
    for combiner in ("allOf", "anyOf"):
        if combiner not in schema:
            continue
        for subschema in schema[combiner]:
            value = get_keyword(subschema, key)
            if value is not MISSING_KEYWORD:
                return value
    return MISSING_KEYWORD


def has_keyword(schema, key):
    """
    Check if a schema has a given keyword.

    Parameters
    ----------
    schema : dict
        Schema to check.

    key : str
        Keyword to check for.

    Returns
    -------
    bool
        If the keyword was found
    """
    return get_keyword(schema, key) != MISSING_KEYWORD


def get_properties(schema):
    """
    Generator that produces property definitions.

    Parameters
    ----------
    schema : dict
        Schema to parse.

    Yields
    ------
    (str, any)
        Property name and subschema.
    """
    if "allOf" in schema:
        for subschema in schema["allOf"]:
            yield from get_properties(subschema)
    elif "anyOf" in schema:
        yield from get_properties(schema["anyOf"][0])
    elif "properties" in schema:
        yield from schema["properties"].items()


def get_pattern_properties(schema, name):
    """
    Get a patternProperties subschema for name.

    Parameters
    ----------
    schema : dict
       Schema to search.

    name : str
       Property name to check the pattern against.

    Yields
    ------
    dict
        Subschema matching the property (empty if None).
    """
    if patterns := schema.get("patternProperties"):
        for pattern, subschema in patterns.items():
            if match(pattern, name):
                yield subschema
    if "allOf" in schema:
        for subschema in schema["allOf"]:
            yield from get_pattern_properties(subschema, name)
    elif "anyOf" in schema:
        yield from get_properties(schema["anyOf"][0])


def get_required(schema):
    """
    Search a schema for required property names.

    Parameters
    ----------
    schema : dict
        Schema to parse.

    Returns
    -------
    set of str
        Set of required property names.
    """
    required = set()
    if "required" in schema:
        required.update(set(schema["required"]))
    if "allOf" in schema:
        for subschema in schema["allOf"]:
            required.update(get_required(subschema))
    if "anyOf" in schema:
        required.update(get_required(schema["anyOf"][0]))
    return required


class _NoValueType:
    """Special value to indicate a builder built nothing"""

    def __bool__(self):
        return False


NO_VALUE = _NoValueType()
