import warnings
from abc import ABC
from collections.abc import Generator
from enum import Enum
from inspect import getattr_static
from typing import Any

from asdf import AsdfFile
from asdf.lazy_nodes import AsdfDictNode, AsdfListNode

from ..core import DNode, FlushOptions, LNode, classproperty, get_config
from ._base import RadNodeMixin

__all__ = [
    "ExtraFieldsMixin",
    "ListNode",
    "ObjectNode",
    "ScalarNode",
]


class ObjectNode(DNode[Any], RadNodeMixin, ABC):
    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)

        # Inject the schema into the fields
        for name in cls.node_fields:
            getattr_static(cls, name)._schema = lambda: cls.asdf_schema

    @classmethod
    def _asdf_required(cls) -> set[str]:
        """List of required fields in this node."""
        # This is reached by the docs build as it ignores the abstractness of the class
        # which causes a doc failure, the cache makes this irrelevant in general
        if (schema := cls.asdf_schema) is None:
            return set()  # type: ignore[unreachable]
        return schema.required

    @classproperty
    def asdf_required(cls) -> set[str]:
        """List of required fields in this node."""
        return cls._asdf_required()

    @property
    def schema_required(self) -> tuple[str, ...]:
        """List of required fields in the schema."""
        # This is reached by the docs build as it ignores the abstractness of the class
        # which causes a doc failure, the cache makes this irrelevant in general
        if (schema := self.schema) is None:
            return ()  # type: ignore[unreachable]
        return tuple(schema.required)

    @classproperty
    def asdf_property_order(cls) -> tuple[str, ...]:
        """Order of properties in the schema."""
        # This is reached by the docs build as it ignores the abstractness of the class
        # which causes a doc failure, the cache makes this irrelevant in general
        if (schema := cls.asdf_schema) is None:
            return ()  # type: ignore[unreachable]
        return schema.property_order

    def _field_generator(self, flush: FlushOptions = FlushOptions.NONE) -> Generator[str, None, None]:
        """
        Generator which yields the fields of this object.
            yields the field values in the following order:
                1. Fields in the order defined in the schema via the `propertyOrder` keyword.
                2. Required fields not already yielded in alphabetical order.
                3. Non-required fields not already yielded in alphabetical order.
                4. Extra fields not already yielded in alphabetical order.
                5. All other non-yielded data in _data in alphabetical order
        """
        flush_fields = FlushOptions.get_fields(self, flush)

        data_fields = set(self._data.keys())
        visited_fields = set()

        def handle_field(field: str) -> Generator[str, None, None]:
            """
            Handle yielding the actual field
            """
            if field not in visited_fields:
                visited_fields.add(field)
                if self._to_schema_key(field) in data_fields:
                    data_fields.remove(self._to_schema_key(field))
                    yield field

                # Elif is necessary to prevent yielding the field twice
                # if it is in both
                elif field in flush_fields:
                    yield field

                # Don't yield the field if it isn't already defined and isn't being
                # flushed out
            else:
                raise ValueError(f"Field {field} has already been visited!")

        # 1) Return fields in the order defined by `propertyOrder`
        for field_ in self.asdf_property_order:
            yield from handle_field(field_)

        # 2) Return required fields not already yielded in alphabetical order
        for field_ in sorted(set(self.schema_required) - visited_fields):
            yield from handle_field(field_)

        # 3) Return non-required fields not already yielded in alphabetical order
        for field_ in sorted(set(self.defined_fields) - visited_fields):
            yield from handle_field(field_)

        # 4) Return extra fields not already yielded in alphabetical order
        for field_ in sorted(set(self.fields) - visited_fields):
            yield from handle_field(field_)

        # 5) Return all other non-yielded data in _data in alphabetical order
        for field_ in sorted(data_fields):
            yield field_

    def node_items(
        self, *, flush: FlushOptions = FlushOptions.NONE, warn: bool = False
    ) -> Generator[tuple[str, Any], None, None]:
        """
        Generator which yields the fields and values of this object.
            yields the field values in the following order:
                1. Fields in the order defined in the schema via the ``propertyOrder`` keyword.
                2. Required fields not already yielded in alphabetical order.
                3. Non-required fields not already yielded in alphabetical order.
                4. Extra fields not already yielded in alphabetical order.
                5. All other non-yielded data in _data in alphabetical order
        """
        for field_ in self._field_generator(flush):
            if not self._has_node(field_) and warn:
                warnings.warn(f"Filling in missing required field '{field_}' with default value.", UserWarning, stacklevel=2)

            yield field_, getattr(self, field_)

    def flat_items(
        self, *, flush: FlushOptions = FlushOptions.NONE, warn: bool = False
    ) -> Generator[tuple[str, Any], None, None]:
        """
        Generator which yields the fields and values of this object, flattened to be keys ``foo.bar.baz``.
            yields the flattened field values, where it will yield until exhausting all the subfields
            following the same ordering

            field values in the following order at the same level:
                1. Fields in the order defined in the schema via the ``propertyOrder`` keyword.
                2. Required fields not already yielded in alphabetical order.
                3. Non-required fields not already yielded in alphabetical order.
                4. Extra fields not already yielded in alphabetical order.
                5. All other non-yielded data in _data in alphabetical order
        """

        def recurse(tree: Any, path: list[str | int] | None = None) -> Generator[tuple[str, Any], None, None]:
            """
            Recurse through the tree to flatten it
            """
            path = path or []

            if isinstance(tree, ObjectNode):
                for field, value in tree.node_items(flush=flush, warn=warn):
                    yield from recurse(value, [*path, field])
            elif isinstance(tree, DNode | dict | AsdfDictNode):
                for field, value in sorted(tree.items()):
                    yield from recurse(value, [*path, field])
            elif isinstance(tree, LNode | list | AsdfListNode):
                for idx, value in enumerate(tree):
                    yield from recurse(value, [*path, idx])
            else:
                yield ".".join(map(str, path)), tree.value if isinstance(tree, Enum) else tree

        yield from recurse(self)

    def flush(self, flush: FlushOptions = FlushOptions.REQUIRED, warn: bool = False, recurse: bool = False) -> None:
        """
        Flush out the object.
            This will be used by asdf to ensure that all required fields are present
            prior to writing the tree to disk. These objects are intended to be
            filled in lazily, so this method will fill in any missing required fields
            making sure that the object is in a valid state for writing to disk.

        Parameters
        ----------
        flush
            Options for flushing out required fields, see FlushOptions for more info
        warn
            If `True`, warn if any required fields are missing.
        recurse
            If we recurese the flush into subnodes
        """
        for field_ in FlushOptions.get_fields(self, flush):
            if not self._has_node(field_) and warn:
                warnings.warn(f"Filling in missing required field '{field_}' with default value.", UserWarning, stacklevel=2)

            # access the field to trigger its default value
            field_value = getattr(self, field_)
            if recurse and isinstance(field_value, ObjectNode):
                field_value.flush(flush=flush, warn=warn, recurse=recurse)

    def to_asdf_tree(self, ctx: AsdfFile, flush: FlushOptions = FlushOptions.REQUIRED, warn: bool = False) -> dict[str, Any]:
        # Flush out any required fields
        self.flush(flush, warn)
        return super().to_asdf_tree(ctx, flush=flush, warn=warn)

    def __asdf_traverse__(self) -> dict[str, Any]:
        return self.to_asdf_tree(ctx=get_config().asdf_ctx, flush=FlushOptions.REQUIRED, warn=False)


class ExtraFieldsMixin(ObjectNode, ABC):
    """
    Mixin for objects that have extra fields
    """


class ListNode(LNode[Any], RadNodeMixin, ABC):
    """
    Base class for all list nodes
    """


class ScalarNode(RadNodeMixin, ABC):
    """
    Base class for all scalars with descriptions in RAD
    -> this is for enums that are not tagged
    """

    def unwrap(self) -> Any:
        base = self.value if isinstance(self, Enum) else self

        return type(base).__bases__[0](base)

    def to_asdf_tree(self, ctx: AsdfFile, flush: FlushOptions = FlushOptions.REQUIRED, warn: bool = False) -> Any:
        return self.unwrap()

    def __asdf_traverse__(self) -> Any:
        return self.to_asdf_tree(ctx=get_config().asdf_ctx, flush=FlushOptions.REQUIRED, warn=False)
