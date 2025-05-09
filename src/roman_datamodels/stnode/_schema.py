"""
Code for relating nodes and schema.
"""

import functools

import asdf

from ._node import DNode, LNode
from ._registry import (
    NODE_CLASSES_BY_TAG,
    SCHEMA_URIS_BY_TAG,
)

__all__ = []


@functools.cache
def _get_schema_from_tag(tag):
    """
    Look up and load ASDF's schema corresponding to the tag_uri.

    Parameters
    ----------
    tag : str
        The tag_uri of the schema to load.
    """
    schema_uri = SCHEMA_URIS_BY_TAG[tag]

    return asdf.schema.load_schema(schema_uri, resolve_references=True)


def _get_properties(schema):
    if "allOf" in schema:
        for subschema in schema["allOf"]:
            yield from _get_properties(subschema)
    elif "anyOf" in schema:
        yield from _get_properties(schema["anyOf"][0])
    elif "properties" in schema:
        yield from schema["properties"].items()


def _has_properties(schema):
    try:
        next(_get_properties(schema))
    except StopIteration:
        return False
    return True


def _is_object(schema):
    # TODO handle just "type: object"
    return _has_properties(schema)


def _is_array(schema):
    # TODO handle recursion
    return schema.get("type") == "array"


def _node_from_schema(node_class, schema=None):
    if schema is None:
        schema = _get_schema_from_tag(node_class._default_tag)
    node = node_class()
    if isinstance(node, DNode):
        # properties, recursively
        # properties = {}
        # if "properties" in schema:
        #    properties.update(schema["properties"])
        # elif "allOf" in schema:
        #    for subschema in schema["allOf"]:
        #        if "properties" in subschema:
        #            properties.update(subschema["properties"])
        # else:
        #    properties = {}
        for name, subschema in _get_properties(schema):
            # TODO handle recursion for tag
            if tag := subschema.get("tag"):
                if property_class := NODE_CLASSES_BY_TAG.get(tag):
                    if hasattr(property_class, "from_schema"):
                        node[name] = property_class.from_schema()
                else:
                    if "roman" in tag:
                        # TODO for "fake" make these
                        pass
            else:
                if _is_object(subschema):
                    # TODO maybe DNode and LNode should have a from_schema?
                    node[name] = _node_from_schema(DNode, subschema)
                elif _is_array(subschema):
                    node[name] = _node_from_schema(LNode, subschema)
                else:
                    # TODO reference frame is a single item enum, make this
                    pass
                ## determine if this is a sub node
                # if "properties" in subschema:
                #    property_class = DNode
                # elif "allOf" in subschema and any("properties" in s for s in subschema["allOf"]):
                #    property_class = DNode
                # else:  # TODO list?
                #    property_class = None
                # if property_class:
                #    node[name] = _node_from_schema(property_class, subschema)
    elif isinstance(node, LNode):
        pass  # TODO list?
    return node
