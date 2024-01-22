"""
Base classes for all the tagged objects defined by RAD.
    Each tagged object will be dynamically created at runtime by _stnode.py
    from RAD's manifest.
"""
import copy

import asdf

from roman_datamodels._asdf.manifest import MANIFESTS

from ._node import DNode, LNode

__all__ = [
    "TaggedObjectNode",
    "TaggedListNode",
    "TaggedScalarNode",
]


def _lookup_latest_tag(pattern):
    for manifest in MANIFESTS:
        for tag_def in manifest["tags"]:
            tag_uri = tag_def["tag_uri"]
            if asdf.util.uri_match(pattern, tag_uri):
                return tag_uri
    raise Exception("pattern no matchy")


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
        if not hasattr(self, "_tag"):
            self._tag = _lookup_latest_tag(self._tag_pattern)
        return self._tag

    def __asdf_traverse__(self):
        self.tag  # trigger tag lookup to generate a _tag attr
        return super().__asdf_traverse__()

    def _schema(self):
        if self._x_schema is None:
            schema_uri = self.ctx.extension_manager.get_tag_definition(self.tag).schema_uris[0]
            self._x_schema = asdf.schema.load_schema(schema_uri, resolve_references=True)
        return self._x_schema


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
        if not hasattr(self, "_tag"):
            self._tag = _lookup_latest_tag(self._tag_pattern)
        return self._tag

    def __asdf_traverse__(self):
        self.tag  # trigger tag lookup to generate a _tag attr
        return super().__asdf_traverse__()


class TaggedScalarNode:
    """
    Base class for all tagged scalars defined by RAD
        There will be one of these for any tagged object defined by RAD, which has
        a scalar base type, or wraps a scalar base type.
        These will all be in the tagged_scalars directory.
    """

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
        self.tag  # trigger tag lookup to generate a _tag attr
        return self

    @property
    def tag(self):
        if not hasattr(self, "_tag"):
            self._tag = _lookup_latest_tag(self._tag_pattern)
        return self._tag

    def copy(self):
        return copy.copy(self)
