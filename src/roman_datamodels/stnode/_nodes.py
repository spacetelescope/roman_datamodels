from astropy.time import Time

from ._tagged import TaggedListNode, TaggedObjectNode, TaggedScalarNode


# define scalars
class CalibrationSoftwareVersion(str, TaggedScalarNode):
    _tag = "asdf://stsci.edu/datamodels/roman/tags/calibration_software_version-1.0.0"


class Filename(str, TaggedScalarNode):
    _tag = "asdf://stsci.edu/datamodels/roman/tags/filename-1.0.0"


class FileDate(Time, TaggedScalarNode):
    _tag = "asdf://stsci.edu/datamodels/roman/tags/file_date-1.0.0"


class ModelType(str, TaggedScalarNode):
    _tag = "asdf://stsci.edu/datamodels/roman/tags/model_type-1.0.0"


class Origin(str, TaggedScalarNode):
    _tag = "asdf://stsci.edu/datamodels/roman/tags/origin-1.0.0"


class PrdSoftwareVersion(str, TaggedScalarNode):
    _tag = "asdf://stsci.edu/datamodels/roman/tags/prd_software_version-1.0.0"


class SdfSoftwareVersion(str, TaggedScalarNode):
    _tag = "asdf://stsci.edu/datamodels/roman/tags/sdf_software_version-1.0.0"


class Telescope(str, TaggedScalarNode):
    _tag = "asdf://stsci.edu/datamodels/roman/tags/telescope-1.0.0"


# lnodes
class CalLogs(TaggedListNode):
    _tag = "asdf://stsci.edu/datamodels/roman/tags/cal_logs-1.0.0"


# dnodes
class Guidewindow(TaggedObjectNode):
    _tag = "asdf://stsci.edu/datamodels/roman/tags/guidewindow-1.0.0"


class Ramp(TaggedObjectNode):
    _tag = "asdf://stsci.edu/datamodels/roman/tags/ramp-1.0.0"


class RampFitOutput(TaggedObjectNode):
    _tag = "asdf://stsci.edu/datamodels/roman/tags/ramp_fit_output-1.0.0"


class WfiScienceRaw(TaggedObjectNode):
    _tag = "asdf://stsci.edu/datamodels/roman/tags/wfi_science_raw-1.0.0"


class WfiImage(TaggedObjectNode):
    _tag = "asdf://stsci.edu/datamodels/roman/tags/wfi_image-1.0.0"


class WfiMosaic(TaggedObjectNode):
    _tag = "asdf://stsci.edu/datamodels/roman/tags/wfi_mosaic-1.0.0"


class WfiMode(TaggedObjectNode):
    _GRATING_OPTICAL_ELEMENTS = {"GRISM", "PRISM"}
    _tag = "asdf://stsci.edu/datamodels/roman/tags/wfi_mode-1.0.0"

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
    _tag = "asdf://stsci.edu/datamodels/roman/tags/exposure-1.0.0"


class Program(TaggedObjectNode):
    _tag = "asdf://stsci.edu/datamodels/roman/tags/program-1.0.0"


class Observation(TaggedObjectNode):
    _tag = "asdf://stsci.edu/datamodels/roman/tags/observation-1.0.0"


class Ephemeris(TaggedObjectNode):
    _tag = "asdf://stsci.edu/datamodels/roman/tags/ephemeris-1.0.0"


class Visit(TaggedObjectNode):
    _tag = "asdf://stsci.edu/datamodels/roman/tags/visit-1.0.0"


class Photometry(TaggedObjectNode):
    _tag = "asdf://stsci.edu/datamodels/roman/tags/photometry-1.0.0"


class SourceDetection(TaggedObjectNode):
    _tag = "asdf://stsci.edu/datamodels/roman/tags/source_detection-1.0.0"


class Coordinates(TaggedObjectNode):
    _tag = "asdf://stsci.edu/datamodels/roman/tags/coordinates-1.0.0"


class Aperture(TaggedObjectNode):
    _tag = "asdf://stsci.edu/datamodels/roman/tags/aperture-1.0.0"


class Pointing(TaggedObjectNode):
    _tag = "asdf://stsci.edu/datamodels/roman/tags/pointing-1.0.0"


class Target(TaggedObjectNode):
    _tag = "asdf://stsci.edu/datamodels/roman/tags/target-1.0.0"


class VelocityAberration(TaggedObjectNode):
    _tag = "asdf://stsci.edu/datamodels/roman/tags/velocity_aberration-1.0.0"


class Wcsinfo(TaggedObjectNode):
    _tag = "asdf://stsci.edu/datamodels/roman/tags/wcsinfo-1.0.0"


class Guidestar(TaggedObjectNode):
    _tag = "asdf://stsci.edu/datamodels/roman/tags/guidestar-1.0.0"


class CalStep(TaggedObjectNode):
    _tag = "asdf://stsci.edu/datamodels/roman/tags/cal_step-1.0.0"


class Resample(TaggedObjectNode):
    _tag = "asdf://stsci.edu/datamodels/roman/tags/resample-1.0.0"


class DarkRef(TaggedObjectNode):
    _tag = "asdf://stsci.edu/datamodels/roman/tags/reference_files/dark-1.0.0"


class DistortionRef(TaggedObjectNode):
    _tag = "asdf://stsci.edu/datamodels/roman/tags/reference_files/distortion-1.0.0"


class FlatRef(TaggedObjectNode):
    _tag = "asdf://stsci.edu/datamodels/roman/tags/reference_files/flat-1.0.0"


class GainRef(TaggedObjectNode):
    _tag = "asdf://stsci.edu/datamodels/roman/tags/reference_files/gain-1.0.0"


class InverselinearityRef(TaggedObjectNode):
    _tag = "asdf://stsci.edu/datamodels/roman/tags/reference_files/inverselinearity-1.0.0"


class IpcRef(TaggedObjectNode):
    _tag = "asdf://stsci.edu/datamodels/roman/tags/reference_files/ipc-1.0.0"


class LinearityRef(TaggedObjectNode):
    _tag = "asdf://stsci.edu/datamodels/roman/tags/reference_files/linearity-1.0.0"


class MaskRef(TaggedObjectNode):
    _tag = "asdf://stsci.edu/datamodels/roman/tags/reference_files/mask-1.0.0"


class PixelareaRef(TaggedObjectNode):
    _tag = "asdf://stsci.edu/datamodels/roman/tags/reference_files/pixelarea-1.0.0"


class ReadnoiseRef(TaggedObjectNode):
    _tag = "asdf://stsci.edu/datamodels/roman/tags/reference_files/readnoise-1.0.0"


class RefpixRef(TaggedObjectNode):
    _tag = "asdf://stsci.edu/datamodels/roman/tags/reference_files/refpix-1.0.0"


class SaturationRef(TaggedObjectNode):
    _tag = "asdf://stsci.edu/datamodels/roman/tags/reference_files/saturation-1.0.0"


class SuperbiasRef(TaggedObjectNode):
    _tag = "asdf://stsci.edu/datamodels/roman/tags/reference_files/superbias-1.0.0"


class WfiImgPhotomRef(TaggedObjectNode):
    _tag = "asdf://stsci.edu/datamodels/roman/tags/reference_files/wfi_img_photom-1.0.0"


class Associations(TaggedObjectNode):
    _tag = "asdf://stsci.edu/datamodels/roman/tags/associations-1.0.0"


class RefFile(TaggedObjectNode):
    _tag = "asdf://stsci.edu/datamodels/roman/tags/ref_file-1.0.0"


class MsosStack(TaggedObjectNode):
    _tag = "asdf://stsci.edu/datamodels/roman/tags/msos_stack-1.0.0"
