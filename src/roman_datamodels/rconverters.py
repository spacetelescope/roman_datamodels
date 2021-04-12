"""
This module holds all the converters for roman datamodels
"""
from .stnode import (TaggedObjectNode, TaggedObjectNodeConverter,
                    TaggedListNode, #TaggedListNodeConverter,
)

class WfiScienceRaw(TaggedObjectNode):
    _tag = "tag:stsci.edu:datamodels/roman/wfi_science_raw-1.0.0"

class WfiScienceRawConverter(TaggedObjectNodeConverter):
    tags = ["tag:stsci.edu:datamodels/roman/wfi_science_raw-*"]
    types = ["roman_datamodels.rconverters.WfiScienceRaw"]

    def to_yaml_tree(self, obj, tags, ctx):
        return obj._data

    def from_yaml_tree(self, node, tag, ctx):
        return WfiScienceRaw(node)

class WfiImage(TaggedObjectNode):
    _tag = "tag:stsci.edu:datamodels/roman/wfi_image-1.0.0"

class WfiImageConverter(TaggedObjectNodeConverter):
    tags = ["tag:stsci.edu:datamodels/roman/wfi_image-*"]
    types = ["roman_datamodels.rconverters.WfiImage"]

    def to_yaml_tree(self, obj, tags, ctx):
        return obj._data

    def from_yaml_tree(self, node, tag, ctx):
        return WfiImage(node)

class WfiMode(TaggedObjectNode):
    _tag = "tag:stsci.edu:datamodels/roman/wfi_mode-1.0.0"

class WfiModeConverter(TaggedObjectNodeConverter):
    tags = ["tag:stsci.edu:datamodels/roman/wfi_mode-*"]
    types = ["roman_datamodels.rconverters.WfiMode"]

    def to_yaml_tree(self, obj, tags, ctx):
        return obj._data

    def from_yaml_tree(self, node, tag, ctx):
        return WfiMode(node)

class Exposure(TaggedObjectNode):
    _tag = "tag:stsci.edu:datamodels/roman/exposure-1.0.0"

class ExposureConverter(TaggedObjectNodeConverter):
    tags = ["tag:stsci.edu:datamodels/roman/exposure-*"]
    types = ["roman_datamodels.rconverters.Exposure"]

    def to_yaml_tree(self, obj, tags, ctx):
        return obj._data

    def from_yaml_tree(self, node, tag, ctx):
        return Exposure(node)

class Wfi(TaggedObjectNode):
    _tag = "tag:stsci.edu:datamodels/roman/wfi-1.0.0"

class WfiConverter(TaggedObjectNodeConverter):
    tags = ["tag:stsci.edu:datamodels/roman/wfi-*"]
    types = ["roman_datamodels.rconverters.Wfi"]

    def to_yaml_tree(self, obj, tags, ctx):
        return obj._data

    def from_yaml_tree(self, node, tag, ctx):
        return Wfi(node)

class Program(TaggedObjectNode):
    _tag = "tag:stsci.edu:datamodels/roman/program-1.0.0"

class ProgramConverter(TaggedObjectNodeConverter):
    tags = ["tag:stsci.edu:datamodels/roman/program-*"]
    types = ["roman_datamodels.rconverters.Program"]

    def to_yaml_tree(self, obj, tags, ctx):
        return obj._data

    def from_yaml_tree(self, node, tag, ctx):
        return Program(node)

class Observation(TaggedObjectNode):
    _tag = "tag:stsci.edu:datamodels/roman/observation-1.0.0"

class ObservationConverter(TaggedObjectNodeConverter):
    tags = ["tag:stsci.edu:datamodels/roman/observation-*"]
    types = ["roman_datamodels.rconverters.Observation"]

    def to_yaml_tree(self, obj, tags, ctx):
        return obj._data

    def from_yaml_tree(self, node, tag, ctx):
        return Observation(node)

class Ephemeris(TaggedObjectNode):
    _tag = "tag:stsci.edu:datamodels/roman/ephemeris-1.0.0"

class EphemerisConverter(TaggedObjectNodeConverter):
    tags = ["tag:stsci.edu:datamodels/roman/ephemeris-*"]
    types = ["roman_datamodels.rconverters.Ephemeris"]

    def to_yaml_tree(self, obj, tags, ctx):
        return obj._data

    def from_yaml_tree(self, node, tag, ctx):
        return Ephemeris(node)

class Visit(TaggedObjectNode):
    _tag = "tag:stsci.edu:datamodels/roman/visit-1.0.0"

class VisitConverter(TaggedObjectNodeConverter):
    tags = ["tag:stsci.edu:datamodels/roman/visit-*"]
    types = ["roman_datamodels.rconverters.Visit"]

    def to_yaml_tree(self, obj, tags, ctx):
        return obj._data

    def from_yaml_tree(self, node, tag, ctx):
        return Visit(node)

class Photometry(TaggedObjectNode):
    _tag = "tag:stsci.edu:datamodels/roman/photometry-1.0.0"

class PhotometryConverter(TaggedObjectNodeConverter):
    tags = ["tag:stsci.edu:datamodels/roman/photometry-*"]
    types = ["roman_datamodels.rconverters.Photometry"]

    def to_yaml_tree(self, obj, tags, ctx):
        return obj._data

    def from_yaml_tree(self, node, tag, ctx):
        return Photometry(node)

class Coordinates(TaggedObjectNode):
    _tag = "tag:stsci.edu:datamodels/roman/coordinates-1.0.0"

class CoordinatesConverter(TaggedObjectNodeConverter):
    tags = ["tag:stsci.edu:datamodels/roman/coordinates-*"]
    types = ["roman_datamodels.rconverters.Coordinates"]

    def to_yaml_tree(self, obj, tags, ctx):
        return obj._data

    def from_yaml_tree(self, node, tag, ctx):
        return Coordinates(node)

class Aperture(TaggedObjectNode):
    _tag = "tag:stsci.edu:datamodels/roman/aperture-1.0.0"

class ApertureConverter(TaggedObjectNodeConverter):
    tags = ["tag:stsci.edu:datamodels/roman/aperture-*"]
    types = ["roman_datamodels.rconverters.Aperture"]

    def to_yaml_tree(self, obj, tags, ctx):
        return obj._data

    def from_yaml_tree(self, node, tag, ctx):
        return Aperture(node)

class Pointing(TaggedObjectNode):
    _tag = "tag:stsci.edu:datamodels/roman/pointing-1.0.0"

class PointingConverter(TaggedObjectNodeConverter):
    tags = ["tag:stsci.edu:datamodels/roman/pointing-*"]
    types = ["roman_datamodels.rconverters.Pointing"]

    def to_yaml_tree(self, obj, tags, ctx):
        return obj._data

    def from_yaml_tree(self, node, tag, ctx):
        return Pointing(node)

class Target(TaggedObjectNode):
    _tag = "tag:stsci.edu:datamodels/roman/target-1.0.0"

class TargetConverter(TaggedObjectNodeConverter):
    tags = ["tag:stsci.edu:datamodels/roman/target-*"]
    types = ["roman_datamodels.rconverters.Target"]

    def to_yaml_tree(self, obj, tags, ctx):
        return obj._data

    def from_yaml_tree(self, node, tag, ctx):
        return Target(node)

class VelocityAberration(TaggedObjectNode):
    _tag = "tag:stsci.edu:datamodels/roman/velocity_aberration-1.0.0"

class VelocityAberrationConverter(TaggedObjectNodeConverter):
    tags = ["tag:stsci.edu:datamodels/roman/velocity_aberration-*"]
    types = ["roman_datamodels.rconverters.VelocityAberration"]

    def to_yaml_tree(self, obj, tags, ctx):
        return obj._data

    def from_yaml_tree(self, node, tag, ctx):
        return VelocityAberration(node)

class Wcsinfo(TaggedObjectNode):
    _tag = "tag:stsci.edu:datamodels/roman/wcsinfo-1.0.0"

class WcsinfoConverter(TaggedObjectNodeConverter):
    tags = ["tag:stsci.edu:datamodels/roman/wcsinfo-*"]
    types = ["roman_datamodels.rconverters.Wcsinfo"]

    def to_yaml_tree(self, obj, tags, ctx):
        return obj._data

    def from_yaml_tree(self, node, tag, ctx):
        return Wcsinfo(node)

class Guidestar(TaggedObjectNode):
    _tag = "tag:stsci.edu:datamodels/roman/guidestar-1.0.0"

class GuidestarConverter(TaggedObjectNodeConverter):
    tags = ["tag:stsci.edu:datamodels/roman/guidestar-*"]
    types = ["roman_datamodels.rconverters.Guidestar"]

    def to_yaml_tree(self, obj, tags, ctx):
        return obj._data

    def from_yaml_tree(self, node, tag, ctx):
        return Guidestar(node)

class Program(TaggedObjectNode):
    _tag = "tag:stsci.edu:datamodels/roman/program-1.0.0"

class ProgramConverter(TaggedObjectNodeConverter):
    tags = ["tag:stsci.edu:datamodels/roman/program-*"]
    types = ["roman_datamodels.rconverters.Program"]

    def to_yaml_tree(self, obj, tags, ctx):
        return obj._data

    def from_yaml_tree(self, node, tag, ctx):
        return Program(node)

class CalStep(TaggedObjectNode):
    _tag = "tag:stsci.edu:datamodels/roman/cal_step-1.0.0"

class CalStepConverter(TaggedObjectNodeConverter):
    tags = ["tag:stsci.edu:datamodels/roman/cal_step-*"]
    types = ["roman_datamodels.rconverters.CalStep"]

    def to_yaml_tree(self, obj, tags, ctx):
        return obj._data

    def from_yaml_tree(self, node, tag, ctx):
        return CalStep(node)

class FlatRef(TaggedObjectNode):
    _tag = "tag:stsci.edu:datamodels/roman/reference_files/flat-1.0.0"

class FlatRefConverter(TaggedObjectNodeConverter):
    tags = ["tag:stsci.edu:datamodels/roman/reference_files/flat-*"]
    types = ["roman_datamodels.rconverters.FlatRef"]

    def to_yaml_tree(self, obj, tags, ctx):
        return obj._data

    def from_yaml_tree(self, node, tag, ctx):
        return FlatRef(node)

