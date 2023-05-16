import sys

if sys.version_info < (3, 11):
    from strenum import StrEnum
else:
    from enum import StrEnum


# TAGGED SCALARS
class Origin(StrEnum):
    STSCI = "STSCI"
    IPAC_SSC = "IPAC/SSC"


class Telescope(StrEnum):
    ROMAN = "ROMAN"


# UNTAGGED SCALARS
class ApertureName(StrEnum):
    WFI_01_FULL = "WFI_01_FULL"
    WFI_02_FULL = "WFI_02_FULL"
    WFI_03_FULL = "WFI_03_FULL"
    WFI_04_FULL = "WFI_04_FULL"
    WFI_05_FULL = "WFI_05_FULL"
    WFI_06_FULL = "WFI_06_FULL"
    WFI_07_FULL = "WFI_07_FULL"
    WFI_08_FULL = "WFI_08_FULL"
    WFI_09_FULL = "WFI_09_FULL"
    WFI_10_FULL = "WFI_10_FULL"
    WFI_11_FULL = "WFI_11_FULL"
    WFI_12_FULL = "WFI_12_FULL"
    WFI_13_FULL = "WFI_13_FULL"
    WFI_14_FULL = "WFI_14_FULL"
    WFI_15_FULL = "WFI_15_FULL"
    WFI_16_FULL = "WFI_16_FULL"
    WFI_17_FULL = "WFI_17_FULL"
    WFI_18_FULL = "WFI_18_FULL"
    BORESIGHT = "BORESIGHT"
    CGI_CEN = "CGI_CEN"
    WFI_CEN = "WFI_CEN"


class CalStepValues(StrEnum):
    NA = "N/A"  # `N/A` is not a valid python name, so we use NA instead
    COMPLETE = "COMPLETE"
    SKIPPED = "SKIPPED"
    INCOMPLETE = "INCOMPLETE"


class ReferenceFrame(StrEnum):
    ICRS = "ICRS"


class EphemerisType(StrEnum):
    DEFINITIVE = "DEFINITIVE"
    PREDICTED = "PREDICTED"


class ExposureType(StrEnum):
    WFI_IMAGE = "WFI_IMAGE"
    WFI_GRISM = "WFI_GRISM"
    WFI_PRISM = "WFI_PRISM"
    WFI_DARK = "WFI_DARK"
    WFI_FLAT = "WFI_FLAT"
    WFI_WFSC = "WFI_WFSC"


class GuidewindowMode(StrEnum):
    WIM_ACQ = "WIM-ACQ"
    WIM_TRACK = "WIM-TRACK"
    WSM_ACQ_1 = "WSM-ACQ-1"
    WSM_ACQ_2 = "WSM-ACQ-2"
    WSM_TRACK = "WSM-TRACK"
    DEFOCUSED_MODERATE = "DEFOCUSED-MODERATE"
    DEFOCUSED_LARGE = "DEFOCUSED-LARGE"


class WfiModeNames(StrEnum):
    WFI = "WFI"


class WfiDetector(StrEnum):
    WFI01 = "WFI01"
    WFI02 = "WFI02"
    WFI03 = "WFI03"
    WFI04 = "WFI04"
    WFI05 = "WFI05"
    WFI06 = "WFI06"
    WFI07 = "WFI07"
    WFI08 = "WFI08"
    WFI09 = "WFI09"
    WFI10 = "WFI10"
    WFI11 = "WFI11"
    WFI12 = "WFI12"
    WFI13 = "WFI13"
    WFI14 = "WFI14"
    WFI15 = "WFI15"
    WFI16 = "WFI16"
    WFI17 = "WFI17"
    WFI18 = "WFI18"


class WfiOpticalElement(StrEnum):
    F062 = "F062"
    F087 = "F087"
    F106 = "F106"
    F129 = "F129"
    F146 = "F146"
    F158 = "F158"
    F184 = "F184"
    F213 = "F213"
    GRISM = "GRISM"
    PRISM = "PRISM"
    DARK = "DARK"


class ObservationSurvey(StrEnum):
    HLS = "HLS"
    EMS = "EMS"
    SN = "SN"
    NA = "N/A"


class TargetType(StrEnum):
    FIXED = "FIXED"
    MOVING = "MOVING"
    GENERIC = "GENERIC"


class SourceType(StrEnum):
    EXTENDED = "EXTENDED"
    POINT = "POINT"
    UNKNOWN = "UNKNOWN"


class EngineeringQuality(StrEnum):
    OK = "OK"
    SUSPECT = "SUSPECT"


class PointingEngdbQuality(StrEnum):
    CALCULATED = "CALCULATED"
    PLANNED = "PLANNED"


class ResampleWeightType(StrEnum):
    EXPTIME = "exptime"
    IVM = "ivm"


class Pedigree(StrEnum):
    GROUND = "GROUND"
    MODEL = "MODEL"
    DUMMY = "DUMMY"
    SIMULATION = "SIMULATION"


class DarkRefType(StrEnum):
    DARK = "DARK"


class DistortionRefType(StrEnum):
    DISTORTION = "DISTORTION"


class FlatRefType(StrEnum):
    FLAT = "FLAT"


class GainRefType(StrEnum):
    GAIN = "GAIN"


class InverseLinearityRefType(StrEnum):
    INVERSE_LINEARITY = "INVERSE_LINEARITY"


class IPCRefType(StrEnum):
    IPC = "IPC"


class LinearityRefType(StrEnum):
    LINEARITY = "LINEARITY"


class MaskRefType(StrEnum):
    MASK = "MASK"


class PixelareaRefType(StrEnum):
    AREA = "AREA"


class ReadnoiseRefType(StrEnum):
    READNOISE = "READNOISE"


class SaturationRefType(StrEnum):
    SATURATION = "SATURATION"


class SuperbiasRefType(StrEnum):
    BIAS = "BIAS"


class WfiPhotomRefType(StrEnum):
    PHOTOM = "PHOTOM"
