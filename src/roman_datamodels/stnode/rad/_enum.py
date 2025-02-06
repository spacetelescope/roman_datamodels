from abc import ABC, ABCMeta, abstractmethod
from enum import Enum, EnumType

from ..core import classproperty
from ._asdf_schema import RadSchema
from ._node import ScalarNode
from ._schema import SchemaMixin, SchemaScalarNode
from ._tagged import TaggedScalarNode

__all__ = [
    "EnumNodeMixin",
    "IntNodeMixin",
    "NodeEnumMeta",
    "RadEnum",
    "SchemaStrNodeMixin",
    "StrNodeMixin",
    "TaggedStrNodeMixin",
]


class EnumNodeMixin(ABC):
    """
    Mixin for nodes that are enums.

    NOTE: due to mixins with built in classes (think str) ABC enforcement goes away.
          asdf_schema needs to be implemented by the enum node class itself.
          simply point this at the property that contains the enum
    """

    @classmethod
    @abstractmethod
    def _asdf_container(cls) -> type[SchemaMixin]:
        """
        The subclass definition for the asdf container
        """

    @classproperty
    def asdf_container(cls) -> type[SchemaMixin]:
        """Get the class that contains the enum"""
        return cls._asdf_container()

    @classmethod
    @abstractmethod
    def _asdf_property_name(cls) -> str:
        """
        The subclass definition for the asdf property name
        """

    @classproperty
    def asdf_property_name(cls) -> str:
        """
        The name of the property that contains the enum
        """
        return cls._asdf_property_name()

    @classmethod
    def _asdf_schema(cls) -> RadSchema:
        """Get the schema for the enum node"""
        # This is reached by the docs build as it ignores the abstractness of the class
        # which causes a doc failure, the cache makes this irrelevant in general
        if cls.asdf_container.asdf_schema is None:
            return RadSchema({})  # type: ignore[unreachable]

        schema = cls.asdf_container.asdf_schema.fields[cls.asdf_property_name]
        if "anyOf" in schema.schema:
            return RadSchema(schema.schema["anyOf"][0]["enum"])

        return RadSchema(schema.get_key("enum")[0])


class RadEnum(Enum):
    def __repr__(self) -> str:
        return repr(self.value)

    def __str__(self) -> str:
        return str(self.value)


class NodeEnumMeta(ABCMeta, EnumType):
    """
    Meta class for enums of nodes

    Since all nodes are ABC classes they have ABCMeta as their metaclass. But
    Enum classes have EnumType (used to be EnumMeta) as their metaclass. This
    makes it so that the enum classes cannot be ABC classes due to a metaclass
    conflict. This metaclass resolves that conflict by inheriting from both
    enabling the use of the enum
    """


class StrNodeMixin(str, EnumNodeMixin, ScalarNode, ABC):
    """
    String EnumNode mixin
    """


class SchemaStrNodeMixin(str, SchemaScalarNode, EnumNodeMixin, ABC):
    """
    String EnumNode mixin for schema nodes
    """


class TaggedStrNodeMixin(str, TaggedScalarNode, EnumNodeMixin, ABC):
    """
    String EnumNode mixin for tagged nodes
    """


class IntNodeMixin(int, EnumNodeMixin, ScalarNode, ABC):
    """
    Integer EnumNode mixin
    """
