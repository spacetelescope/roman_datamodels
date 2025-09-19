"""
Base classes for all the tagged objects defined by RAD.
    Each tagged object will be dynamically created at runtime by _stnode.py
    from RAD's manifest.
"""

from __future__ import annotations

import copy
from abc import ABC, abstractmethod
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
    from collections.abc import Mapping
    from typing import Any, ClassVar, Self, TypeAlias

__all__ = ["TaggedListNode", "TaggedObjectNode", "TaggedScalarNode"]


def name_from_tag_uri(tag_uri: str) -> str:
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


class _TaggedNodeMixin(ABC):
    """
    Mixin class for all tagged nodes
    """

    __slots__ = ()

    _pattern: ClassVar[str]
    _latest_manifest: ClassVar[str]
    _default_tag: ClassVar[str]

    @classmethod
    @abstractmethod
    def create_minimal(
        cls, defaults: Mapping[str, Any] | None = None, builder: Builder | None = None, *, tag: str | None = None
    ) -> Self:
        """
        Create a minimal instance of this class, only things with the attributes
        which have a default value that can be determined.

        Parameters
        ----------
        defaults : Mapping[str, Any] | None
            A mapping of default values to use when creating the instance
        builder : Builder | None
            The builder to use when creating the instance
        tag : str | None
            The tag to use when creating the instance. If None, the default tag for the class will be used.

        Returns
        -------
        Self
            An instance of this class
        """

    @classmethod
    def create_fake_data(
        cls,
        defaults: Mapping[str, Any] | None = None,
        shape: tuple[int, ...] | None = None,
        builder: Builder | None = None,
        *,
        tag: str | None = None,
    ) -> Self:
        """
        Create an instance of this class with with all required attributes
        filled in with fake data.

        Parameters
        ----------
        defaults, optional
            A mapping of default values to use when creating the instance
        shape, optional
            The shape of the data to create
        builder, optional
            The builder to use when creating the instance
        tag, optional
            The tag to use when creating the instance. If None, the default tag for the class will be used.

        Returns
        -------
        Self
            An instance of this class
        """
        return cls.create_minimal(defaults, builder or FakeDataBuilder(shape), tag=tag)

    @classmethod
    def create_from_node(cls, node: Mapping[str, Any], builder: Builder | None = None, *, tag: str | None = None) -> Self:
        """
        Create an instance of this class from a node (dict-like object)

        Parameters
        ----------
        node
            The node to create the instance from
        builder, optional
            The builder to use when creating the instance
        tag, optional
            The tag to use when creating the instance. If None, the default tag for the class will be used.

        Returns
        -------
        Self
            An instance of this class
        """
        return cls.create_minimal(node, builder or NodeBuilder(), tag=tag)

    @property
    @abstractmethod
    def _tag(self):
        pass

    @property
    def tag(self):
        return self._tag

    def get_schema(self):
        """Retrieve the schema associated with this tag"""
        return _get_schema_from_tag(self.tag)


class TaggedObjectNode(DNode, _TaggedNodeMixin):
    """
    Base class for all tagged objects defined by RAD
        There will be one of these for any tagged object defined by RAD, which has
        base type: object.
    """

    __slots__ = ()

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
    def create_minimal(cls, defaults=None, builder=None, *, tag=None):
        builder = builder or Builder()
        new = cls(builder.build(_get_schema_from_tag(tag or cls._default_tag), defaults))

        if tag:
            new._read_tag = tag

        return new

    @property
    def _tag(self):
        if self._read_tag is None:
            return self._default_tag

        return self._read_tag


class TaggedListNode(LNode, _TaggedNodeMixin):
    """
    Base class for all tagged list defined by RAD
        There will be one of these for any tagged object defined by RAD, which has
        base type: array.
    """

    __slots__ = ()

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
    def create_minimal(cls, defaults=None, builder=None, *, tag=None):
        builder = builder or Builder()
        new = cls(builder.build(_get_schema_from_tag(tag or cls._default_tag), defaults))

        if tag:
            new._read_tag = tag

        return new

    @property
    def _tag(self):
        if self._read_tag is None:
            return self._default_tag

        return self._read_tag


class TaggedScalarNode(_TaggedNodeMixin):
    """
    Base class for all tagged scalars defined by RAD
        There will be one of these for any tagged object defined by RAD, which has
        a scalar base type, or wraps a scalar base type.
        These will all be in the tagged_scalars directory.
    """

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
    def create_minimal(cls, defaults=None, builder=None, *, tag: str | None = None):
        builder = builder or Builder()
        value = builder.build(_get_schema_from_tag(tag or cls._default_tag), defaults)
        if value is _NO_VALUE:
            return value

        new = cls(value)
        if tag:
            new._read_tag = tag

        return new

    @property
    def _tag(self):
        # _tag is required by asdf to allow __asdf_traverse__
        return getattr(self, "_read_tag", self._default_tag)

    def copy(self):
        return copy.copy(self)


tagged_type: TypeAlias = type[TaggedObjectNode] | type[TaggedListNode] | type[TaggedScalarNode]
