from __future__ import annotations

__all__ = ["RomanPydanticExtension"]

import warnings
from typing import Any, ClassVar

from asdf.extension import Converter, Extension
from asdf_astropy.converters.time import TimeConverter
from pydantic import RootModel

from roman_datamodels.core import DataModel

# Import all the models so they get registered
from roman_datamodels.datamodels import _generated

_ROMAN_DATAMODEL_CONVERTER: RomanDataModelConverter | None = None
_ROMAN_ROOTMODEL_CONVERTER: RomanRootModelConverter | None = None
_TIME_CONVERTER = TimeConverter()


class RomanDataModelConverter(Converter):
    """
    Converter to handle RomanDataModel tagged objects

    Class Variables
    ---------------
    _tag_to_model :
        Map from tag uri to model class object
    _removed_tags :
        Tags that can still be read but have been removed from the schemas. These
        are to support reading of old files during the transition period.
    _updated_tags :
        Mapping of old tags to new tags. These are to support reading old files
        written before reorganizing RAD. This is to ease the transition period.
    """

    _tag_to_model: ClassVar[dict[str, type[DataModel]] | None] = None
    _removed_tags: ClassVar[tuple(str)] = (
        "asdf://stsci.edu/datamodels/roman/tags/calibration_software_version-1.0.0",
        "asdf://stsci.edu/datamodels/roman/tags/filename-1.0.0",
        "asdf://stsci.edu/datamodels/roman/tags/file_date-1.0.0",
        "asdf://stsci.edu/datamodels/roman/tags/model_type-1.0.0",
        "asdf://stsci.edu/datamodels/roman/tags/origin-1.0.0",
        "asdf://stsci.edu/datamodels/roman/tags/prd_software_version-1.0.0",
        "asdf://stsci.edu/datamodels/roman/tags/sdf_software_version-1.0.0",
        "asdf://stsci.edu/datamodels/roman/tags/telescope-1.0.0",
        "asdf://stsci.edu/datamodels/roman/tags/source_detection-1.0.0",
        "asdf://stsci.edu/datamodels/roman/tags/resample-1.0.0",
    )
    _updated_tags: ClassVar[dict[str, str]] = {
        "asdf://stsci.edu/datamodels/roman/tags/guidewindow-1.0.0": "asdf://stsci.edu/datamodels/roman/tags/data_products/guidewindow-1.0.0",
        "asdf://stsci.edu/datamodels/roman/tags/ramp-1.0.0": "asdf://stsci.edu/datamodels/roman/tags/data_products/ramp-1.0.0",
        "asdf://stsci.edu/datamodels/roman/tags/ramp_fit_output-1.0.0": "asdf://stsci.edu/datamodels/roman/tags/data_products/ramp_fit_output-1.0.0",
        "asdf://stsci.edu/datamodels/roman/tags/wfi_science_raw-1.0.0": "asdf://stsci.edu/datamodels/roman/tags/data_products/wfi_science_raw-1.0.0",
        "asdf://stsci.edu/datamodels/roman/tags/wfi_image-1.0.0": "asdf://stsci.edu/datamodels/roman/tags/data_products/wfi_image-1.0.0",
        "asdf://stsci.edu/datamodels/roman/tags/wfi_mosaic-1.0.0": "asdf://stsci.edu/datamodels/roman/tags/data_products/wfi_mosaic-1.0.0",
        "asdf://stsci.edu/datamodels/roman/tags/associations-1.0.0": "asdf://stsci.edu/datamodels/roman/tags/data_products/associations-1.0.0",
        "asdf://stsci.edu/datamodels/roman/tags/msos_stack-1.0.0": "asdf://stsci.edu/datamodels/roman/tags/data_products/msos_stack-1.0.0",
    }

    def __init__(self) -> None:
        global _ROMAN_DATAMODEL_CONVERTER

        if _ROMAN_DATAMODEL_CONVERTER is not None:
            _ROMAN_DATAMODEL_CONVERTER = self

        self = _ROMAN_DATAMODEL_CONVERTER

    @classmethod
    def from_registry(cls, registry: dict[str, type[DataModel]]) -> RomanDataModelConverter:
        cls._tag_to_model = registry if cls._tag_to_model is None else {**cls._tag_to_model, **registry}
        return cls()

    @classmethod
    def build_converter(cls) -> RomanDataModelConverter:
        models = {}
        for name in _generated.__all__:
            if issubclass(model := getattr(_generated, name), DataModel) and model.tag_uri is not None:
                models[model.tag_uri] = model

        return cls.from_registry(models)

    @property
    def tags(self) -> tuple(str):
        return tuple(self._tag_to_model.keys()) + self._removed_tags + tuple(self._updated_tags.keys())

    @property
    def types(self) -> tuple(type):
        return tuple(self._tag_to_model.values())

    def select_tag(self, obj: DataModel, tags: Any, ctx: Any) -> str:
        return obj.tag_uri

    def to_yaml_tree(self, obj: DataModel, tag: Any, ctx: Any) -> dict:
        return obj.to_asdf_tree()

    def from_yaml_tree(self, node: Any, tag: Any, ctx: Any) -> DataModel:
        if tag in self._removed_tags:
            warnings.warn(
                f"The tag: {tag} has been removed as a stand alone tag, if this data is written the tag will not be included",
                DeprecationWarning,
            )
            if "file_date" in tag:
                return _TIME_CONVERTER.from_yaml_tree(node, "tag:stsci.edu:asdf/time/time-1.1.0", ctx)

            return node

        if tag in self._updated_tags:
            warnings.warn(
                f"The tag: {tag} has been updated to {self._updated_tags[tag]}, if this data is written the tag will be updated",
                DeprecationWarning,
            )
            tag = self._updated_tags[tag]

        return self._tag_to_model[tag](**node)


class RomanRootModelConverter(Converter):
    """
    Converter for tagged RootModel objects.
        - Currently this is only to support CalLogs
    """

    _tag_to_model: ClassVar[dict[str, type[RootModel]] | None] = None

    def __init__(self) -> None:
        global _ROMAN_ROOTMODEL_CONVERTER

        if _ROMAN_ROOTMODEL_CONVERTER is not None:
            _ROMAN_ROOTMODEL_CONVERTER = self

        self = _ROMAN_ROOTMODEL_CONVERTER

    @classmethod
    def from_registry(cls, registry: dict[str, type[RootModel]]) -> RomanRootModelConverter:
        cls._tag_to_model = registry if cls._tag_to_model is None else {**cls._tag_to_model, **registry}
        return cls()

    @classmethod
    def build_converter(cls) -> RomanRootModelConverter:
        models = {}
        for name in _generated.__all__:
            if (
                issubclass(model := getattr(_generated, name), RootModel)
                and hasattr(model, "tag_uri")
                and model.tag_uri is not None
            ):
                models[model.tag_uri] = model

        return cls.from_registry(models)

    @property
    def tags(self) -> tuple(str):
        return tuple(self._tag_to_model.keys())

    @property
    def types(self) -> tuple(type):
        return tuple(self._tag_to_model.values())

    def select_tag(self, obj: RootModel, tags: Any, ctx: Any) -> str:
        return obj.tag_uri

    def to_yaml_tree(self, obj: RootModel, tag: Any, ctx: Any) -> dict:
        return obj.root

    def from_yaml_tree(self, node: Any, tag: Any, ctx: Any) -> RootModel:
        return self._tag_to_model[tag](node)


class RomanPydanticExtension(Extension):
    extension_uri = "asdf://stsci.edu/datamodels/roman/manifests/datamodels-1.0"
    converters = [
        datamodel_converter := RomanDataModelConverter.build_converter(),
        rootmodel_converter := RomanRootModelConverter.build_converter(),
    ]
    tags = list(datamodel_converter.tags + rootmodel_converter.tags)
