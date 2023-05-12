import typing as T

if T.TYPE_CHECKING:
    from astropy.modeling import Model  # type: ignore
    from astropy.time import Time  # type: ignore
    from astropy.units import Quantity, Unit  # type: ignore
    from numpy import ndarray  # type: ignore

    from roman_datamodels import stnode  # type: ignore

class FileDate(stnode.TaggedScalarNode, Time):
    pass

class CalibrationSoftwareVersion(stnode.TaggedScalarNode, Time):
    pass

class Filename(stnode.TaggedScalarNode, str):
    pass

class ModelType(stnode.TaggedScalarNode, str):
    pass

class Origin(stnode.TaggedScalarNode, str):
    pass

class PrdSoftwareVersion(stnode.TaggedScalarNode, str):
    pass

class SdfSoftwareVersion(stnode.TaggedScalarNode, str):
    pass

class Telescope(stnode.TaggedScalarNode, str):
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

class Aperture(stnode.TaggedObjectNode):
    name: str
    position_angle: float
    shape: str

class CalStep(stnode.TaggedObjectNode):
    assign_wcs: str
    flat_field: str
    dark: str
    dq_init: str
    jump: str
    linearity: str
    photom: str
    source_detection: str
    ramp_fit: str
    saturation: str

class Coordinates(stnode.TaggedObjectNode):
    reference_frame: str

class Ephemeris(stnode.TaggedObjectNode):
    earth_angele: float
    moon_angle: float
    ephemeris_reference_frame: str
    sun_angle: float
    type: str
    time: float
    spatial_x: float
    spatial_y: float
    spatial_z: float
    velocity_x: float
    velocity_y: float
    velocity_z: float

class Exposure(stnode.TaggedObjectNode):
    id: int
    type: str
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
    gw_fgs_mode: str
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

class WfiMode(stnode.TaggedObjectNode):
    name: str
    detector: str
    optical_element: str

class Observation(stnode.TaggedObjectNode):
    obs_id: str
    visit_id: str
    program: int
    execution_plan: int
    # pass: int
    segment: int
    observation: int
    visit: int
    visit_file_group: int
    visit_file_sequence: int
    visit_file_activity: int
    exposure: int
    template: str
    observation_label: str
    survey: str

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

class Target(stnode.TaggedObjectNode):
    proposer_name: str
    catalog_name: str
    type: str
    ra: float
    dec: float
    ra_uncertainty: float
    dec_uncertainty: float
    proper_motion_ra: float
    proper_motion_dec: float
    proper_motion_epoch: float
    proposer_ra: float
    proposer_dec: float
    source_type: str

class VelocityAberration(stnode.TaggedObjectNode):
    ra_offset: float
    dec_offset: float
    scale_factor: float

class Visit(stnode.TaggedObjectNode):
    engineering_quality: str
    pointing_engdb_quality: str
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
    gw_mode: str
    gw_window_xstart: int
    gw_window_ystart: int
    gw_window_xstop: int
    gw_window_ystop: int
    gw_window_xsize: int
    gw_window_ysize: int

class Guidewindow(stnode.TaggedObjectNode):
    meta: _GuidewindowMeta
    pedestal_frames: Quantity
    signal_frames: Quantity
    amp33: Quantity

class Ramp(stnode.TaggedObjectNode):
    meta: _Common
    data: Quantity
    pixeldq: ndarray
    groupdq: ndarray
    err: Quantity
    amp33: Quantity
    border_ref_pix_left: Quantity
    border_ref_pix_right: Quantity
    border_ref_pix_top: Quantity
    border_ref_pix_bottom: Quantity
    dq_border_ref_pix_left: ndarray
    dq_border_ref_pix_right: ndarray
    dq_border_ref_pix_top: ndarray
    dq_border_ref_pix_bottom: ndarray

class RampFitOutput(stnode.TaggedObjectNode):
    meta: _Common
    slope: Quantity
    sigslope: Quantity
    yint: Quantity
    sigyint: Quantity
    pedestal: Quantity
    weights: ndarray
    crmag: Quantity
    var_poisson: Quantity
    var_rnoise: Quantity

class WfiScienceRaw(stnode.TaggedObjectNode):
    meta: _Common
    data: Quantity
    amp33: Quantity

class Photometry(stnode.TaggedObjectNode):
    conversion_megajanskys: Quantity | None
    conversion_microjanskys: Quantity | None
    pixelarea_steradians: Quantity | None
    pixelarea_arcseqsq: Quantity | None
    conversion_megajanskys_uncertainty: Quantity | None
    conversion_microjanskys_uncertainty: Quantity | None

class SourceDetection(stnode.TaggedObjectNode):
    tweakreg_catalog_name: str

class _WfiImageMeta(_Common):
    photometry: Photometry
    source_detection: SourceDetection

class CalLogs(stnode.TaggedListNode):
    pass

class WfiImage(stnode.TaggedObjectNode):
    meta: _WfiImageMeta
    data: Quantity
    dq: ndarray
    err: Quantity
    var_poisson: Quantity
    var_rnoise: Quantity
    var_flat: Quantity
    amp33: Quantity
    border_ref_pix_left: Quantity
    border_ref_pix_right: Quantity
    border_ref_pix_top: Quantity
    border_ref_pix_bottom: Quantity
    dq_border_ref_pix_left: ndarray
    dq_border_ref_pix_right: ndarray
    dq_border_ref_pix_top: ndarray
    dq_border_ref_pix_bottom: ndarray
    cal_logs: CalLogs

class _RefExposureType(stnode.DNode):
    type: str
    p_type: str

class _DarkExposure(_RefExposureType):
    ngroups: int
    nframes: int
    groupgap: int
    ma_table_name: str
    ma_table_number: int

class _Instrument(stnode.DNode):
    optical_element: str

class _DarkRefMeta(_Common):
    reftype: str
    exposure: _DarkExposure
    instrument: _Instrument

class DarkRef(stnode.TaggedObjectNode):
    meta: _DarkRefMeta
    data: Quantity
    dq: ndarray
    err: Quantity

class _DistortionRefMeta(_Common):
    reftype: str
    input_units: Unit
    output_units: Unit

class DistortionRef(stnode.TaggedObjectNode):
    meta: _DistortionRefMeta
    coordinate_distortion_transform: Model

class _FlatRefMeta(_Common):
    reftype: str
    instrument: _Instrument

class FlatRef(stnode.TaggedObjectNode):
    meta: _FlatRefMeta
    data: ndarray
    dq: ndarray
    err: ndarray

class _GainRefMeta(_Common):
    reftype: str

class GainRef(stnode.TaggedObjectNode):
    data: Quantity

class _InverseLinearityRefMeta(_Common):
    reftype: str
    input_units: Unit
    output_units: Unit

class InverseLinearityRef(stnode.TaggedObjectNode):
    meta: _InverseLinearityRefMeta
    coeffs: ndarray
    dq: ndarray

class _IpcRefMeta(_Common):
    reftype: str
    instrument: _Instrument

class IpcRef(stnode.TaggedObjectNode):
    meta: _IpcRefMeta
    data: ndarray

class _LinearityRefMeta(_Common):
    reftype: str
    input_units: Unit
    output_units: Unit

class LinearityRef(stnode.TaggedObjectNode):
    meta: _LinearityRefMeta
    coeffs: ndarray
    dq: ndarray

class _MaskRefMeta(_Common):
    reftype: str

class MaskRef(stnode.TaggedObjectNode):
    meta: _MaskRefMeta
    dq: ndarray

class _PixelareaRefPhotometry(stnode.DNode):
    pixelarea_steradians: Quantity | None
    pixelarea_arcseqsq: Quantity | None

class _PixelareaRefMeta(_Common):
    reftype: str
    photometry: _PixelareaRefPhotometry
    instrument: _Instrument

class PixelareaRef(stnode.TaggedObjectNode):
    meta: _PixelareaRefMeta
    data: ndarray

class _ReadnoiseRefMeta(_Common):
    reftype: str
    exposure: _RefExposureType

class ReadnoiseRef(stnode.TaggedObjectNode):
    meta: _ReadnoiseRefMeta
    data: Quantity

class _SaturationRefMeta(_Common):
    reftype: str

class SaturationRef(stnode.TaggedObjectNode):
    meta: _SaturationRefMeta
    data: Quantity
    dq: ndarray

class _SuperbiasRefMeta(_Common):
    reftype: str

class SuperbiasRef(stnode.TaggedObjectNode):
    meta: _SuperbiasRefMeta
    data: ndarray
    dq: ndarray
    err: ndarray

class _WfiImgPhotomRefMeta(_Common):
    reftype: str

class _PhotTableEntry(stnode.DNode):
    photmjsr: Quantity | None
    uncertainty: Quantity | None
    pixelareasr: Quantity | None

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
