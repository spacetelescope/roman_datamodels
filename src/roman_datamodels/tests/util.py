from .. import stnode
import asdf
import astropy.time as time
import numpy as np

NONUM = -999999
NOSTR = "dummy value"

def mk_exposure():
    exp = stnode.Exposure()
    exp['count'] = NONUM
    exp['type'] = 'WFI_IMAGE'
    exp['start_time'] =  NONUM
    exp['mid_time'] =   NONUM
    exp['end_time'] =   NONUM
    exp['start_time_mjd'] = NONUM
    exp['mid_time_mjd'] = NONUM
    exp['end_time_mjd'] = NONUM
    exp['start_time_tdb'] =  NONUM
    exp['mid_time_tdb'] = NONUM
    exp['end_time_tdb'] = NONUM
    exp['start_time_eng'] = NOSTR
    exp['ngroups'] = NONUM
    exp['nframes'] = NONUM
    exp['data_problem'] = False
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
    prog['sub_category'] = NOSTR
    prog['science_category'] = NOSTR
    prog['continuation_id'] = NONUM
    return prog

def mk_observation():
    obs = stnode.Observation()
    obs['date'] = NOSTR
    obs['time'] = NOSTR
    obs['date_beg'] = NOSTR
    obs['date_end'] = NOSTR
    obs['obs_id'] = NOSTR
    obs['visit_id'] = NOSTR
    obs['program_number'] = NOSTR
    obs['execution_plan_number'] = NOSTR
    obs['pass_number'] = NOSTR
    obs['leg_number'] = NOSTR
    obs['observation_number'] = NOSTR
    obs['visit_number'] = NOSTR
    obs['visit_group'] = NOSTR
    obs['activity_id'] = NOSTR
    obs['exposure_number'] = NOSTR
    obs['template'] = NOSTR
    obs['observation_label'] = NOSTR
    obs['observation_folder'] = NOSTR
    obs['ma_table_name'] = NOSTR
    return obs

def mk_ephemeris():
    ephem = stnode.Ephemeris()
    ephem['earth_angle'] = NONUM
    ephem['moon_angle'] = NONUM
    ephem['sun_angle'] = NONUM
    ephem['type'] = NOSTR
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
    visit['engineering_quality'] = 'OK' #qqqq
    visit['pointing_engdb_quality'] = 'CALCULATED' #qqqq
    visit['type'] = NOSTR
    visit['start_time'] = NOSTR
    visit['end_time'] = NOSTR
    visit['status'] = NOSTR
    visit['total_exposures'] = NONUM
    visit['internal_target'] = False
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
    aper['position_angle'] = NONUM
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
    targ['type'] = NOSTR
    targ['ra'] = NONUM
    targ['dec'] =  NONUM
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
    wcsi['v3_ref'] =  NONUM
    wcsi['vparity'] = NONUM
    wcsi['v3yangle'] = NONUM
    wcsi['ra_ref'] = NONUM
    wcsi['dec_ref'] = NONUM
    wcsi['roll_ref'] = NONUM
    return wcsi

def mk_cal_step():
    calstep = stnode.CalStep()
    calstep['flat_field'] = 'INCOMPLETE'
    return calstep

def mk_guide():
    guide = stnode.Guidestar()
    guide['gs_start_time'] = NOSTR
    guide['gs_stop_time'] = NOSTR
    guide['gs_id'] = NOSTR
    guide['gs_ra'] = NONUM
    guide['gs_dec'] = NONUM
    guide['gs_ura'] = NONUM
    guide['gs_udec'] = NONUM
    guide['gs_mag'] = NONUM
    guide['gs_umag'] = NONUM
    guide['gs_pcs_mode'] = NOSTR
    guide['gs_function_start_time'] = NOSTR
    guide['gs_function_end_time'] =  NOSTR
    guide['data_start'] = NONUM
    guide['data_end'] = NONUM
    guide['gs_acq_exec_stat'] = NOSTR
    guide['gs_ctd_x'] = NONUM
    guide['gs_ctd_y'] = NONUM
    guide['gs_ctd_ux'] = NONUM
    guide['gs_ctd_uy'] = NONUM
    guide['gs_epoch'] = NOSTR
    guide['gs_mura'] = NONUM
    guide['gs_mudec'] = NONUM
    guide['gs_para'] = NONUM
    guide['gs_window_xstart'] = NONUM
    guide['gs_window_ystart'] = NONUM
    guide['gs_window_xsize'] = NONUM
    guide['gs_window_ysize'] = NONUM
    return guide

def mk_common_meta():
    meta = {}
    meta['filename'] = NOSTR
    meta['date'] = time.Time('2020-01-01T00:00:00.0', format='isot', scale='utc')
    meta['telescope'] = 'ROMAN'
    meta['exposure'] = mk_exposure()
    meta['instrument'] = mk_wfi_mode()
    meta['observation'] = mk_observation()
    meta['program'] = mk_program()
    meta['ephemeris'] = mk_ephemeris()
    meta['visit'] = mk_visit()
    meta['photometry'] = mk_photometry()
    meta['coordinates'] = mk_coordinates()
    meta['aperture'] = mk_aperture()
    meta['pointing'] = mk_pointing()
    meta['target'] = mk_target()
    meta['velocity_aberration'] = mk_velocity_aberration()
    meta['wcsinfo'] = mk_wcsinfo()
    meta['cal_step'] = mk_cal_step()
    return meta

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
    instrument = {'name': 'WFI', 'detector': 'WFI01', 'optical_element': 'F158'}
    meta['telescope'] = 'ROMAN'
    meta['instrument'] = instrument
    meta['pedigree'] = 'test pedigree'
    meta['author'] = 'test system'
    meta['description'] = 'blah blah blah'
    meta['useafter'] = time.Time('2020-01-01T00:00:00.0', format='isot', scale='utc')
    meta['reftype'] = ''

def mk_flat(outfilepath):

    meta = {}
    add_ref_common(meta)
    flatref = stnode.FlatRef()
    meta['reftype'] = 'FLAT'
    flatref['meta'] = meta
    shape = (20, 20)
    flatref['data'] = np.zeros(shape, dtype=np.float32)
    flatref['dq'] = np.zeros(shape, dtype=np.uint32)
    flatref['err'] = np.zeros(shape, dtype=np.float32)
    af = asdf.AsdfFile()
    af.tree = {'roman': flatref}
    af.write_to(outfilepath)
