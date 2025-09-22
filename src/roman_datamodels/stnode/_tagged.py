"""
Base classes for all the tagged objects defined by RAD.
    Each tagged object will be dynamically created at runtime by _stnode.py
    from RAD's manifest.
"""

from __future__ import annotations

import copy
from typing import TYPE_CHECKING

from ._node import DNode, LNode
from ._registry import (
    LIST_NODE_CLASSES_BY_PATTERN,
    OBJECT_NODE_CLASSES_BY_PATTERN,
    SCALAR_NODE_CLASSES_BY_KEY,
    SCALAR_NODE_CLASSES_BY_PATTERN,
)
from ._schema import _NO_VALUE, Builder, FakeDataBuilder, NodeBuilder, _get_schema_from_tag

if TYPE_CHECKING:
    from typing import ClassVar, TypeAlias

__all__ = [
    "TaggedListNode",
    "TaggedObjectNode",
    "TaggedScalarNode",
]


def name_from_tag_uri(tag_uri):
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


class TaggedObjectNode(DNode):
    """
    Base class for all tagged objects defined by RAD
        There will be one of these for any tagged object defined by RAD, which has
        base type: object.
    """

    __slots__ = ()

    _default_tag: ClassVar[str]

    def __init_subclass__(cls, **kwargs) -> None:
        """
        Register any subclasses of this class in the OBJECT_NODE_CLASSES_BY_PATTERN
        registry.
        """
        super().__init_subclass__(**kwargs)
        if cls.__name__ != "TaggedObjectNode":
            if cls._pattern in OBJECT_NODE_CLASSES_BY_PATTERN:
                raise RuntimeError(f"TaggedObjectNode class for tag '{cls._pattern}' has been defined twice")
            OBJECT_NODE_CLASSES_BY_PATTERN[cls._pattern] = cls

    @classmethod
    def create_minimal(cls, defaults=None, _builder=None, *, tag: str | None = None):
        builder = _builder or Builder()
        new = cls(builder.build(_get_schema_from_tag(tag or cls._default_tag), defaults))

        if tag:
            new._read_tag = tag

        return new

    @classmethod
    def create_fake_data(cls, defaults=None, shape=None, _builder=None, *, tag: str | None = None):
        return cls.create_minimal(defaults, _builder or FakeDataBuilder(shape), tag=tag)

    @classmethod
    def create_from_node(cls, node, _builder=None, *, tag: str | None = None):
        return cls.create_minimal(node, _builder or NodeBuilder(), tag=tag)

    @property
    def _tag(self):
        if self._read_tag is None:
            return self._default_tag

        return self._read_tag

    @property
    def tag(self):
        return self._tag

    def get_schema(self):
        """Retrieve the schema associated with this tag"""
        return _get_schema_from_tag(self.tag)


class TaggedListNode(LNode):
    """
    Base class for all tagged list defined by RAD
        There will be one of these for any tagged object defined by RAD, which has
        base type: array.
    """

    __slots__ = ()

    _default_tag: ClassVar[str]

    def __init_subclass__(cls, **kwargs) -> None:
        """
        Register any subclasses of this class in the LIST_NODE_CLASSES_BY_PATTERN
        registry.
        """
        super().__init_subclass__(**kwargs)
        if cls.__name__ != "TaggedListNode":
            if cls._pattern in LIST_NODE_CLASSES_BY_PATTERN:
                raise RuntimeError(f"TaggedListNode class for tag '{cls._pattern}' has been defined twice")
            LIST_NODE_CLASSES_BY_PATTERN[cls._pattern] = cls

    @classmethod
    def create_minimal(cls, defaults=None, _builder=None, *, tag: str | None = None):
        builder = _builder or Builder()
        new = cls(builder.build(_get_schema_from_tag(tag or cls._default_tag), defaults))

        if tag:
            new._read_tag = tag

        return new

    @classmethod
    def create_fake_data(cls, defaults=None, shape=None, _builder=None, *, tag: str | None = None):
        return cls.create_minimal(defaults, _builder or FakeDataBuilder(shape), tag=tag)

    @classmethod
    def create_from_node(cls, node, _builder=None, *, tag: str | None = None):
        return cls.create_minimal(node, _builder or NodeBuilder(), tag=tag)

    @property
    def _tag(self):
        if self._read_tag is None:
            return self._default_tag

        return self._read_tag

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

    _pattern: ClassVar[str]
    _latest_manifest: ClassVar[str]
    _default_tag: ClassVar[str]

    _read_tag: str

    def __init_subclass__(cls, **kwargs) -> None:
        """
        Register any subclasses of this class in the SCALAR_NODE_CLASSES_BY_PATTERN
        and SCALAR_NODE_CLASSES_BY_KEY registry.
        """
        super().__init_subclass__(**kwargs)
        if cls.__name__ != "TaggedScalarNode":
            if cls._pattern in SCALAR_NODE_CLASSES_BY_PATTERN:
                raise RuntimeError(f"TaggedScalarNode class for tag '{cls._pattern}' has been defined twice")
            SCALAR_NODE_CLASSES_BY_PATTERN[cls._pattern] = cls
            SCALAR_NODE_CLASSES_BY_KEY[name_from_tag_uri(cls._pattern)] = cls

    def __asdf_traverse__(self):
        return self

    def __init__(self, value, **kwargs):
        pass

    @classmethod
    def create_minimal(cls, defaults=None, _builder=None, *, tag: str | None = None):
        builder = _builder or Builder()
        value = builder.build(_get_schema_from_tag(tag or cls._default_tag), defaults)
        if value is _NO_VALUE:
            return value

        new = cls(value)
        if tag:
            new._read_tag = tag

        return new

    @classmethod
    def create_fake_data(cls, defaults=None, shape=None, _builder=None, *, tag: str | None = None):
        return cls.create_minimal(defaults, _builder or FakeDataBuilder(shape), tag=tag)

    @classmethod
    def create_from_node(cls, node, _builder=None, *, tag: str | None = None):
        return cls.create_minimal(node, _builder or NodeBuilder(), tag=tag)

    @property
    def _tag(self):
        # _tag is required by asdf to allow __asdf_traverse__
        return getattr(self, "_read_tag", self._default_tag)

    @property
    def tag(self):
        return self._tag

    def get_schema(self):
        return _get_schema_from_tag(self.tag)

    def copy(self):
        return copy.copy(self)


tagged_type: TypeAlias = type[TaggedObjectNode] | type[TaggedListNode] | type[TaggedScalarNode]
