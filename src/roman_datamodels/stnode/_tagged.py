"""
Base classes for all the tagged objects defined by RAD.
    Each tagged object will be dynamically created at runtime by _stnode.py
    from RAD's manifest.
"""

import copy

import asdf

from ._node import DNode, LNode
from ._registry import (
    LIST_NODE_CLASSES_BY_TAG,
    OBJECT_NODE_CLASSES_BY_TAG,
    SCALAR_NODE_CLASSES_BY_KEY,
    SCALAR_NODE_CLASSES_BY_TAG,
)

__all__ = [
    "TaggedObjectNode",
    "TaggedListNode",
    "TaggedScalarNode",
]


def get_schema_from_tag(ctx, tag):
    """
    Look up and load ASDF's schema corresponding to the tag_uri.

    Parameters
    ----------
    ctx :
        An ASDF file context.
    tag : str
        The tag_uri of the schema to load.
    """
    schema_uri = ctx.extension_manager.get_tag_definition(tag).schema_uris[0]

    return asdf.schema.load_schema(schema_uri, resolve_references=True)


def name_from_tag_uri(tag_uri):
    """
    Compute the name of the schema from the tag_uri.

    Parameters
    ----------
    tag_uri : str
        The tag_uri to find the name from
    """
    return tag_uri.split("/")[-1].split("-")[0]


class TaggedObjectNode(DNode):
    """
    Base class for all tagged objects defined by RAD
        There will be one of these for any tagged object defined by RAD, which has
        base type: object.
    """

    def __init_subclass__(cls, **kwargs) -> None:
        """
        Register any subclasses of this class in the OBJECT_NODE_CLASSES_BY_TAG
        registry.
        """
        super().__init_subclass__(**kwargs)
        if cls.__name__ != "TaggedObjectNode":
            if cls._tag in OBJECT_NODE_CLASSES_BY_TAG:
                raise RuntimeError(f"TaggedObjectNode class for tag '{cls._tag}' has been defined twice")
            OBJECT_NODE_CLASSES_BY_TAG[cls._tag] = cls

    @property
    def tag(self):
        return self._tag

    def _schema(self):
        if self._x_schema is None:
            self._x_schema = self.get_schema()
        return self._x_schema

    def get_schema(self):
        """Retrieve the schema associated with this tag"""
        return get_schema_from_tag(self.ctx, self._tag)


class TaggedListNode(LNode):
    """
    Base class for all tagged list defined by RAD
        There will be one of these for any tagged object defined by RAD, which has
        base type: array.
    """

    def __init_subclass__(cls, **kwargs) -> None:
        """
        Register any subclasses of this class in the LIST_NODE_CLASSES_BY_TAG
        registry.
        """
        super().__init_subclass__(**kwargs)
        if cls.__name__ != "TaggedListNode":
            if cls._tag in LIST_NODE_CLASSES_BY_TAG:
                raise RuntimeError(f"TaggedListNode class for tag '{cls._tag}' has been defined twice")
            LIST_NODE_CLASSES_BY_TAG[cls._tag] = cls

    @property
    def tag(self):
        return self._tag


class TaggedScalarNode:
    """
    Base class for all tagged scalars defined by RAD
        There will be one of these for any tagged object defined by RAD, which has
        a scalar base type, or wraps a scalar base type.
        These will all be in the tagged_scalars directory.
    """

    _tag = None
    _ctx = None

    def __init_subclass__(cls, **kwargs) -> None:
        """
        Register any subclasses of this class in the SCALAR_NODE_CLASSES_BY_TAG
        and SCALAR_NODE_CLASSES_BY_KEY registry.
        """
        super().__init_subclass__(**kwargs)
        if cls.__name__ != "TaggedScalarNode":
            if cls._tag in SCALAR_NODE_CLASSES_BY_TAG:
                raise RuntimeError(f"TaggedScalarNode class for tag '{cls._tag}' has been defined twice")
            SCALAR_NODE_CLASSES_BY_TAG[cls._tag] = cls
            SCALAR_NODE_CLASSES_BY_KEY[name_from_tag_uri(cls._tag)] = cls

    @property
    def ctx(self):
        if self._ctx is None:
            TaggedScalarNode._ctx = asdf.AsdfFile()
        return self._ctx

    def __asdf_traverse__(self):
        return self

    @property
    def tag(self):
        return self._tag

    @property
    def key(self):
        return name_from_tag_uri(self._tag)

    def get_schema(self):
        return get_schema_from_tag(self.ctx, self._tag)

    def copy(self):
        return copy.copy(self)
