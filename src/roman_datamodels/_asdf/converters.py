"""
The ASDF Converters to handle the serialization/deseialization of the STNode classes to ASDF.
"""
import importlib

from asdf.extension import Converter, ManifestExtension
from asdf.util import uri_match
from astropy.time import Time

from .manifest import MANIFESTS

__all__ = [
    "TaggedObjectNodeConverter",
    "TaggedListNodeConverter",
    "TaggedScalarNodeConverter",
]


class _RomanConverter(Converter):
    def lookup_type(self, tag):
        for tag_pattern in self.tag_pattern_to_type_string:
            if uri_match(tag_pattern, tag):
                type_string = self.tag_pattern_to_type_string[tag_pattern]
                module_name, class_name = type_string.rsplit(".", maxsplit=1)
                return getattr(importlib.import_module(module_name), class_name)

    def select_tag(self, obj, tags, ctx):
        class_ = obj.__class__
        type_string = ".".join((class_.__module__, class_.__name__))
        tag_pattern = self.type_string_to_tag_pattern[type_string]
        for tag in tags:
            if uri_match(tag_pattern, tag):
                return tag
        return obj.tag

    def from_yaml_tree(self, node, tag, ctx):
        instance = self.lookup_type(tag)(node)
        instance._tag = tag
        return instance


class TaggedObjectNodeConverter(_RomanConverter):
    """
    Converter for all subclasses of TaggedObjectNode.
    """

    tags = (
        "asdf://stsci.edu/datamodels/roman/tags/guidewindow-*",
        "asdf://stsci.edu/datamodels/roman/tags/ramp-*",
        "asdf://stsci.edu/datamodels/roman/tags/ramp_fit_output-*",
        "asdf://stsci.edu/datamodels/roman/tags/wfi_science_raw-*",
        "asdf://stsci.edu/datamodels/roman/tags/wfi_image-*",
        "asdf://stsci.edu/datamodels/roman/tags/wfi_mosaic-*",
        "asdf://stsci.edu/datamodels/roman/tags/wfi_mode-*",
        "asdf://stsci.edu/datamodels/roman/tags/exposure-*",
        "asdf://stsci.edu/datamodels/roman/tags/program-*",
        "asdf://stsci.edu/datamodels/roman/tags/observation-*",
        "asdf://stsci.edu/datamodels/roman/tags/ephemeris-*",
        "asdf://stsci.edu/datamodels/roman/tags/visit-*",
        "asdf://stsci.edu/datamodels/roman/tags/photometry-*",
        "asdf://stsci.edu/datamodels/roman/tags/source_detection-*",
        "asdf://stsci.edu/datamodels/roman/tags/coordinates-*",
        "asdf://stsci.edu/datamodels/roman/tags/aperture-*",
        "asdf://stsci.edu/datamodels/roman/tags/pointing-*",
        "asdf://stsci.edu/datamodels/roman/tags/target-*",
        "asdf://stsci.edu/datamodels/roman/tags/velocity_aberration-*",
        "asdf://stsci.edu/datamodels/roman/tags/wcsinfo-*",
        "asdf://stsci.edu/datamodels/roman/tags/guidestar-*",
        "asdf://stsci.edu/datamodels/roman/tags/cal_step-*",
        "asdf://stsci.edu/datamodels/roman/tags/resample-*",
        "asdf://stsci.edu/datamodels/roman/tags/reference_files/dark-*",
        "asdf://stsci.edu/datamodels/roman/tags/reference_files/distortion-*",
        "asdf://stsci.edu/datamodels/roman/tags/reference_files/flat-*",
        "asdf://stsci.edu/datamodels/roman/tags/reference_files/gain-*",
        "asdf://stsci.edu/datamodels/roman/tags/reference_files/inverselinearity-*",
        "asdf://stsci.edu/datamodels/roman/tags/reference_files/ipc-*",
        "asdf://stsci.edu/datamodels/roman/tags/reference_files/linearity-*",
        "asdf://stsci.edu/datamodels/roman/tags/reference_files/mask-*",
        "asdf://stsci.edu/datamodels/roman/tags/reference_files/pixelarea-*",
        "asdf://stsci.edu/datamodels/roman/tags/reference_files/readnoise-*",
        "asdf://stsci.edu/datamodels/roman/tags/reference_files/refpix-*",
        "asdf://stsci.edu/datamodels/roman/tags/reference_files/saturation-*",
        "asdf://stsci.edu/datamodels/roman/tags/reference_files/superbias-*",
        "asdf://stsci.edu/datamodels/roman/tags/reference_files/wfi_img_photom-*",
        "asdf://stsci.edu/datamodels/roman/tags/associations-*",
        "asdf://stsci.edu/datamodels/roman/tags/ref_file-*",
        "asdf://stsci.edu/datamodels/roman/tags/msos_stack-*",
    )

    types = (
        "roman_datamodels.stnode.Guidewindow",
        "roman_datamodels.stnode.Ramp",
        "roman_datamodels.stnode.RampFitOutput",
        "roman_datamodels.stnode.WfiScienceRaw",
        "roman_datamodels.stnode.WfiImage",
        "roman_datamodels.stnode.WfiMosaic",
        "roman_datamodels.stnode.WfiMode",
        "roman_datamodels.stnode.Exposure",
        "roman_datamodels.stnode.Program",
        "roman_datamodels.stnode.Observation",
        "roman_datamodels.stnode.Ephemeris",
        "roman_datamodels.stnode.Visit",
        "roman_datamodels.stnode.Photometry",
        "roman_datamodels.stnode.SourceDetection",
        "roman_datamodels.stnode.Coordinates",
        "roman_datamodels.stnode.Aperture",
        "roman_datamodels.stnode.Pointing",
        "roman_datamodels.stnode.Target",
        "roman_datamodels.stnode.VelocityAberration",
        "roman_datamodels.stnode.Wcsinfo",
        "roman_datamodels.stnode.Guidestar",
        "roman_datamodels.stnode.CalStep",
        "roman_datamodels.stnode.Resample",
        "roman_datamodels.stnode.DarkRef",
        "roman_datamodels.stnode.DistortionRef",
        "roman_datamodels.stnode.FlatRef",
        "roman_datamodels.stnode.GainRef",
        "roman_datamodels.stnode.InverselinearityRef",
        "roman_datamodels.stnode.IpcRef",
        "roman_datamodels.stnode.LinearityRef",
        "roman_datamodels.stnode.MaskRef",
        "roman_datamodels.stnode.PixelareaRef",
        "roman_datamodels.stnode.ReadnoiseRef",
        "roman_datamodels.stnode.RefpixRef",
        "roman_datamodels.stnode.SaturationRef",
        "roman_datamodels.stnode.SuperbiasRef",
        "roman_datamodels.stnode.WfiImgPhotomRef",
        "roman_datamodels.stnode.Associations",
        "roman_datamodels.stnode.RefFile",
        "roman_datamodels.stnode.MsosStack",
    )

    tag_pattern_to_type_string = dict(zip(tags, types))
    type_string_to_tag_pattern = {v: k for k, v in tag_pattern_to_type_string.items()}

    def to_yaml_tree(self, obj, tag, ctx):
        return obj._data


class TaggedListNodeConverter(_RomanConverter):
    """
    Converter for all subclasses of TaggedListNode.
    """

    tags = ("asdf://stsci.edu/datamodels/roman/tags/cal_logs-*",)

    types = ("roman_datamodels.stnode.CalLogs",)

    tag_pattern_to_type_string = dict(zip(tags, types))
    type_string_to_tag_pattern = {v: k for k, v in tag_pattern_to_type_string.items()}

    def to_yaml_tree(self, obj, tag, ctx):
        return list(obj)


class TaggedScalarNodeConverter(_RomanConverter):
    """
    Converter for all subclasses of TaggedScalarNode.
    """

    tags = (
        "asdf://stsci.edu/datamodels/roman/tags/calibration_software_version-*",
        "asdf://stsci.edu/datamodels/roman/tags/filename-*",
        "asdf://stsci.edu/datamodels/roman/tags/file_date-*",
        "asdf://stsci.edu/datamodels/roman/tags/model_type-*",
        "asdf://stsci.edu/datamodels/roman/tags/origin-*",
        "asdf://stsci.edu/datamodels/roman/tags/prd_software_version-*",
        "asdf://stsci.edu/datamodels/roman/tags/sdf_software_version-*",
        "asdf://stsci.edu/datamodels/roman/tags/telescope-*",
    )

    types = (
        "roman_datamodels.stnode.CalibrationSoftwareVersion",
        "roman_datamodels.stnode.Filename",
        "roman_datamodels.stnode.FileDate",
        "roman_datamodels.stnode.ModelType",
        "roman_datamodels.stnode.Origin",
        "roman_datamodels.stnode.PrdSoftwareVersion",
        "roman_datamodels.stnode.SdfSoftwareVersion",
        "roman_datamodels.stnode.Telescope",
    )

    tag_pattern_to_type_string = dict(zip(tags, types))
    type_string_to_tag_pattern = {v: k for k, v in tag_pattern_to_type_string.items()}

    def to_yaml_tree(self, obj, tag, ctx):
        node = obj.__class__.__bases__[0](obj)

        if "file_date" in tag:
            converter = ctx.extension_manager.get_converter_for_type(type(node))
            node = converter.to_yaml_tree(node, tag, ctx)

        return node

    def from_yaml_tree(self, node, tag, ctx):
        if "file_date" in tag:
            converter = ctx.extension_manager.get_converter_for_type(Time)
            node = converter.from_yaml_tree(node, tag, ctx)

        return super().from_yaml_tree(node, tag, ctx)


NODE_CONVERTERS = [TaggedObjectNodeConverter(), TaggedListNodeConverter(), TaggedScalarNodeConverter()]

# Create the ASDF extension for the STNode classes.
NODE_EXTENSIONS = [ManifestExtension.from_uri(manifest["id"], converters=NODE_CONVERTERS) for manifest in MANIFESTS]
