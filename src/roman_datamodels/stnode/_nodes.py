from astropy.time import Time

from ._registry import SCALAR_NODE_CLASSES_BY_KEY
from ._tagged import TaggedListNode, TaggedObjectNode, TaggedScalarNode


# define scalars
class CalibrationSoftwareVersion(str, TaggedScalarNode):
    _tag_pattern = "asdf://stsci.edu/datamodels/roman/tags/calibration_software_version-*"


class Filename(str, TaggedScalarNode):
    _tag_pattern = "asdf://stsci.edu/datamodels/roman/tags/filename-*"


class FileDate(Time, TaggedScalarNode):
    _tag_pattern = "asdf://stsci.edu/datamodels/roman/tags/file_date-*"


class ModelType(str, TaggedScalarNode):
    _tag_pattern = "asdf://stsci.edu/datamodels/roman/tags/model_type-*"


class Origin(str, TaggedScalarNode):
    _tag_pattern = "asdf://stsci.edu/datamodels/roman/tags/origin-*"


class PrdSoftwareVersion(str, TaggedScalarNode):
    _tag_pattern = "asdf://stsci.edu/datamodels/roman/tags/prd_software_version-*"


class SdfSoftwareVersion(str, TaggedScalarNode):
    _tag_pattern = "asdf://stsci.edu/datamodels/roman/tags/sdf_software_version-*"


class Telescope(str, TaggedScalarNode):
    _tag_pattern = "asdf://stsci.edu/datamodels/roman/tags/telescope-*"


# these keys are special and cannot be used anywhere as the value
# stored with the key will be converted to the following nodes
SCALAR_NODE_CLASSES_BY_KEY.update(
    {
        "calibration_software_version": CalibrationSoftwareVersion,
        "filename": Filename,
        "file_date": FileDate,
        "model_type": ModelType,
        "origin": Origin,
        "prd_software_version": PrdSoftwareVersion,
        "sdf_software_version": SdfSoftwareVersion,
        "telescope": Telescope,
    }
)


# lnodes
class CalLogs(TaggedListNode):
    _tag_pattern = "asdf://stsci.edu/datamodels/roman/tags/cal_logs-*"


# dnodes
class Guidewindow(TaggedObjectNode):
    _tag_pattern = "asdf://stsci.edu/datamodels/roman/tags/guidewindow-*"


class Ramp(TaggedObjectNode):
    _tag_pattern = "asdf://stsci.edu/datamodels/roman/tags/ramp-*"


class RampFitOutput(TaggedObjectNode):
    _tag_pattern = "asdf://stsci.edu/datamodels/roman/tags/ramp_fit_output-*"


class WfiScienceRaw(TaggedObjectNode):
    _tag_pattern = "asdf://stsci.edu/datamodels/roman/tags/wfi_science_raw-*"


class WfiImage(TaggedObjectNode):
    _tag_pattern = "asdf://stsci.edu/datamodels/roman/tags/wfi_image-*"


class WfiMosaic(TaggedObjectNode):
    _tag_pattern = "asdf://stsci.edu/datamodels/roman/tags/wfi_mosaic-*"


class WfiMode(TaggedObjectNode):
    _GRATING_OPTICAL_ELEMENTS = {"GRISM", "PRISM"}
    _tag_pattern = "asdf://stsci.edu/datamodels/roman/tags/wfi_mode-*"

    @property
    def filter(self):
        if self.optical_element in self._GRATING_OPTICAL_ELEMENTS:
            return None
        else:
            return self.optical_element

    @property
    def grating(self):
        if self.optical_element in self._GRATING_OPTICAL_ELEMENTS:
            return self.optical_element
        else:
            return None


class Exposure(TaggedObjectNode):
    _tag_pattern = "asdf://stsci.edu/datamodels/roman/tags/exposure-*"


class Program(TaggedObjectNode):
    _tag_pattern = "asdf://stsci.edu/datamodels/roman/tags/program-*"


class Observation(TaggedObjectNode):
    _tag_pattern = "asdf://stsci.edu/datamodels/roman/tags/observation-*"


class Ephemeris(TaggedObjectNode):
    _tag_pattern = "asdf://stsci.edu/datamodels/roman/tags/ephemeris-*"


class Visit(TaggedObjectNode):
    _tag_pattern = "asdf://stsci.edu/datamodels/roman/tags/visit-*"


class Photometry(TaggedObjectNode):
    _tag_pattern = "asdf://stsci.edu/datamodels/roman/tags/photometry-*"


class SourceDetection(TaggedObjectNode):
    _tag_pattern = "asdf://stsci.edu/datamodels/roman/tags/source_detection-*"


class Coordinates(TaggedObjectNode):
    _tag_pattern = "asdf://stsci.edu/datamodels/roman/tags/coordinates-*"


class Aperture(TaggedObjectNode):
    _tag_pattern = "asdf://stsci.edu/datamodels/roman/tags/aperture-*"


class Pointing(TaggedObjectNode):
    _tag_pattern = "asdf://stsci.edu/datamodels/roman/tags/pointing-*"


class Target(TaggedObjectNode):
    _tag_pattern = "asdf://stsci.edu/datamodels/roman/tags/target-*"


class VelocityAberration(TaggedObjectNode):
    _tag_pattern = "asdf://stsci.edu/datamodels/roman/tags/velocity_aberration-*"


class Wcsinfo(TaggedObjectNode):
    _tag_pattern = "asdf://stsci.edu/datamodels/roman/tags/wcsinfo-*"


class Guidestar(TaggedObjectNode):
    _tag_pattern = "asdf://stsci.edu/datamodels/roman/tags/guidestar-*"


class CalStep(TaggedObjectNode):
    _tag_pattern = "asdf://stsci.edu/datamodels/roman/tags/cal_step-*"


class Resample(TaggedObjectNode):
    _tag_pattern = "asdf://stsci.edu/datamodels/roman/tags/resample-*"


class DarkRef(TaggedObjectNode):
    _tag_pattern = "asdf://stsci.edu/datamodels/roman/tags/reference_files/dark-*"


class DistortionRef(TaggedObjectNode):
    _tag_pattern = "asdf://stsci.edu/datamodels/roman/tags/reference_files/distortion-*"


class FlatRef(TaggedObjectNode):
    _tag_pattern = "asdf://stsci.edu/datamodels/roman/tags/reference_files/flat-*"


class GainRef(TaggedObjectNode):
    _tag_pattern = "asdf://stsci.edu/datamodels/roman/tags/reference_files/gain-*"


class InverselinearityRef(TaggedObjectNode):
    _tag_pattern = "asdf://stsci.edu/datamodels/roman/tags/reference_files/inverselinearity-*"


class IpcRef(TaggedObjectNode):
    _tag_pattern = "asdf://stsci.edu/datamodels/roman/tags/reference_files/ipc-*"


class LinearityRef(TaggedObjectNode):
    _tag_pattern = "asdf://stsci.edu/datamodels/roman/tags/reference_files/linearity-*"


class MaskRef(TaggedObjectNode):
    _tag_pattern = "asdf://stsci.edu/datamodels/roman/tags/reference_files/mask-*"


class PixelareaRef(TaggedObjectNode):
    _tag_pattern = "asdf://stsci.edu/datamodels/roman/tags/reference_files/pixelarea-*"


class ReadnoiseRef(TaggedObjectNode):
    _tag_pattern = "asdf://stsci.edu/datamodels/roman/tags/reference_files/readnoise-*"


class RefpixRef(TaggedObjectNode):
    _tag_pattern = "asdf://stsci.edu/datamodels/roman/tags/reference_files/refpix-*"


class SaturationRef(TaggedObjectNode):
    _tag_pattern = "asdf://stsci.edu/datamodels/roman/tags/reference_files/saturation-*"


class SuperbiasRef(TaggedObjectNode):
    _tag_pattern = "asdf://stsci.edu/datamodels/roman/tags/reference_files/superbias-*"


class WfiImgPhotomRef(TaggedObjectNode):
    _tag_pattern = "asdf://stsci.edu/datamodels/roman/tags/reference_files/wfi_img_photom-*"


class Associations(TaggedObjectNode):
    _tag_pattern = "asdf://stsci.edu/datamodels/roman/tags/associations-*"


class RefFile(TaggedObjectNode):
    _tag_pattern = "asdf://stsci.edu/datamodels/roman/tags/ref_file-*"


class MsosStack(TaggedObjectNode):
    _tag_pattern = "asdf://stsci.edu/datamodels/roman/tags/msos_stack-*"
