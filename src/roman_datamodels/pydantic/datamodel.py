from __future__ import annotations

from enum import Enum
from inspect import isclass
from typing import ClassVar, get_args

from pydantic import BaseModel, ConfigDict, RootModel
from pydantic.fields import FieldInfo
from pydantic_core import PydanticUndefined

from .adaptors import Adaptor
from .metadata import Archive, Archives


class RomanDataModel(BaseModel):
    _tag_uri: ClassVar[str | None] = None

    model_config = ConfigDict(
        protected_namespaces=(),
    )

    def to_asdf_tree(self):
        """Convert to an ASDF tree, stopping at tags"""

        tree = dict(self)

        for field_name, field in tree.items():
            if isinstance(field, RomanDataModel) and field._tag_uri is not None:
                tree[field_name] = field.to_asdf_tree()

            if isinstance(field, dict):
                for key, value in field.items():
                    if isinstance(value, RomanDataModel) and value._tag_uri is not None:
                        field[key] = value.to_asdf_tree()

            if isinstance(field, list):
                for index, value in enumerate(field):
                    if isinstance(value, RomanDataModel) and value._tag_uri is not None:
                        field[index] = value.to_asdf_tree()

            if isinstance(field, RootModel) and (not hasattr(field, "_tag_uri") or field._tag_uri is None):
                tree[field_name] = field.root

            if isinstance(field, Enum):
                tree[field_name] = field.value

        return tree

    @classmethod
    def get_archive_metadata(cls) -> dict[str, Archive | Archives]:
        """Get the archive data for this model"""

        metadata = {}

        for field_name, field in cls.model_fields.items():
            if (archive := Archive(**({} if field.json_schema_extra is None else field.json_schema_extra))).has_info:
                metadata[field_name] = archive

            field_type = _field_type(field.annotation)
            if issubclass(field_type, RomanDataModel) and (archive := field_type.get_archive_metadata()):
                metadata[field_name] = archive

            if issubclass(field_type, RootModel):
                extra = field_type.model_fields["root"].json_schema_extra
                if (archive := Archive(**({} if extra is None else extra))).has_info:
                    metadata[field_name] = archive

        return metadata

    @classmethod
    def make_default(cls, **kwargs) -> RomanDataModel:
        """Create a default instance of this model"""

        defaults = {}
        for field_name, field in cls.model_fields.items():
            if field_name.endswith("_"):
                field_name = field_name[:-1]
            if field.is_required():
                if field.default is not PydanticUndefined:
                    defaults[field_name] = field.default
                    continue

                if (adaptor := _get_adaptor(field)) is not None:
                    defaults[field_name] = adaptor.make_default(**kwargs)
                    continue

                if field_name == "read_pattern":
                    defaults[field_name] = [[1], [2, 3], [4], [5, 6, 7, 8], [9, 10], [11]]
                    continue

                if field_name == "cal_logs":
                    defaults[field_name] = [
                        "2021-11-15T09:15:07.12Z :: FlatFieldStep :: INFO :: Completed",
                        "2021-11-15T10:22.55.55Z :: RampFittingStep :: WARNING :: Wow, lots of Cosmic Rays detected",
                    ]
                    continue

                field_type = _field_type(field.annotation)
                if issubclass(field_type, RomanDataModel):
                    defaults[field_name] = field_type.make_default(**kwargs)
                    continue

                if field_type is float or field_type is int:
                    defaults[field_name] = -999999
                    continue

                if field_type is str:
                    defaults[field_name] = "dummy value"
                    continue

                if field_type is bool:
                    defaults[field_name] = False
                    continue

                if issubclass(field_type, Enum):
                    defaults[field_name] = next(field_type.__iter__()).value
                    continue

        return cls(**defaults)


def _get_adaptor(field: FieldInfo) -> Adaptor | None:
    if field.metadata:
        metadata = field.metadata
        if isinstance(field.metadata, list) and len(field.metadata) == 1:
            metadata = field.metadata[0]

        if isclass(metadata) and issubclass(metadata, Adaptor):
            return metadata

    if issubclass(adaptor := _field_type(field.annotation), Adaptor):
        return adaptor

    return None


def _field_type(annotation: type) -> type:
    """Get the type of a field"""

    if isclass(annotation):
        return annotation

    args = get_args(annotation)
    if args[-1] is None:
        return _field_type(args[0])

    if isclass(args[-1]) and issubclass(args[-1], Adaptor):
        return args[-1]

    return _field_type(get_args(annotation)[0])
