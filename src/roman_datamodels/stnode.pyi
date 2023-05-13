import typing as T

if T.TYPE_CHECKING:
    from astropy.modeling import Model  # type: ignore
    from astropy.time import Time  # type: ignore
    from astropy.units import Quantity  # type: ignore
    from numpy import ndarray  # type: ignore

    from roman_datamodels import stnode  # type: ignore

_OptionalQuantity = Quantity | None

class _ndarray_uint8(ndarray):
    pass

class _ndarray_uint8_3D(_ndarray_uint8):
    pass

class _ndarray_uint16(ndarray):
    pass

class _ndarray_uint16_2D(_ndarray_uint16):
    pass

class _ndarray_uint16_3D(_ndarray_uint16):
    pass

class _ndarray_uint32(ndarray):
    pass

class _ndarray_uint32_2D(_ndarray_uint32):
    pass

class _ndarray_float32(ndarray):
    pass

class _ndarray_float32_2D(_ndarray_float32):
    pass

class _ndarray_float32_3D(_ndarray_float32):
    pass

class _Quantity_float32(Quantity):
    pass

class _Quantity_float32_electron(_Quantity_float32):
    pass

class _Quantity_float32_electron_2D(_Quantity_float32_electron):
    pass

class _Quantity_float32_electron_3D(_Quantity_float32_electron):
    pass

class _Quantity_float32_electron_DN(_Quantity_float32):
    pass

class _Quantity_float32_electron_DN_2D(_Quantity_float32_electron_DN):
    pass

class _Quantity_float32_electron_s(_Quantity_float32):
    pass

class _Quantity_float32_electron_s_2D(_Quantity_float32_electron_s):
    pass

class _Quantity_float32_electron_s_3D(_Quantity_float32_electron_s):
    pass

class _Quantity_float32_electron2_s2(_Quantity_float32):
    pass

class _Quantity_float32_electron2_s2_2D(_Quantity_float32_electron2_s2):
    pass

class _Quantity_float32_electron2_s2_3D(_Quantity_float32_electron2_s2):
    pass

class _Quantity_float32_DN(_Quantity_float32):
    pass

class _Quantity_float32_DN_2D(_Quantity_float32_DN):
    pass

class _Quantity_float32_DN_3D(_Quantity_float32_DN):
    pass

class _Quantity_uint16(Quantity):
    pass

class _Quantity_uint16_DN(_Quantity_uint16):
    pass

class _Quantity_uint16_DN_3D(_Quantity_uint16):
    pass

class _Quantity_uint16_DN_5D(_Quantity_uint16_DN):
    pass

_GwMode = T.Literal[
    "WIM-ACQ",
    "WIM-TRACK",
    "WSM-ACQ-1",
    "WSM-ACQ-2",
    "WSM-TRACK",
    "DEFOCUSED-MODERATE",
    "DEFOCUSED-LARGE",
]

class FileDate(stnode.TaggedScalarNode, Time):
    pass

class CalibrationSoftwareVersion(stnode.TaggedScalarNode, str):
    pass

class Filename(stnode.TaggedScalarNode, str):
    pass

class ModelType(stnode.TaggedScalarNode, str):
    pass

_Origin = T.Literal["STSCI", "IPAC/SSC"]

class Origin(stnode.TaggedScalarNode, _Origin):
    pass

class PrdSoftwareVersion(stnode.TaggedScalarNode, str):
    pass

class SdfSoftwareVersion(stnode.TaggedScalarNode, str):
    pass

_Telescope = T.Literal["ROMAN"]

class Telescope(stnode.TaggedScalarNode, _Telescope):
    pass

class _Basic(stnode.DNode):
    calibration_software_version: CalibrationSoftwareVersion
    filename: Filename
    file_date: FileDate
    model_type: ModelType
    origin: Origin
    prd_software_version: PrdSoftwareVersion
    sdf_software_version: SdfSoftwareVersion
    telescope: Telescope

_ApertureName = T.Literal[
    "WFI_01_FULL",
    "WFI_02_FULL",
    "WFI_03_FULL",
    "WFI_04_FULL",
    "WFI_05_FULL",
    "WFI_06_FULL",
    "WFI_07_FULL",
    "WFI_08_FULL",
    "WFI_09_FULL",
    "WFI_10_FULL",
    "WFI_11_FULL",
    "WFI_12_FULL",
    "WFI_13_FULL",
    "WFI_14_FULL",
    "WFI_15_FULL",
    "WFI_16_FULL",
    "WFI_17_FULL",
    "WFI_18_FULL",
    "BORESIGHT",
    "CGI_CEN",
    "WFI_CEN",
]

class Aperture(stnode.TaggedObjectNode):
    name: _ApertureName
    position_angle: float

_CalStepVal = T.Literal["N/A", "COMPLETE", "SKIPPED", "INCOMPLETE"]

class CalStep(stnode.TaggedObjectNode):
    assign_wcs: _CalStepVal
    flat_field: _CalStepVal
    dark: _CalStepVal
    dq_init: _CalStepVal
    jump: _CalStepVal
    linearity: _CalStepVal
    photom: _CalStepVal
    source_detection: _CalStepVal
    ramp_fit: _CalStepVal
    saturation: _CalStepVal

_ReferenceFrame = T.Literal["ICRS"]

class Coordinates(stnode.TaggedObjectNode):
    reference_frame: _ReferenceFrame

_EphemerisType = T.Literal["DEFINITIVE", "PREDICTED"]

class Ephemeris(stnode.TaggedObjectNode):
    earth_angle: float
    moon_angle: float
    ephemeris_reference_frame: str
    sun_angle: float
    type: _EphemerisType
    time: float
    spatial_x: float
    spatial_y: float
    spatial_z: float
    velocity_x: float
    velocity_y: float
    velocity_z: float

_ExposureType = T.Literal[
    "WFI_IMAGE",
    "WFI_GRISM",
    "WFI_PRISM",
    "WFI_DARK",
    "WFI_FLAT",
    "WFI_WFSC",
]

class Exposure(stnode.TaggedObjectNode):
    id: int
    type: _ExposureType
    start_time: Time
    mid_time: Time
    end_time: Time
    start_time_mjd: float
    mid_time_mjd: float
    end_time_mjd: float
    start_time_tdb: float
    mid_time_tdb: float
    end_time_tdb: float
    ngroups: int
    nframes: int
    data_problem: bool
    sca_number: int
    gain_factor: float
    integration_time: float
    elapsed_exposure_time: float
    frame_divisor: int
    groupgap: int
    frame_time: float
    group_time: float
    exposure_time: float
    effective_exposure_time: float
    duration: float
    ma_table_name: str
    ma_table_number: float
    level0_compressed: bool
    read_pattern: stnode.LNode[stnode.LNode[int]]

class Guidestar(stnode.TaggedObjectNode):
    gw_id: str
    gw_fgs_mode: _GwMode
    gw_science_file_source: str
    gs_id: str
    gs_catalog_version: str
    gs_ra: float
    gs_dec: float
    gs_ura: float
    gs_udec: float
    gs_mag: float
    gs_umag: float
    data_start: float
    data_end: float
    gs_ctd_x: float
    gs_ctd_y: float
    gs_ctd_ux: float
    gs_ctd_uy: float
    gs_epoch: str
    gs_mura: float
    gs_mudec: float
    gs_para: float
    gs_pattern_error: float
    gw_window_xstart: int
    gw_window_ystart: int
    gw_window_xstop: int
    gw_window_ystop: int
    gw_window_xsize: int
    gw_window_ysize: int

_WfiModeName = T.Literal["WFI"]
_WfiDetector = T.Literal[
    "WFI01",
    "WFI02",
    "WFI03",
    "WFI04",
    "WFI05",
    "WFI06",
    "WFI07",
    "WFI08",
    "WFI09",
    "WFI10",
    "WFI11",
    "WFI12",
    "WFI13",
    "WFI14",
    "WFI15",
    "WFI16",
    "WFI17",
    "WFI18",
]
_WfiOpticalElement = T.Literal[
    "F062",
    "F087",
    "F106",
    "F129",
    "F146",
    "F158",
    "F184",
    "F213",
    "GRISM",
    "PRISM",
    "DARK",
]

class WfiMode(stnode.TaggedObjectNode):
    name: _WfiModeName
    detector: _WfiDetector
    optical_element: _WfiOpticalElement

_ObservationSurvey = T.Literal["HLS", "EMS", "SN", "N/A"]

class Observation(stnode.TaggedObjectNode):
    obs_id: str
    visit_id: str
    program: str
    execution_plan: int
    pass_: int
    segment: int
    observation: int
    visit: int
    visit_file_group: int
    visit_file_sequence: int
    visit_file_activity: str
    exposure: int
    template: str
    observation_label: str
    survey: _ObservationSurvey

class Pointing(stnode.TaggedObjectNode):
    ra_v1: float
    dec_v1: float
    pa_v3: float

class Program(stnode.TaggedObjectNode):
    title: str
    pi_name: str
    category: str
    subcategory: str
    science_category: str
    continuation_id: int

class _Crds(stnode.DNode):
    sw_version: str
    context_used: str

class RefFile(stnode.TaggedObjectNode):
    crds: _Crds
    dark: str
    distortion: str
    mask: str
    flat: str
    gain: str
    readnoise: str
    linearity: str
    photom: str
    area: str
    saturation: str

_TargetType = T.Literal["FIXED", "MOVING", "GENERIC"]
_TargetSourceType = T.Literal["EXTENDED", "POINT", "UNKNOWN"]

class Target(stnode.TaggedObjectNode):
    proposer_name: str
    catalog_name: str
    type: _TargetType
    ra: float
    dec: float
    ra_uncertainty: float
    dec_uncertainty: float
    proper_motion_ra: float
    proper_motion_dec: float
    proper_motion_epoch: str
    proposer_ra: float
    proposer_dec: float
    source_type: _TargetSourceType

class VelocityAberration(stnode.TaggedObjectNode):
    ra_offset: float
    dec_offset: float
    scale_factor: float

_EngineeringQuality = T.Literal["OK", "SUSPECT"]
_PointingEngdbQuality = T.Literal["CALCULATED", "PLANNED"]

class Visit(stnode.TaggedObjectNode):
    engineering_quality: _EngineeringQuality
    pointing_engdb_quality: _PointingEngdbQuality
    type: str
    start_time: Time
    end_time: Time
    status: str
    total_exposures: int
    internal_target: bool
    target_of_opportunity: bool

class Wcsinfo(stnode.TaggedObjectNode):
    v2_ref: float
    v3_ref: float
    vparity: int
    v3yangle: float
    ra_ref: float
    dec_ref: float
    roll_ref: float
    s_region: str

class _Common(_Basic):
    aperture: Aperture
    cal_step: CalStep
    coordinates: Coordinates
    ephemeris: Ephemeris
    exposure: Exposure
    guidestar: Guidestar
    instrument: WfiMode
    observation: Observation
    pointing: Pointing
    program: Program
    ref_file: RefFile
    target: Target
    velocity_aberration: VelocityAberration
    visit: Visit
    wcsinfo: Wcsinfo

class _GuidewindowMeta(_Common):
    gw_start_time: Time
    gw_end_time: Time
    gw_frame_readout_time: float
    gw_function_start_time: Time
    gw_function_end_time: Time
    gw_acq_exec_stat: str
    pedestal_resultant_exp_time: float
    signal_resultant_exp_time: float
    gw_acq_number: int
    gw_mode: _GwMode
    gw_window_xstart: int
    gw_window_ystart: int
    gw_window_xstop: int
    gw_window_ystop: int
    gw_window_xsize: int
    gw_window_ysize: int

class Guidewindow(stnode.TaggedObjectNode):
    meta: _GuidewindowMeta
    pedestal_frames: _Quantity_uint16_DN_5D
    signal_frames: _Quantity_uint16_DN_5D
    amp33: _Quantity_uint16_DN_5D

class Ramp(stnode.TaggedObjectNode):
    meta: _Common
    data: _Quantity_float32_electron_3D
    pixeldq: _ndarray_uint16_2D
    groupdq: _ndarray_uint8_3D
    err: _Quantity_float32_electron_3D
    amp33: _Quantity_uint16_DN_3D
    border_ref_pix_left: _Quantity_float32_DN_3D
    border_ref_pix_right: _Quantity_float32_DN_3D
    border_ref_pix_top: _Quantity_float32_DN_3D
    border_ref_pix_bottom: _Quantity_float32_DN_3D
    dq_border_ref_pix_left: _ndarray_uint16_2D
    dq_border_ref_pix_right: _ndarray_uint16_2D
    dq_border_ref_pix_top: _ndarray_uint16_2D
    dq_border_ref_pix_bottom: _ndarray_uint16_2D

class RampFitOutput(stnode.TaggedObjectNode):
    meta: _Common
    slope: _Quantity_float32_electron_s_3D
    sigslope: _Quantity_float32_electron_s_3D
    yint: _Quantity_float32_electron_3D
    sigyint: _Quantity_float32_electron_3D
    pedestal: _Quantity_float32_electron_2D
    weights: _ndarray_float32_3D
    crmag: _Quantity_float32_electron_3D
    var_poisson: _Quantity_float32_electron2_s2_3D
    var_rnoise: _Quantity_float32_electron2_s2_3D

class WfiScienceRaw(stnode.TaggedObjectNode):
    meta: _Common
    data: _Quantity_uint16_DN_3D
    amp33: _Quantity_uint16_DN_3D

_ConversionMegaJanskys = _OptionalQuantity["MJy"]

_MJy_per_sr = T.Literal["MJy / sr"]
_uJy_per_arcsec2 = T.Literal["uJy / arcsec2"]
_sr = T.Literal["sr"]
_arcsec2 = T.Literal["arcsec2"]

class Photometry(stnode.TaggedObjectNode):
    conversion_megajanskys: _OptionalQuantity[_MJy_per_sr]
    conversion_microjanskys: _OptionalQuantity[_uJy_per_arcsec2]
    pixelarea_steradians: _OptionalQuantity[_sr]
    pixelarea_arcsecsq: _OptionalQuantity[_arcsec2]
    conversion_megajanskys_uncertainty: _OptionalQuantity[_MJy_per_sr]
    conversion_microjanskys_uncertainty: _OptionalQuantity[_uJy_per_arcsec2]

class SourceDetection(stnode.TaggedObjectNode):
    tweakreg_catalog_name: str

class _WfiImageMeta(_Common):
    photometry: Photometry
    source_detection: SourceDetection

class CalLogs(stnode.TaggedListNode):
    pass

class WfiImage(stnode.TaggedObjectNode):
    meta: _WfiImageMeta
    data: _Quantity_float32_electron_s_2D
    dq: _ndarray_uint16_2D
    err: _Quantity_float32_electron_s_2D
    var_poisson: _Quantity_float32_electron2_s2_2D
    var_rnoise: _Quantity_float32_electron2_s2_2D
    var_flat: _Quantity_float32_electron2_s2_2D
    amp33: _Quantity_uint16_DN_3D
    border_ref_pix_left: _Quantity_float32_DN_3D
    border_ref_pix_right: _Quantity_float32_DN_3D
    border_ref_pix_top: _Quantity_float32_DN_3D
    border_ref_pix_bottom: _Quantity_float32_DN_3D
    dq_border_ref_pix_left: _ndarray_uint32_2D
    dq_border_ref_pix_right: _ndarray_uint32_2D
    dq_border_ref_pix_top: _ndarray_uint32_2D
    dq_border_ref_pix_bottom: _ndarray_uint32_2D
    cal_logs: CalLogs

_p_exptype = T.Literal[
    "WFI_IMAGE",
    "WFI_GRISM",
    "WFI_PRISM",
    "WFI_DARK",
    "WFI_FLAT",
    "WFI_WFSC",
]

class _RefExposureType(stnode.DNode):
    type: _ExposureType
    p_exptype: _p_exptype

class _DarkExposure(_RefExposureType):
    ngroups: int
    nframes: int
    groupgap: int
    ma_table_name: str
    ma_table_number: int

class _Instrument(stnode.DNode):
    name: _WfiModeName
    detector: _WfiDetector
    optical_element: _WfiOpticalElement

_Pedigree = T.Literal["GROUND", "MODEL", "DUMMY", "SIMULATION"]

class _RefCommon(stnode.DNode):
    pedigree: _Pedigree
    description: str
    author: str
    useafter: Time
    telescope: _Telescope
    origin: str
    instrument: _Instrument

_DarkRefType = T.Literal["DARK"]

class _DarkRefMeta(_RefCommon):
    reftype: _DarkRefType
    exposure: _DarkExposure
    instrument: _Instrument

class DarkRef(stnode.TaggedObjectNode):
    meta: _DarkRefMeta
    data: _Quantity_float32_DN_3D
    dq: _ndarray_uint32_2D
    err: _Quantity_float32_DN_3D

_DistortionInput = T.Literal["pix"]
_DistortionOutput = T.Literal["arcsec"]

_DistortionRefType = T.Literal["DISTORTION"]

class _DistortionRefMeta(_RefCommon):
    reftype: _DistortionRefType
    input_units: _DistortionInput
    output_units: _DistortionOutput

class DistortionRef(stnode.TaggedObjectNode):
    meta: _DistortionRefMeta
    coordinate_distortion_transform: Model

_FlatRefType = T.Literal["FLAT"]

class _FlatRefMeta(_RefCommon):
    reftype: _FlatRefType
    instrument: _Instrument

class FlatRef(stnode.TaggedObjectNode):
    meta: _FlatRefMeta
    data: _ndarray_float32_2D
    dq: _ndarray_uint32_2D
    err: _ndarray_float32_2D

_GainRefType = T.Literal["GAIN"]

class _GainRefMeta(_RefCommon):
    reftype: _GainRefType

class GainRef(stnode.TaggedObjectNode):
    meta: _GainRefMeta
    data: _Quantity_float32_electron_DN_2D

_DNunit = T.Literal["DN"]

_InverseLinearityRefType = T.Literal["INVERSE_LINEARITY"]

class _InverseLinearityRefMeta(_RefCommon):
    reftype: _InverseLinearityRefType
    input_units: _DNunit
    output_units: _DNunit

class InverseLinearityRef(stnode.TaggedObjectNode):
    meta: _InverseLinearityRefMeta
    coeffs: _ndarray_float32_3D
    dq: _ndarray_uint32_2D

_IpcRefType = T.Literal["IPC"]

class _IpcRefMeta(_RefCommon):
    reftype: _IpcRefType
    instrument: _Instrument

class IpcRef(stnode.TaggedObjectNode):
    meta: _IpcRefMeta
    data: _ndarray_float32_2D

_LinearityRefType = T.Literal["LINEARITY"]

class _LinearityRefMeta(_RefCommon):
    reftype: _LinearityRefType
    input_units: _DNunit
    output_units: _DNunit

class LinearityRef(stnode.TaggedObjectNode):
    meta: _LinearityRefMeta
    coeffs: _ndarray_float32_3D
    dq: _ndarray_uint32_2D

_MaskRefType = T.Literal["MASK"]

class _MaskRefMeta(_RefCommon):
    reftype: _MaskRefType

class MaskRef(stnode.TaggedObjectNode):
    meta: _MaskRefMeta
    dq: _ndarray_uint32_2D

class _PixelareaRefPhotometry(stnode.DNode):
    pixelarea_steradians: _OptionalQuantity[_sr]
    pixelarea_arcsecsq: _OptionalQuantity[_arcsec2]

_PixelareaRefType = T.Literal["AREA"]

class _PixelareaRefMeta(_RefCommon):
    reftype: _PixelareaRefType
    photometry: _PixelareaRefPhotometry
    instrument: _Instrument

class PixelareaRef(stnode.TaggedObjectNode):
    meta: _PixelareaRefMeta
    data: _ndarray_float32_2D

_ReadnoiseRefType = T.Literal["READNOISE"]

class _ReadnoiseRefMeta(_RefCommon):
    reftype: _ReadnoiseRefType
    exposure: _RefExposureType

class ReadnoiseRef(stnode.TaggedObjectNode):
    meta: _ReadnoiseRefMeta
    data: _Quantity_float32_DN_2D

_SaturationRefType = T.Literal["SATURATION"]

class _SaturationRefMeta(_RefCommon):
    reftype: _SaturationRefType

class SaturationRef(stnode.TaggedObjectNode):
    meta: _SaturationRefMeta
    data: _Quantity_float32_DN_2D
    dq: _ndarray_uint32_2D

_SuperbiasRefType = T.Literal["BIAS"]

class _SuperbiasRefMeta(_RefCommon):
    reftype: _SuperbiasRefType

class SuperbiasRef(stnode.TaggedObjectNode):
    meta: _SuperbiasRefMeta
    data: _ndarray_float32_2D
    dq: _ndarray_uint32_2D
    err: _ndarray_float32_2D

_WfiImgPhotomRefType = T.Literal["PHOTOM"]

class _WfiImgPhotomRefMeta(_RefCommon):
    reftype: _WfiImgPhotomRefType

class _PhotTableEntry(stnode.DNode):
    photmjsr: _OptionalQuantity[_MJy_per_sr]
    uncertainty: _OptionalQuantity[_MJy_per_sr]
    pixelareasr: _OptionalQuantity[_sr]

class _PhotTable(stnode.DNode):
    F062: _PhotTableEntry
    F087: _PhotTableEntry
    F106: _PhotTableEntry
    F129: _PhotTableEntry
    F146: _PhotTableEntry
    F158: _PhotTableEntry
    F184: _PhotTableEntry
    F213: _PhotTableEntry
    GRISM: _PhotTableEntry
    PRISM: _PhotTableEntry
    DARK: _PhotTableEntry

class WfiImgPhotomRef(stnode.TaggedObjectNode):
    meta: _WfiImgPhotomRefMeta
    phot_table: _PhotTable

class _AssociationProduct(stnode.DNode):
    name: str
    members: stnode.LNode[str]

class Associations(stnode.TaggedObjectNode):
    asn_id: str
    asn_pool: str
    asn_type: str
    asn_rule: str
    version_id: str
    code_version: str
    degraded_status: str
    program: int
    target: int
    constraints: str
    products: stnode.LNode[_AssociationProduct]
