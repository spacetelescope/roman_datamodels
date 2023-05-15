from __future__ import annotations

import astropy.units as u
import numpy as np
from astropy.modeling import Model  # type: ignore
from astropy.time import Time  # type: ignore

from roman_datamodels import stnode  # type: ignore
from roman_datamodels._typing import base, enums

with stnode.registration_off():
    class FileDate(stnode.TaggedScalarNode, Time):
        pass

    class CalibrationSoftwareVersion(stnode.TaggedScalarNode, str):
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
        name: enums.ApertureName
        position_angle: float

    class CalStep(stnode.TaggedObjectNode):
        assign_wcs: enums.CalStepValues
        flat_field: enums.CalStepValues
        dark: enums.CalStepValues
        dq_init: enums.CalStepValues
        jump: enums.CalStepValues
        linearity: enums.CalStepValues
        photom: enums.CalStepValues
        source_detection: enums.CalStepValues
        ramp_fit: enums.CalStepValues
        saturation: enums.CalStepValues

    class Coordinates(stnode.TaggedObjectNode):
        reference_frame: enums.ReferenceFrame

    class Ephemeris(stnode.TaggedObjectNode):
        earth_angle: float
        moon_angle: float
        ephemeris_reference_frame: str
        sun_angle: float
        type: enums.EphemerisType
        time: float
        spatial_x: float
        spatial_y: float
        spatial_z: float
        velocity_x: float
        velocity_y: float
        velocity_z: float

    class Exposure(stnode.TaggedObjectNode):
        id: int
        type: enums.ExposureType
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
        gw_fgs_mode: enums.GuidewindowMode
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

    class WfiMode(stnode.TaggedObjectNode):
        name: enums.WfiModeNames
        detector: enums.WfiDetector
        optical_element: enums.WfiOpticalElement

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
        survey: enums.ObservationSurvey

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
        type: enums.TargetType
        ra: float
        dec: float
        ra_uncertainty: float
        dec_uncertainty: float
        proper_motion_ra: float
        proper_motion_dec: float
        proper_motion_epoch: str
        proposer_ra: float
        proposer_dec: float
        source_type: enums.SourceType

    class VelocityAberration(stnode.TaggedObjectNode):
        ra_offset: float
        dec_offset: float
        scale_factor: float

    class Visit(stnode.TaggedObjectNode):
        engineering_quality: enums.EngineeringQuality
        pointing_engdb_quality: enums.PointingEngdbQuality
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
        gw_science_file_source: str
        gw_mode: enums.GuidewindowMode
        gw_window_xstart: int
        gw_window_ystart: int
        gw_window_xstop: int
        gw_window_ystop: int
        gw_window_xsize: int
        gw_window_ysize: int

    class Guidewindow(stnode.TaggedObjectNode):
        meta: _GuidewindowMeta
        pedestal_frames: base.Quantity[np.ndarray[1, np.uint16], u.DN]
        signal_frames: base.Quantity[np.ndarray[1, np.uint16], u.DN]
        amp33: base.Quantity[np.ndarray[1, np.uint16], u.DN]

    class Ramp(stnode.TaggedObjectNode):
        meta: _Common
        data: base.Quantity[np.ndarray[3, np.float32], u.electron]
        pixeldq: np.ndarray[2, np.uint16]
        groupdq: np.ndarray[2, np.uint8]
        err: base.Quantity[np.ndarray[3, np.float32], u.electron]
        amp33: base.Quantity[np.ndarray[3, np.uint16], u.DN]
        border_ref_pix_left: base.Quantity[np.ndarray[3, np.float32], u.DN]
        border_ref_pix_right: base.Quantity[np.ndarray[3, np.float32], u.DN]
        border_ref_pix_top: base.Quantity[np.ndarray[3, np.float32], u.DN]
        border_ref_pix_bottom: base.Quantity[np.ndarray[3, np.float32], u.DN]
        dq_border_ref_pix_left: np.ndarray[2, np.uint16]
        dq_border_ref_pix_right: np.ndarray[2, np.uint16]
        dq_border_ref_pix_top: np.ndarray[2, np.uint16]
        dq_border_ref_pix_left: np.ndarray[2, np.uint16]

    class RampFitOutput(stnode.TaggedObjectNode):
        meta: _Common
        slope: base.Quantity[np.ndarray[3, np.float32], u.electron / u.s]
        sigslope: base.Quantity[np.ndarray[3, np.float32], u.electron / u.s]
        yint: base.Quantity[np.ndarray[3, np.float32], u.electron]
        sigyint: base.Quantity[np.ndarray[3, np.float32], u.electron]
        pedestal: base.Quantity[np.ndarray[2, np.float32], u.electron]
        weights: np.ndarray[3, np.float32]
        crmag: base.Quantity[np.ndarray[3, np.float32], u.electron]
        var_poisson: base.Quantity[np.ndarray[3, np.float32], u.electron**2 / u.s**2]
        var_rnoise: base.Quantity[np.ndarray[3, np.float32], u.electron**2 / u.s**2]

    class Resample(stnode.TaggedObjectNode):
        pixel_scale_ratio: float
        pixfrac: float
        pointings: int
        product_exposure_time: int
        weight_type: enums.ResampleWeightType

    class WfiScienceRaw(stnode.TaggedObjectNode):
        meta: _Common
        data: base.Quantity[np.ndarray[3, np.uint16], u.DN]
        amp33: base.Quantity[np.ndarray[3, np.uint16], u.DN]

    class Photometry(stnode.TaggedObjectNode):
        conversion_megajanskys: u.Quantity[u.MJy / u.sr] | None
        conversion_microjanskys: u.Quantity[u.uJy / u.arcsec**2] | None
        pixelarea_steradians: u.Quantity[u.sr] | None
        pixelarea_arcsecsq: u.Quantity[u.arcsec**2] | None
        conversion_megajanskys_uncertainty: u.Quantity[u.MJy / u.sr] | None
        conversion_microjanskys_uncertainty: u.Quantity[u.uJy / u.arcsec**2] | None

    class SourceDetection(stnode.TaggedObjectNode):
        tweakreg_catalog_name: str

    class _WfiImageMeta(_Common):
        photometry: Photometry
        source_detection: SourceDetection

    class CalLogs(stnode.TaggedListNode):
        pass

    class WfiImage(stnode.TaggedObjectNode):
        meta: _WfiImageMeta
        data: base.Quantity[np.ndarray[2, np.float32], u.electron / u.s]
        dq: np.ndarray[2, np.uint16]
        err: base.Quantity[np.ndarray[2, np.float32], u.electron / u.s]
        var_poisson: base.Quantity[np.ndarray[2, np.float32], u.electron**2 / u.s**2]
        var_rnoise: base.Quantity[np.ndarray[2, np.float32], u.electron**2 / u.s**2]
        var_flat: base.Quantity[np.ndarray[2, np.float32], u.electron**2 / u.s**2]
        amp33: base.Quantity[np.ndarray[3, np.uint16], u.DN]
        border_ref_pix_left: base.Quantity[np.ndarray[3, np.float32], u.DN]
        border_ref_pix_right: base.Quantity[np.ndarray[3, np.float32], u.DN]
        border_ref_pix_top: base.Quantity[np.ndarray[3, np.float32], u.DN]
        border_ref_pix_bottom: base.Quantity[np.ndarray[3, np.float32], u.DN]
        dq_border_ref_pix_left: np.ndarray[3, np.uint32]
        dq_border_ref_pix_right: np.ndarray[3, np.uint32]
        dq_border_ref_pix_top: np.ndarray[3, np.uint32]
        dq_border_ref_pix_bottom: np.ndarray[3, np.uint32]
        cal_logs: CalLogs

    class _WfiMosiacMeta(_Common):
        photometry: Photometry
        resample: Resample

    class WfiMosaic(stnode.TaggedObjectNode):
        meta: _WfiMosiacMeta
        data: base.Quantity[np.ndarray[2, np.float32], u.electron / u.s]
        err: base.Quantity[np.ndarray[2, np.float32], u.electron / u.s]
        context: np.ndarray[3, np.uint32]
        weight: np.ndarray[2, np.float32]
        var_poisson: base.Quantity[np.ndarray[2, np.float32], u.electron**2 / u.s**2]
        var_rnoise: base.Quantity[np.ndarray[2, np.float32], u.electron**2 / u.s**2]
        var_flat: base.Quantity[np.ndarray[2, np.float32], u.electron**2 / u.s**2]
        cal_logs: CalLogs

    class _RefExposureType(stnode.DNode):
        type: enums.ExposureType
        p_exptype: enums.ExposureType

    class _DarkExposure(_RefExposureType):
        ngroups: int
        nframes: int
        groupgap: int
        ma_table_name: str
        ma_table_number: int

    class _Instrument(stnode.DNode):
        name: enums.WfiModeNames
        detector: enums.WfiDetector
        optical_element: enums.WfiOpticalElement

    class _RefCommon(stnode.DNode):
        pedigree: enums.Pedigree
        description: str
        author: str
        useafter: Time
        telescope: enums.Telescope
        origin: str
        instrument: _Instrument

    class _DarkRefMeta(_RefCommon):
        reftype: enums.DarkRefType
        exposure: _DarkExposure
        instrument: _Instrument

    class DarkRef(stnode.TaggedObjectNode):
        meta: _DarkRefMeta
        data: base.Quantity[np.ndarray[3, np.float32], u.DN]
        dq: base.Quantity[np.ndarray[2, np.uint32], u.DN]
        err: base.Quantity[np.ndarray[3, np.float32], u.DN]

    class _DistortionRefMeta(_RefCommon):
        reftype: enums.DistortionRefType
        input_units: base.Unit[u.pix]
        output_units: base.Unit[u.arcsec]

    class DistortionRef(stnode.TaggedObjectNode):
        meta: _DistortionRefMeta
        coordinate_distortion_transform: Model

    class _FlatRefMeta(_RefCommon):
        reftype: enums.FlatRefType
        instrument: _Instrument

    class FlatRef(stnode.TaggedObjectNode):
        meta: _FlatRefMeta
        data: np.ndarray[2, np.float32]
        dq: np.ndarray[2, np.uint32]
        err: np.ndarray[2, np.float32]

    class _GainRefMeta(_RefCommon):
        reftype: enums.GainRefType

    class GainRef(stnode.TaggedObjectNode):
        meta: _GainRefMeta
        data: base.Quantity[np.ndarray[2, np.float32], u.electron / u.DN]

    class _InverseLinearityRefMeta(_RefCommon):
        reftype: enums.InverseLinearityRefType
        input_units: base.Unit[u.DN]
        output_units: base.Unit[u.DN]

    class InverseLinearityRef(stnode.TaggedObjectNode):
        meta: _InverseLinearityRefMeta
        coeffs: np.ndarray[3, np.float32]
        dq: np.ndarray[2, np.uint32]

    class _IpcRefMeta(_RefCommon):
        reftype: enums.IPCRefType
        instrument: _Instrument

    class IpcRef(stnode.TaggedObjectNode):
        meta: _IpcRefMeta
        data: np.ndarray[3, np.float32]

    class _LinearityRefMeta(_RefCommon):
        reftype: enums.LinearityRefType
        input_units: base.Unit[u.DN]
        output_units: base.Unit[u.DN]

    class LinearityRef(stnode.TaggedObjectNode):
        meta: _LinearityRefMeta
        coeffs: np.ndarray[3, np.float32]
        dq: np.ndarray[2, np.uint32]

    class _MaskRefMeta(_RefCommon):
        reftype: enums.MaskRefType

    class MaskRef(stnode.TaggedObjectNode):
        meta: _MaskRefMeta
        dq: np.ndarray[2, np.uint32]

    class _PixelareaRefPhotometry(stnode.DNode):
        pixelarea_steradians: u.Quantity[u.sr] | None
        pixelarea_arcsecsq: u.Quantity[u.arcsec**2] | None

    class _PixelareaRefMeta(_RefCommon):
        reftype: enums.PixelareaRefType
        photometry: _PixelareaRefPhotometry
        instrument: _Instrument

    class PixelareaRef(stnode.TaggedObjectNode):
        meta: _PixelareaRefMeta
        data: np.ndarray[2, np.float32]

    class _ReadnoiseRefMeta(_RefCommon):
        reftype: enums.ReadnoiseRefType
        exposure: _RefExposureType

    class ReadnoiseRef(stnode.TaggedObjectNode):
        meta: _ReadnoiseRefMeta
        data: base.Quantity[np.ndarray[2, np.float32], u.DN]

    class _SaturationRefMeta(_RefCommon):
        reftype: enums.SaturationRefType

    class SaturationRef(stnode.TaggedObjectNode):
        meta: _SaturationRefMeta
        data: base.Quantity[np.ndarray[2, np.float32], u.DN]
        dq: np.ndarray[2, np.uint32]

    class _SuperbiasRefMeta(_RefCommon):
        reftype: enums.SuperbiasRefType

    class SuperbiasRef(stnode.TaggedObjectNode):
        meta: _SuperbiasRefMeta
        data: np.ndarray[2, np.float32]
        dq: np.ndarray[2, np.uint32]
        err: np.ndarray[2, np.float32]

    class _WfiImgPhotomRefMeta(_RefCommon):
        reftype: enums.WfiPhotomRefType

    class _PhotTableEntry(stnode.DNode):
        photmjsr: u.Quantity[u.MJy / u.sr] | None
        uncertainty: u.Quantity[u.MJy / u.sr] | None
        pixelareasr: u.Quantity[u.sr] | None

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
