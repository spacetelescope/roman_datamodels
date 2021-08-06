import asdf
import astropy.time as time
import numpy as np

from .. import stnode
# from .. import table_definitions

NONUM = -999999
NOSTR = "dummy value"


def mk_exposure():
    exp = stnode.Exposure()
    exp['id'] = NONUM
    exp['type'] = 'WFI_IMAGE'
    exp['start_time'] = time.Time(
        '2020-01-01T00:00:00.0', format='isot', scale='utc')
    exp['mid_time'] = time.Time(
        '2020-01-01T00:00:00.0', format='isot', scale='utc')
    exp['end_time'] = time.Time(
        '2020-01-01T00:00:00.0', format='isot', scale='utc')
    exp['start_time_mjd'] = NONUM
    exp['mid_time_mjd'] = NONUM
    exp['end_time_mjd'] = NONUM
    exp['start_time_tdb'] = NONUM
    exp['mid_time_tdb'] = NONUM
    exp['end_time_tdb'] = NONUM
    exp['start_time_eng'] = NOSTR
    exp['ngroups'] = NONUM
    exp['nframes'] = NONUM
    exp['data_problem'] = False
    exp['sca_number'] = NONUM
    exp['gain_factor'] = NONUM
    exp['integration_time'] = NONUM
    exp['elapsed_exposure_time'] = NONUM
    exp['nints'] = NONUM
    exp['integration_start'] = NONUM
    exp['integration_end'] = NONUM
    exp['frame_divisor'] = NONUM
    exp['groupgap'] = NONUM
    exp['nsamples'] = NONUM
    exp['sample_time'] = NONUM
    exp['frame_time'] = NONUM
    exp['group_time'] = NONUM
    exp['exposure_time'] = NONUM
    exp['effective_exposure_time'] = NONUM
    exp['duration'] = NONUM
    exp['nresets_at_start'] = NONUM
    exp['datamode'] = NONUM
    return exp


def mk_wfi_mode():
    mode = stnode.WfiMode()
    mode['name'] = 'WFI'
    mode['detector'] = 'WFI01'
    mode['optical_element'] = 'F062'
    return mode


def mk_program():
    prog = stnode.Program()
    prog['title'] = NOSTR
    prog['pi_name'] = NOSTR
    prog['category'] = NOSTR
    prog['subcategory'] = NOSTR
    prog['science_category'] = NOSTR
    prog['continuation_id'] = NONUM
    return prog


def mk_observation():
    obs = stnode.Observation()
    obs['start_time'] = time.Time(
        '2020-01-01T00:00:00.0', format='isot', scale='utc')
    obs['end_time'] = time.Time(
        '2020-01-01T00:00:00.0', format='isot', scale='utc')
    obs['obs_id'] = NOSTR
    obs['visit_id'] = NOSTR
    obs['program'] = NONUM
    obs['execution_plan'] = NONUM
    obs['pass'] = NONUM
    obs['segment'] = NONUM
    obs['observation'] = NONUM
    obs['visit'] = NONUM
    obs['visit_file_group'] = NONUM
    obs['visit_file_sequence'] = NONUM
    obs['visit_file_activity'] = NOSTR
    obs['exposure'] = NONUM
    obs['activity_id'] = NOSTR
    obs['template'] = NOSTR
    obs['observation_label'] = NOSTR
    obs['ma_table_name'] = NOSTR
    obs['survey'] = 'N/A'
    return obs


def mk_ephemeris():
    ephem = stnode.Ephemeris()
    ephem['earth_angle'] = NONUM
    ephem['moon_angle'] = NONUM
    ephem['ephemeris_reference_frame'] = NOSTR
    ephem['sun_angle'] = NONUM
    ephem['type'] = 'DEFINITIVE'
    ephem['time'] = NONUM
    ephem['spatial_x'] = NONUM
    ephem['spatial_y'] = NONUM
    ephem['spatial_z'] = NONUM
    ephem['velocity_x'] = NONUM
    ephem['velocity_y'] = NONUM
    ephem['velocity_z'] = NONUM
    return ephem


def mk_visit():
    visit = stnode.Visit()
    visit['engineering_quality'] = 'OK'  # qqqq
    visit['pointing_engdb_quality'] = 'CALCULATED'  # qqqq
    visit['type'] = NOSTR
    visit['start_time'] = time.Time(
        '2020-01-01T00:00:00.0', format='isot', scale='utc')
    visit['end_time'] = time.Time(
        '2020-01-01T00:00:00.0', format='isot', scale='utc')
    visit['status'] = NOSTR
    visit['total_exposures'] = NONUM
    visit['internal_target'] = False
    visit['target_of_opportunity'] = False
    return visit


def mk_photometry():
    phot = stnode.Photometry()
    phot['conversion_megajanskys'] = NONUM
    phot['conversion_microjanskys'] = NONUM
    phot['pixelarea_steradians'] = NONUM
    phot['pixelarea_arcsecsq'] = NONUM
    return phot


def mk_coordinates():
    coord = stnode.Coordinates()
    coord['reference_frame'] = 'ICRS'
    return coord


def mk_aperture():
    aper = stnode.Aperture()
    aper['name'] = NOSTR
    aper['pss_name'] = NOSTR
    aper['position_angle'] = 30.
    return aper


def mk_pointing():
    point = stnode.Pointing()
    point['ra_v1'] = NONUM
    point['dec_v1'] = NONUM
    point['pa_v3'] = NONUM
    return point


def mk_target():
    targ = stnode.Target()
    targ['proposer_name'] = NOSTR
    targ['catalog_name'] = NOSTR
    targ['type'] = 'FIXED'
    targ['ra'] = NONUM
    targ['dec'] = NONUM
    targ['ra_uncertainty'] = NONUM
    targ['dec_uncertainty'] = NONUM
    targ['proper_motion_ra'] = NONUM
    targ['proper_motion_dec'] = NONUM
    targ['proper_motion_epoch'] = NOSTR
    targ['proposer_ra'] = NONUM
    targ['proposer_dec'] = NONUM
    targ['source_type_apt'] = 'POINT'
    targ['source_type'] = 'POINT'
    return targ


def mk_velocity_aberration():
    vab = stnode.VelocityAberration()
    vab['ra_offset'] = NONUM
    vab['dec_offset'] = NONUM
    vab['scale_factor'] = NONUM
    return vab


def mk_wcsinfo():
    wcsi = stnode.Wcsinfo()
    wcsi['v2_ref'] = NONUM
    wcsi['v3_ref'] = NONUM
    wcsi['vparity'] = NONUM
    wcsi['v3yangle'] = NONUM
    wcsi['ra_ref'] = NONUM
    wcsi['dec_ref'] = NONUM
    wcsi['roll_ref'] = NONUM
    wcsi['s_region'] = NOSTR
    return wcsi


def mk_cal_step():
    calstep = stnode.CalStep()
    calstep['flat_field'] = 'INCOMPLETE'
    calstep['dq_init'] = 'INCOMPLETE'
    return calstep


def mk_guide():
    guide = stnode.Guidestar()
    guide['gw_start_time'] = time.Time(
        '2020-01-01T00:00:00.0', format='isot', scale='utc')
    guide['gw_stop_time'] = time.Time(
        '2020-01-01T00:00:00.0', format='isot', scale='utc')
    guide['gw_id'] = NOSTR
    guide['gs_ra'] = NONUM
    guide['gs_dec'] = NONUM
    guide['gs_ura'] = NONUM
    guide['gs_udec'] = NONUM
    guide['gs_mag'] = NONUM
    guide['gs_umag'] = NONUM
    guide['gw_pcs_mode'] = NOSTR
    guide['gw_function_start_time'] = time.Time(
        '2020-01-01T00:00:00.0', format='isot', scale='utc')
    guide['gw_function_end_time'] = time.Time(
        '2020-01-01T00:00:00.0', format='isot', scale='utc')
    guide['data_start'] = NONUM
    guide['data_end'] = NONUM
    guide['gw_acq_exec_stat'] = NOSTR
    guide['gs_ctd_x'] = NONUM
    guide['gs_ctd_y'] = NONUM
    guide['gs_ctd_ux'] = NONUM
    guide['gs_ctd_uy'] = NONUM
    guide['gs_epoch'] = NOSTR
    guide['gs_mura'] = NONUM
    guide['gs_mudec'] = NONUM
    guide['gs_para'] = NONUM
    guide['gw_window_xstart'] = NONUM
    guide['gw_window_ystart'] = NONUM
    guide['gw_window_xsize'] = NONUM
    guide['gw_window_ysize'] = NONUM
    return guide


def mk_basic_meta():
    meta = {}
    meta['calibration_software_version'] = '9.9.9'
    meta['crds_software_version'] = '8.8.8'
    meta['crds_context_used'] = '222'
    meta['sdf_software_version'] = '7.7.7'
    meta['filename'] = NOSTR
    meta['file_date'] = time.Time(
        '2020-01-01T00:00:00.0', format='isot', scale='utc')
    meta['model_type'] = NOSTR
    meta['origin'] = 'STSCI'
    meta['prd_software_version'] = '8.8.8'
    meta['telescope'] = 'ROMAN'
    return meta


def mk_common_meta():
    meta = mk_basic_meta()
    meta['aperture'] = mk_aperture()
    meta['cal_step'] = mk_cal_step()
    meta['coordinates'] = mk_coordinates()
    meta['ephemeris'] = mk_ephemeris()
    meta['exposure'] = mk_exposure()
    meta['guidestar'] = mk_guide()
    meta['instrument'] = mk_wfi_mode()
    meta['observation'] = mk_observation()
    meta['photometry'] = mk_photometry()
    meta['pointing'] = mk_pointing()
    meta['program'] = mk_program()
    meta['target'] = mk_target()
    meta['velocity_aberration'] = mk_velocity_aberration()
    meta['visit'] = mk_visit()
    meta['wcsinfo'] = mk_wcsinfo()
    return meta

def mk_level1_science_raw(arrays=True):
    meta = mk_common_meta()
    wfi_science_raw = stnode.WfiScienceRaw()
    wfi_science_raw['meta'] = meta
    if not arrays:
        wfi_science_raw['data'] = None
    else:
        if arrays is True:
            shape = (8, 4096, 4096)
        else:
            shape = arrays
        wfi_science_raw['data'] = np.zeros(shape, dtype=np.uint16)
    return wfi_science_raw


def mk_level2_image(arrays=True):
    meta = mk_common_meta()
    wfi_image = stnode.WfiImage()
    wfi_image['meta'] = meta
    if not arrays:
        wfi_image['data'] = None
        wfi_image['dq'] = None
        wfi_image['err'] = None
        wfi_image['var_poisson'] = None
        wfi_image['var_rnoise'] = None
        wfi_image['var_flat'] = None
        wfi_image['area'] = None
    else:
        if arrays is True:
            shape = (4096, 4096)
        else:
            shape = arrays
        wfi_image['data'] = np.zeros(shape, dtype=np.float32)
        wfi_image['dq'] = np.zeros(shape, dtype=np.uint32)
        wfi_image['err'] = np.zeros(shape, dtype=np.float32)
        wfi_image['var_poisson'] = np.zeros(shape, dtype=np.float32)
        wfi_image['var_rnoise'] = np.zeros(shape, dtype=np.float32)
        wfi_image['var_flat'] = np.zeros(shape, dtype=np.float32)
        wfi_image['area'] = np.zeros(shape, dtype=np.float32)
    return wfi_image


def add_ref_common(meta):
    instrument = {'name': 'WFI', 'detector': 'WFI01',
                  'optical_element': 'F158'}
    meta['telescope'] = 'ROMAN'
    meta['instrument'] = instrument
    meta['origin'] = 'STSCI'
    meta['pedigree'] = 'test pedigree'
    meta['author'] = 'test system'
    meta['description'] = 'blah blah blah'
    meta['useafter'] = time.Time(
        '2020-01-01T00:00:00.0', format='isot', scale='utc')
    meta['reftype'] = ''

def mk_flat_file(outfilepath, shape=(20, 20)):
    meta = {}
    add_ref_common(meta)
    flatref = stnode.FlatRef()
    meta['reftype'] = 'FLAT'
    flatref['meta'] = meta
    flatref['data'] = np.zeros(shape, dtype=np.float32)
    flatref['dq'] = np.zeros(shape, dtype=np.uint32)
    flatref['err'] = np.zeros(shape, dtype=np.float32)
    af = asdf.AsdfFile()
    af.tree = {'roman': flatref}
    af.write_to(outfilepath)

def mk_mask(shape=True):
    meta = {}
    add_ref_common(meta)
    maskref = stnode.MaskRef()
    meta['reftype'] = 'MASK'
    maskref['meta'] = meta

    if shape:
        maskref['dq'] = np.zeros(shape, dtype=np.uint32)
    else:
        maskref['dq'] = np.zeros((4096, 4096), dtype=np.uint32)

    return maskref


def mk_ramp(arrays=True):
    meta = mk_common_meta()
    ramp = stnode.Ramp()
    ramp['meta'] = meta
    if not arrays:
        ramp['data'] = None
        ramp['pixeldq'] = None
        ramp['groupdq'] = None
        ramp['err'] = None
    else:
        if arrays is True:
            shape = (8, 4096, 4096)
        else:
            shape = arrays
        ramp['data'] = np.full(shape, 1.0, dtype=np.float32)
        ramp['pixeldq'] = np.zeros(shape[1:], dtype=np.uint32)
        ramp['groupdq'] = np.zeros(shape, dtype=np.uint8)
        ramp['err'] = np.zeros(shape[1:], dtype=np.float32)
    return ramp
