"""
The datamodel-code-generator based parser for the RAD schemas.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any
from urllib.parse import ParseResult

from datamodel_code_generator import DataModelType
from datamodel_code_generator.format import PythonVersion
from datamodel_code_generator.model import get_data_model_types
from datamodel_code_generator.parser.base import get_special_path
from datamodel_code_generator.parser.jsonschema import JsonSchemaParser, get_model_by_path
from datamodel_code_generator.types import DataType

from roman_datamodels.pydantic import BaseRomanDataModel

from ._adaptor import adaptor_factory, has_adaptor
from ._reslover import RadModelResolver
from ._schema import RadSchemaObject
from ._utils import class_name_from_uri, remove_uri_version

__all__ = ["RadSchemaParser"]


class RadSchemaParser(JsonSchemaParser):
    """Modifications to the JsonSchemaParser to support Rad schemas"""

    def __init__(
        self,
        source: str | Path | list[Path] | ParseResult,
    ) -> None:
        """
        Note this explicitly feeds all the adjusted arguments to the JsonSchemaParser's
        __init__ method, so that we don't have to replicate the interface here.
        """
        data_model_types = get_data_model_types(DataModelType.PydanticV2BaseModel, target_python_version=PythonVersion.PY_310)

        # Use the datamodel as the baseclass
        base_class = f"{BaseRomanDataModel.__module__}.{BaseRomanDataModel.__name__}"

        super().__init__(
            source=source,
            # Select the PydanticV2BaseModel as the base class
            data_model_type=data_model_types.data_model,
            data_model_root_type=data_model_types.root_model,
            data_model_field_type=data_model_types.field_model,
            data_type_manager_type=data_model_types.data_type_manager,
            dump_resolve_reference_action=data_model_types.dump_resolve_reference_action,
            # Python version
            target_python_version=PythonVersion.PY_310,
            # Use the annotated style
            use_annotated=True,
            # Use field constraints
            field_constraints=True,
            # String pointing the the RomanDataModel class
            base_class=base_class,
            # Use the template files to modify the code output
            custom_template_dir=Path(__file__).parent / "custom_templates",
            # We use some class variables in the generated code, Pydantic needs those
            #   to be specifically annotated as such.
            additional_imports=["typing.ClassVar"],
            # Include the archive metadata in the generated code
            field_extra_keys={"sdf", "archive_catalog"},
        )
        # Override the standard model resolver in order to enable ASDF to handle
        #     resolving some schema references
        self.model_resolver = RadModelResolver(
            base_url=self.model_resolver.base_url,
            singular_name_suffix=self.model_resolver.singular_name_suffix,
            aliases=None,
            empty_field_name=None,
            snake_case_field=None,
            custom_class_name_generator=lambda name: name,
            base_path=self.base_path,
            original_field_name_delimiter=None,
            special_field_name_prefix=None,
            remove_special_field_name_prefix=False,
            capitalise_enum_members=False,
        )

    def get_data_type(self, obj: RadSchemaObject) -> DataType:
        """Short circuit to enable reaching to ASDF types outside of RAD"""
        if has_adaptor(obj):
            return adaptor_factory(obj, self.data_type_manager.data_type())
        return super().get_data_type(obj)

    def parse_item(
        self,
        name: str,
        item: RadSchemaObject,
        path: list[str],
        singular_name: bool = False,
        parent: RadSchemaObject | None = None,
    ) -> DataType:
        """Short circuit to enable reaching to ASDF types outside of RAD"""
        if has_adaptor(item):
            return adaptor_factory(item, self.data_type_manager.data_type())
        return super().parse_item(name, item, path, singular_name, parent)

    def set_title(self, name: str, obj: RadSchemaObject) -> None:
        """Override the title setting to use our naming conventions"""
        if obj.title:
            self.extra_template_data[name]["title"] = obj.title

        # Be sure to include the tag_uri in the template data
        if obj.tag_uri:
            self.extra_template_data[name]["tag_uri"] = obj.tag_uri

        if obj.id:
            self.extra_template_data[name]["id"] = obj.id

    def parse_array(self, name: str, obj: RadSchemaObject, path: list[str], original_name: str | None = None) -> DataType:
        """Insert the ability to tag an array"""
        self.set_title(name, obj)

        return super().parse_array(name, obj, path, original_name)

    def parse_object(
        self,
        name: str,
        obj: RadSchemaObject,
        path: list[str],
        singular_name: bool = False,
        unique: bool = True,
    ) -> DataType:
        """Short circuit to enable reaching to ASDF types outside of RAD"""
        if has_adaptor(obj):
            return adaptor_factory(obj, self.data_type_manager.data_type())
        return super().parse_object(name, obj, path, singular_name, unique)

    @property
    def current_source_path(self) -> Path:
        """Override the current_source_path to remove the version from the path"""
        return self._current_source_path

    @current_source_path.setter
    def current_source_path(self, value: Path) -> None:
        """
        Override the current_source_path to remove the version from the path

        The version number plays havoc with the module names, and we don't need it
        in those name in any case.
        """
        self._current_source_path = Path(remove_uri_version(str(value)))

    ###### Below this point are copies of the JsonSchemaParser methods, with the
    ######   JsonSchemaObject replaced with RadSchemaObject to enable the custom
    ######   processing of the ASDF related bits of RAD schemas
    ###### These can be removed once datamodel-code-generator is released with
    ######   the changes from https://github.com/koxudaxi/datamodel-code-generator/pull/1783

    def parse_combined_schema(
        self,
        name: str,
        obj: RadSchemaObject,
        path: list[str],
        target_attribute_name: str,
    ) -> list[DataType]:
        """
        This is a copy of the JsonSchemaParser.parse_combined_schema method, but with the
        JsonSchemaObject replaced with RadSchemaObject to enable the custom processing of
        our Json schema extension
        """
        base_object = obj.dict(exclude={target_attribute_name}, exclude_unset=True, by_alias=True)
        combined_schemas: list[RadSchemaObject] = []
        refs = []
        for index, target_attribute in enumerate(getattr(obj, target_attribute_name, [])):
            if target_attribute.ref:
                combined_schemas.append(target_attribute)
                refs.append(index)
            else:
                combined_schemas.append(
                    RadSchemaObject.parse_obj(
                        self._deep_merge(
                            base_object,
                            target_attribute.dict(exclude_unset=True, by_alias=True),
                        )
                    )
                )

        parsed_schemas = self.parse_list_item(
            name,
            combined_schemas,
            path,
            obj,
            singular_name=False,
        )
        common_path_keyword = f"{target_attribute_name}Common"
        return [
            self._parse_object_common_part(
                name,
                obj,
                [*get_special_path(common_path_keyword, path), str(i)],
                ignore_duplicate_model=True,
                fields=[],
                base_classes=[d.reference],
                required=[],
            )
            if i in refs and d.reference
            else d
            for i, d in enumerate(parsed_schemas)
        ]

    def parse_raw_obj(
        self,
        name: str,
        raw: dict[str, Any],
        path: list[str],
    ) -> None:
        """
        This is a copy of the JsonSchemaParser.parse_raw_obj method, but with the
        JsonSchemaObject replaced with RadSchemaObject to enable the custom processing of
        our Json schema extension
        """
        self.parse_obj(name, RadSchemaObject.parse_obj(raw), path)

    def _parse_file(
        self,
        raw: dict[str, Any],
        obj_name: str,
        path_parts: list[str],
        object_paths: list[str] | None = None,
    ) -> None:
        """
        This is a copy of the JsonSchemaParser._parse_file method, but with the
        JsonSchemaObject replaced with RadSchemaObject to enable the custom processing of
        our Json schema extension
        """
        obj_name = class_name_from_uri(raw.get("id", "NoID"))

        object_paths = [o for o in object_paths or [] if o]
        if object_paths:
            path = [*path_parts, f"#/{object_paths[0]}", *object_paths[1:]]
        else:
            path = path_parts
        with self.model_resolver.current_root_context(path_parts):
            obj_name = self.model_resolver.add(path, obj_name, unique=False, class_name=True).name
            with self.root_id_context(raw):
                # Some jsonschema docs include attribute self to have include version details
                raw.pop("self", None)
                # parse $id before parsing $ref
                root_obj = RadSchemaObject.parse_obj(raw)
                self.parse_id(root_obj, path_parts)
                definitions: dict[Any, Any] | None = None
                for schema_path, split_schema_path in self.schema_paths:
                    try:
                        definitions = get_model_by_path(raw, split_schema_path)
                        if definitions:
                            break
                    except KeyError:
                        continue
                if definitions is None:
                    definitions = {}

                for key, model in definitions.items():
                    obj = RadSchemaObject.parse_obj(model)
                    self.parse_id(obj, [*path_parts, schema_path, key])

                if object_paths:
                    models = get_model_by_path(raw, object_paths)
                    model_name = object_paths[-1]
                    self.parse_obj(model_name, RadSchemaObject.parse_obj(models), path)
                else:
                    self.parse_obj(obj_name, root_obj, path_parts or ["#"])
                for key, model in definitions.items():
                    path = [*path_parts, schema_path, key]
                    reference = self.model_resolver.get(path)
                    if not reference or not reference.loaded:
                        self.parse_raw_obj(key, model, path)

                key = tuple(path_parts)
                reserved_refs = set(self.reserved_refs.get(key) or [])
                while reserved_refs:
                    for reserved_path in sorted(reserved_refs):
                        reference = self.model_resolver.get(reserved_path)
                        if not reference or reference.loaded:
                            continue
                        object_paths = reserved_path.split("#/", 1)[-1].split("/")
                        path = reserved_path.split("/")
                        models = get_model_by_path(raw, object_paths)
                        model_name = object_paths[-1]
                        self.parse_obj(model_name, RadSchemaObject.parse_obj(models), path)
                    previous_reserved_refs = reserved_refs
                    reserved_refs = set(self.reserved_refs.get(key) or [])
                    if previous_reserved_refs == reserved_refs:
                        break
