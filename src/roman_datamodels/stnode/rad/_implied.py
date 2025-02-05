from abc import ABC, abstractmethod
from typing import Any, cast

from ..core import classproperty, field
from ._asdf_schema import RadSchema
from ._base import RadNodeMixin
from ._schema import SchemaMixin
from ._utils import camel_case_to_snake_case

__all__ = ["ImpliedNodeMixin"]


class ImpliedNodeMixin(RadNodeMixin, ABC):
    """
    Mixin for nodes that are implied by other nodes.

    These nodes should have names following the convention:
        <implying_node_name>_<camel_case(implied_property_name)>
    """

    @classmethod
    @abstractmethod
    def _asdf_implied_by(cls) -> type[SchemaMixin]:
        """The name of the field that implies this node."""

    @classproperty
    def asdf_implied_by(cls) -> type[SchemaMixin]:
        """Get the class that implies this node."""
        return cls._asdf_implied_by()

    @classproperty
    def asdf_implied_property_name(cls) -> str:
        """The name of the property that implies this node."""

        # MyPy thinks that ImpliedNodeMixin has no attribute __name__
        return camel_case_to_snake_case(cls.__name__.split("_")[-1])  # type: ignore[attr-defined]

    @classproperty
    def asdf_implied_property(cls) -> field[Any]:
        """Get the raw property object that will accept this node"""

        # This is reached by the docs build as it ignores the abstractness of the class
        # which causes a doc failure, the cache makes this irrelevant in general
        if cls.asdf_implied_by is None:
            return None  # type: ignore[unreachable]

        return cast(field[Any], getattr(cls.asdf_implied_by, cls.asdf_implied_property_name))

    @classmethod
    def _asdf_schema(cls) -> RadSchema:
        """Get the schema for the implied node"""
        # This is reached by the docs build as it ignores the abstractness of the class
        # which causes a doc failure, the cache makes this irrelevant in general
        if (schema := cls.asdf_implied_by.asdf_schema) is None:
            return RadSchema({})  # type: ignore[unreachable]
        return schema.fields[cls.asdf_implied_property_name]

    # TODO: Figure out why I need to redefine this here
    @property
    def schema(self) -> RadSchema:
        """Get the schema for this instance."""
        return self.asdf_schema
