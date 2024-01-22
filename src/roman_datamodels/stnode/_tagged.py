"""
Base classes for all the tagged objects defined by RAD.
    Each tagged object will be dynamically created at runtime by _stnode.py
    from RAD's manifest.
"""
import copy

import asdf

from ._node import DNode, LNode

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


class TaggedObjectNode(DNode):
    """
    Base class for all tagged objects defined by RAD
        There will be one of these for any tagged object defined by RAD, which has
        base type: object.
    """

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        if cls.__name__ != "TaggedObjectNode":
            cls.__module__ = "roman_datamodels.stnode"

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
        super().__init_subclass__(**kwargs)
        if cls.__name__ != "TaggedListNode":
            cls.__module__ = "roman_datamodels.stnode"

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
        super().__init_subclass__(**kwargs)
        if cls.__name__ != "TaggedScalarNode":
            cls.__module__ = "roman_datamodels.stnode"

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

    def get_schema(self):
        return get_schema_from_tag(self.ctx, self._tag)

    def copy(self):
        return copy.copy(self)
