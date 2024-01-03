from enum import Enum
from inspect import isclass
from typing import ClassVar, get_args

from pydantic import BaseModel, ConfigDict, RootModel

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

        def _field_type(annotation: type) -> type:
            """Get the type of a field"""

            if isclass(annotation):
                return annotation

            return _field_type(get_args(annotation)[0])

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
