from typing import Any

from asdf.extension import ManifestExtension

from ._tagged import TaggedObjectNode

class AbvegaoffsetRef(TaggedObjectNode):
    _tag_pattern: str

class ApcorrRef(TaggedObjectNode):
    _tag_pattern: str

class DarkdecaysignalRef(TaggedObjectNode):
    _tag_pattern: str

class DarkRef(TaggedObjectNode):
    _tag_pattern: str

class DetectorstatusRef(TaggedObjectNode):
    _tag_pattern: str

class DistortionRef(TaggedObjectNode):
    _tag_pattern: str

class EpsfRef(TaggedObjectNode):
    _tag_pattern: str

class FlatRef(TaggedObjectNode):
    _tag_pattern: str

class ForcedImageSourceCatalog(TaggedObjectNode):
    _tag_pattern: str

class ForcedMosaicSourceCatalog(TaggedObjectNode):
    _tag_pattern: str

class Fps(TaggedObjectNode):
    _tag_pattern: str

class GainRef(TaggedObjectNode):
    _tag_pattern: str

class Guidewindow(TaggedObjectNode):
    _tag_pattern: str

class ImageSourceCatalog(TaggedObjectNode):
    _tag_pattern: str

class IntegralnonlinearityRef(TaggedObjectNode):
    _tag_pattern: str

class InverselinearityRef(TaggedObjectNode):
    _tag_pattern: str

class IpcRef(TaggedObjectNode):
    _tag_pattern: str

class L1DetectorGuidewindow(TaggedObjectNode):
    _tag_pattern: str

class L1FaceGuidewindow(TaggedObjectNode):
    _tag_pattern: str

class LinearityRef(TaggedObjectNode):
    _tag_pattern: str

class MaskRef(TaggedObjectNode):
    _tag_pattern: str

class MatableRef(TaggedObjectNode):
    _tag_pattern: str

class MosaicSegmentationMap(TaggedObjectNode):
    _tag_pattern: str

class MosaicSourceCatalog(TaggedObjectNode):
    _tag_pattern: str

class MsosStack(TaggedObjectNode):
    _tag_pattern: str

class MultibandSegmentationMap(TaggedObjectNode):
    _tag_pattern: str

class MultibandSourceCatalog(TaggedObjectNode):
    _tag_pattern: str

class PixelareaRef(TaggedObjectNode):
    _tag_pattern: str

class Ramp(TaggedObjectNode):
    _tag_pattern: str

class RampFitOutput(TaggedObjectNode):
    _tag_pattern: str

class ReadnoiseRef(TaggedObjectNode):
    _tag_pattern: str

class RefpixRef(TaggedObjectNode):
    _tag_pattern: str

class SaturationRef(TaggedObjectNode):
    _tag_pattern: str

class SegmentationMap(TaggedObjectNode):
    _tag_pattern: str

class SkycellsRef(TaggedObjectNode):
    _tag_pattern: str

class SuperbiasRef(TaggedObjectNode):
    _tag_pattern: str

class Tvac(TaggedObjectNode):
    _tag_pattern: str

class WfiImage(TaggedObjectNode):
    _tag_pattern: str

class WfiImgPhotomRef(TaggedObjectNode):
    _tag_pattern: str

class WfiMosaic(TaggedObjectNode):
    _tag_pattern: str

class WfiScienceRaw(TaggedObjectNode):
    _tag_pattern: str

class WfiWcs(TaggedObjectNode):
    _tag_pattern: str

_MANIFESTS: list[dict[str, Any]]
NODE_EXTENSIONS: dict[str, ManifestExtension]
