from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, DefaultDict, Iterable, Mapping, Sequence
from urllib.parse import ParseResult

from datamodel_code_generator.format import PythonVersion
from datamodel_code_generator.model import DataModel, DataModelFieldBase
from datamodel_code_generator.model import pydantic as pydantic_model
from datamodel_code_generator.parser import DefaultPutDict, LiteralType
from datamodel_code_generator.parser.base import get_special_path
from datamodel_code_generator.parser.jsonschema import JsonSchemaParser, get_model_by_path
from datamodel_code_generator.types import DataType, DataTypeManager, StrictTypes

from roman_datamodels.pydantic.adaptors import adaptor_factory, has_adaptor

from ._reslover import RadModelResolver
from ._schema import RadSchemaObject

__all__ = ["RadSchemaParser"]


class RadSchemaParser(JsonSchemaParser):
    """Modifications to the JsonSchemaParser to support Rad schemas"""

    def __init__(
        self,
        source: str | Path | list[Path] | ParseResult,
        *,
        data_model_type: type[DataModel] = pydantic_model.BaseModel,
        data_model_root_type: type[DataModel] = pydantic_model.CustomRootType,
        data_type_manager_type: type[DataTypeManager] = pydantic_model.DataTypeManager,
        data_model_field_type: type[DataModelFieldBase] = pydantic_model.DataModelField,
        base_class: str | None = None,
        additional_imports: list[str] | None = None,
        custom_template_dir: Path | None = None,
        extra_template_data: DefaultDict[str, dict[str, Any]] | None = None,
        target_python_version: PythonVersion = PythonVersion.PY_37,
        dump_resolve_reference_action: Callable[[Iterable[str]], str] | None = None,
        validation: bool = False,
        field_constraints: bool = False,
        snake_case_field: bool = False,
        strip_default_none: bool = False,
        aliases: Mapping[str, str] | None = None,
        allow_population_by_field_name: bool = False,
        apply_default_values_for_required_fields: bool = False,
        allow_extra_fields: bool = False,
        force_optional_for_required_fields: bool = False,
        class_name: str | None = None,
        use_standard_collections: bool = False,
        base_path: Path | None = None,
        use_schema_description: bool = False,
        use_field_description: bool = False,
        use_default_kwarg: bool = False,
        reuse_model: bool = False,
        encoding: str = "utf-8",
        enum_field_as_literal: LiteralType | None = None,
        use_one_literal_as_default: bool = False,
        set_default_enum_member: bool = False,
        use_subclass_enum: bool = False,
        strict_nullable: bool = False,
        use_generic_container_types: bool = False,
        enable_faux_immutability: bool = False,
        remote_text_cache: DefaultPutDict[str, str] | None = None,
        disable_appending_item_suffix: bool = False,
        strict_types: Sequence[StrictTypes] | None = None,
        empty_enum_field_name: str | None = None,
        field_extra_keys: set[str] | None = None,
        field_include_all_keys: bool = False,
        field_extra_keys_without_x_prefix: set[str] | None = None,
        wrap_string_literal: bool | None = None,
        use_title_as_name: bool = False,
        use_operation_id_as_name: bool = False,
        use_unique_items_as_set: bool = False,
        http_headers: Sequence[tuple[str, str]] | None = None,
        http_ignore_tls: bool = False,
        use_annotated: bool = False,
        use_non_positive_negative_number_constrained_types: bool = False,
        original_field_name_delimiter: str | None = None,
        use_double_quotes: bool = False,
        use_union_operator: bool = False,
        allow_responses_without_content: bool = False,
        collapse_root_models: bool = False,
        special_field_name_prefix: str | None = None,
        remove_special_field_name_prefix: bool = False,
        capitalise_enum_members: bool = False,
        keep_model_order: bool = False,
        known_third_party: list[str] | None = None,
        custom_formatters: list[str] | None = None,
        custom_formatters_kwargs: dict[str, Any] | None = None,
    ) -> None:
        """
        Note this exactly replcates the JsonSchemaParser constructor, but with the
        custom_class_name_generator argument removed.

        This is done so we can override the custom_class_name_generator argument with
        our own default and pass the correct inputs to the model_resolver constructor
        in order to override it with our own custom implementation.
        """
        custom_class_name_generator: Callable[[str], str] | None = class_name_generator
        super().__init__(
            source=source,
            data_model_type=data_model_type,
            data_model_root_type=data_model_root_type,
            data_type_manager_type=data_type_manager_type,
            data_model_field_type=data_model_field_type,
            base_class=base_class,
            additional_imports=additional_imports,
            custom_template_dir=custom_template_dir,
            extra_template_data=extra_template_data,
            target_python_version=target_python_version,
            dump_resolve_reference_action=dump_resolve_reference_action,
            validation=validation,
            field_constraints=field_constraints,
            snake_case_field=snake_case_field,
            strip_default_none=strip_default_none,
            aliases=aliases,
            allow_population_by_field_name=allow_population_by_field_name,
            apply_default_values_for_required_fields=apply_default_values_for_required_fields,
            allow_extra_fields=allow_extra_fields,
            force_optional_for_required_fields=force_optional_for_required_fields,
            class_name=class_name,
            use_standard_collections=use_standard_collections,
            base_path=base_path,
            use_schema_description=use_schema_description,
            use_field_description=use_field_description,
            use_default_kwarg=use_default_kwarg,
            reuse_model=reuse_model,
            encoding=encoding,
            enum_field_as_literal=enum_field_as_literal,
            use_one_literal_as_default=use_one_literal_as_default,
            set_default_enum_member=set_default_enum_member,
            use_subclass_enum=use_subclass_enum,
            strict_nullable=strict_nullable,
            use_generic_container_types=use_generic_container_types,
            enable_faux_immutability=enable_faux_immutability,
            remote_text_cache=remote_text_cache,
            disable_appending_item_suffix=disable_appending_item_suffix,
            strict_types=strict_types,
            empty_enum_field_name=empty_enum_field_name,
            custom_class_name_generator=custom_class_name_generator,
            field_extra_keys=field_extra_keys,
            field_include_all_keys=field_include_all_keys,
            field_extra_keys_without_x_prefix=field_extra_keys_without_x_prefix,
            wrap_string_literal=wrap_string_literal,
            use_title_as_name=use_title_as_name,
            use_operation_id_as_name=use_operation_id_as_name,
            use_unique_items_as_set=use_unique_items_as_set,
            http_headers=http_headers,
            http_ignore_tls=http_ignore_tls,
            use_annotated=use_annotated,
            use_non_positive_negative_number_constrained_types=use_non_positive_negative_number_constrained_types,
            original_field_name_delimiter=original_field_name_delimiter,
            use_double_quotes=use_double_quotes,
            use_union_operator=use_union_operator,
            allow_responses_without_content=allow_responses_without_content,
            collapse_root_models=collapse_root_models,
            special_field_name_prefix=special_field_name_prefix,
            remove_special_field_name_prefix=remove_special_field_name_prefix,
            capitalise_enum_members=capitalise_enum_members,
            keep_model_order=keep_model_order,
            known_third_party=known_third_party,
            custom_formatters=custom_formatters,
            custom_formatters_kwargs=custom_formatters_kwargs,
        )
        self.model_resolver = RadModelResolver(
            base_url=self.model_resolver.base_url,
            singular_name_suffix=self.model_resolver.singular_name_suffix,
            aliases=aliases,
            empty_field_name=empty_enum_field_name,
            snake_case_field=snake_case_field,
            custom_class_name_generator=custom_class_name_generator,
            base_path=self.base_path,
            original_field_name_delimiter=original_field_name_delimiter,
            special_field_name_prefix=special_field_name_prefix,
            remove_special_field_name_prefix=remove_special_field_name_prefix,
            capitalise_enum_members=capitalise_enum_members,
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
        if obj.title:
            self.extra_template_data[name]["title"] = obj.title

        if obj.tag_uri:
            self.extra_template_data[name]["tag_uri"] = obj.tag_uri

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
        # self._current_source_path = value

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


def remove_uri_version(uri):
    """
    Remove the version from the uri, this is helpful because the version number forces
    module names to not be valid python module names, and we don't need the version
    for the models anyway.
    """
    return uri.split("-")[0]


def class_name_from_uri(uri):
    """Turn the uri/id into a valid python class name"""

    uri = remove_uri_version(uri)

    class_name = "".join([p.capitalize() for p in uri.split("/")[-1].split("_")])
    if uri.startswith("asdf://stsci.edu/datamodels/roman/schemas/reference_files/"):
        class_name += "Ref"

    return class_name


def class_name_generator(name: str) -> str:
    """Identity function to supersede the default class name generator"""
    return name
