"""
The ASDF Converters to handle the serialization/deseialization of the STNode classes to ASDF.
"""
from asdf.extension import Converter, ManifestExtension
from astropy.time import Time

from roman_datamodels.stnode._registry import LIST_NODE_CLASSES_BY_TAG, OBJECT_NODE_CLASSES_BY_TAG, SCALAR_NODE_CLASSES_BY_TAG

from .manifest import MANIFESTS

__all__ = [
    "TaggedObjectNodeConverter",
    "TaggedListNodeConverter",
    "TaggedScalarNodeConverter",
]


class TaggedObjectNodeConverter(Converter):
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

    @property
    def tags(self):
        return list(OBJECT_NODE_CLASSES_BY_TAG.keys())

    @property
    def types(self):
        return list(OBJECT_NODE_CLASSES_BY_TAG.values())

    def select_tag(self, obj, tags, ctx):
        return obj.tag

    def to_yaml_tree(self, obj, tag, ctx):
        return obj._data

    def from_yaml_tree(self, node, tag, ctx):
        return OBJECT_NODE_CLASSES_BY_TAG[tag](node)


class TaggedListNodeConverter(Converter):
    """
    Converter for all subclasses of TaggedListNode.
    """

    tags = ("asdf://stsci.edu/datamodels/roman/tags/cal_logs-*",)

    types = ("roman_datamodels.stnode.CalLogs",)

    def select_tag(self, obj, tags, ctx):
        return obj.tag

    def to_yaml_tree(self, obj, tag, ctx):
        return list(obj)

    def from_yaml_tree(self, node, tag, ctx):
        return LIST_NODE_CLASSES_BY_TAG[tag](node)


class TaggedScalarNodeConverter(Converter):
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

    def select_tag(self, obj, tags, ctx):
        return obj.tag

    def to_yaml_tree(self, obj, tag, ctx):
        from roman_datamodels.stnode._nodes import FileDate

        node = obj.__class__.__bases__[0](obj)

        if tag == FileDate._tag:
            converter = ctx.extension_manager.get_converter_for_type(type(node))
            node = converter.to_yaml_tree(node, tag, ctx)

        return node

    def from_yaml_tree(self, node, tag, ctx):
        from roman_datamodels.stnode._nodes import FileDate

        if tag == FileDate._tag:
            converter = ctx.extension_manager.get_converter_for_type(Time)
            node = converter.from_yaml_tree(node, tag, ctx)

        return SCALAR_NODE_CLASSES_BY_TAG[tag](node)


NODE_CONVERTERS = [TaggedObjectNodeConverter(), TaggedListNodeConverter(), TaggedScalarNodeConverter()]

# Create the ASDF extension for the STNode classes.
NODE_EXTENSIONS = [ManifestExtension.from_uri(manifest["id"], converters=NODE_CONVERTERS) for manifest in MANIFESTS]
