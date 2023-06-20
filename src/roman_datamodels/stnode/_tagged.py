from abc import ABCMeta

import asdf
import asdf.schema as asdfschema

from ._node import DNode, LNode
from ._registry import (
    LIST_NODE_CLASSES_BY_TAG,
    OBJECT_NODE_CLASSES_BY_TAG,
    SCALAR_NODE_CLASSES_BY_KEY,
    SCALAR_NODE_CLASSES_BY_TAG,
)


class TaggedObjectNodeMeta(ABCMeta):
    """
    Metaclass for TaggedObjectNode that maintains a registry
    of subclasses.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.__name__ != "TaggedObjectNode":
            if self._tag in OBJECT_NODE_CLASSES_BY_TAG:
                raise RuntimeError(f"TaggedObjectNode class for tag '{self._tag}' has been defined twice")
            OBJECT_NODE_CLASSES_BY_TAG[self._tag] = self


class TaggedObjectNode(DNode, metaclass=TaggedObjectNodeMeta):
    """
    Expects subclass to define a class instance of _tag
    """

    @property
    def tag(self):
        return self._tag

    def _schema(self):
        if self._x_schema is None:
            self._x_schema = self.get_schema()
        return self._x_schema

    def get_schema(self):
        """Retrieve the schema associated with this tag"""
        extension_manager = self.ctx.extension_manager
        tag_def = extension_manager.get_tag_definition(self.tag)
        schema_uri = tag_def.schema_uris[0]
        schema = asdfschema.load_schema(schema_uri, resolve_references=True)
        return schema


class TaggedListNodeMeta(ABCMeta):
    """
    Metaclass for TaggedListNode that maintains a registry
    of subclasses.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.__name__ != "TaggedListNode":
            if self._tag in LIST_NODE_CLASSES_BY_TAG:
                raise RuntimeError(f"TaggedListNode class for tag '{self._tag}' has been defined twice")
            LIST_NODE_CLASSES_BY_TAG[self._tag] = self


class TaggedListNode(LNode, metaclass=TaggedListNodeMeta):
    @property
    def tag(self):
        return self._tag


def _scalar_tag_to_key(tag):
    return tag.split("/")[-1].split("-")[0]


class TaggedScalarNodeMeta(ABCMeta):
    """
    Metaclass for TaggedScalarNode that maintains a registry
    of subclasses.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.__name__ != "TaggedScalarNode":
            if self._tag in SCALAR_NODE_CLASSES_BY_TAG:
                raise RuntimeError(f"TaggedScalarNode class for tag '{self._tag}' has been defined twice")
            SCALAR_NODE_CLASSES_BY_TAG[self._tag] = self
            SCALAR_NODE_CLASSES_BY_KEY[_scalar_tag_to_key(self._tag)] = self


class TaggedScalarNode(metaclass=TaggedScalarNodeMeta):
    _tag = None
    _ctx = None

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
        return _scalar_tag_to_key(self._tag)

    def get_schema(self):
        extension_manager = self.ctx.extension_manager
        tag_def = extension_manager.get_tag_definition(self.tag)
        schema_uri = tag_def.schema_uris[0]
        schema = asdf.schema.load_schema(schema_uri, resolve_references=True)
        return schema

    def copy(self):
        import copy

        return copy.copy(self)
