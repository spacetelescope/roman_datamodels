from . import stnode
from astropy.time import Time
import numpy as np


def mk_test_object():
    exp = stnode.Exposure()
    exp['type'] = "WFI_CORON"
    exp['readpatt'] = "RAPID"
    exp['start_time'] = Time('2020-11-11T11:11:11.11')
    exp['end_time'] = Time('2020-11-11T11:21:11.11')
    exp['nints'] = 5
    exp['ngroups'] = 2
    exp['nframes'] = 99
    exp['groupgap'] = 1
    exp['frame_time'] = 5.0
    exp['group_time'] = 20
    exp['exposure_time'] = 1000.
    wfi = stnode.Wfi()
    wfi['name'] = 'WFI'
    wfi['detector'] = 'WFI01'
    wfi['optical_element'] = 'GRISM'
    wfi['dummy_data'] = np.arange(10)
    rd = stnode.WfiImage()
    rd['meta'] = {}
    rd['meta']['filename'] = 'bozo.asdf'
    rd['meta']['telescope'] = 'Roman'
    # return rd, exp, wfi
    rd['meta']['exposure'] = exp
    rd['meta']['instrument'] = wfi
    return rd


def mk_test2():
    exp = stnode.Exposure()
    exp['count'] = 10
    exp['type'] = 'WFI_IMAGE'
    exp['start_time'] = 1001.5
    exp['mid_time'] = 1002.
    exp['end_time'] = 1002.5
    exp['start_time_mjd'] = 9999.0
    exp['mid_time_mjd'] = 9999.1
    exp['end_time_mjd'] = 9999.2
    exp['start_time_tdb'] = 1002
    exp['mid_time_tdb'] = 1002.5
    exp['end_time_tdb'] = 10003
    exp['start_time_eng'] = "2000."
    exp['ngroups'] = 10
    exp['nframes'] = 6
    exp['data_problem'] = False
    exp['gain_factor'] = 1
    exp['integration_time'] = 10
    exp['elapsed_exposure_time'] = 100
    exp['nints'] = 10
    exp['integration_start'] = 1
    exp['integration_end'] = 9
    exp['frame_divisor'] = 1
    exp['groupgap'] = 0
    exp['nsamples'] = 16
    exp['sample_time'] = 1
    exp['frame_time'] = 5
    exp['group_time'] = 2
    exp['exposure_time'] = 100
    exp['effective_exposure_time'] = 100
    exp['duration'] = 100
    exp['nresets_at_start'] = 0

    mode = stnode.WfiMode()
    mode['name'] = 'WFI'
    mode['detector'] = 'WFI07'
    mode['optical_element'] = 'GRISM'

    prog = stnode.Program()
    prog['title'] = 'Finding Nemo'
    prog['pi_name'] = 'Ivan the Terrible'
    prog['category'] = 'deep sea'
    prog['sub_category'] = 'fish'
    prog['science_category'] = 'biology'
    prog['continuation_id'] = 7

    obs = stnode.Observation()
    obs['date'] = 'Halloween'
    obs['time'] = 'Midnight'
    obs['date_beg'] = 'Halloween'
    obs['date_end'] = 'Halloween'
    obs['obs_id'] = 'Freddie'
    obs['visit_id'] = 'creepy 1'
    obs['program_number'] = '13'
    obs['execution_plan_number'] = 'chainsaw'
    obs['pass_number'] = '14'
    obs['leg_number'] = '2'
    obs['observation_number'] = '2'
    obs['visit_number'] = '1'
    obs['visit_group'] = '1'
    obs['activity_id'] = 'scary'
    obs['exposure_number'] = '223'
    obs['template'] = 'sequel'
    obs['observation_label'] = 'Friday the 13th'
    obs['observation_folder'] = 'APT folder'
    obs['ma_table_name'] = 'round table'

    ephem = stnode.Ephemeris()
    ephem['earth_angle'] = 179.2
    ephem['moon_angle'] = 170.1
    ephem['sun_angle'] = 169.9
    ephem['type'] = 'Definitive'
    ephem['time'] = 111.5
    ephem['spatial_x'] = 100000.
    ephem['spatial_y'] = 3.5
    ephem['spatial_z'] = -77
    ephem['velocity_x'] = 1.2
    ephem['velocity_y'] = 1.9
    ephem['velocity_z'] = -3.14

    visit = stnode.Visit()
    visit['engineering_quality'] = 'OK'
    visit['pointing_engdb_quality'] = 'CALCULATED'
    visit['type'] = 'summer vacation'
    visit['start_time'] = 'memorial day'
    visit['end_time'] = 'labor day'
    visit['status'] = 'wunderbar'
    visit['total_exposures'] = 7
    visit['internal_target'] = False

    phot = stnode.Photometry()
    phot['conversion_megajanskys'] = 2
    phot['conversion_microjanskys'] = 2e12
    phot['pixelarea_steradians'] = 1e-15
    phot['pixelarea_arcsecsq'] = 1e-4

    coord = stnode.Coordinates()
    coord['reference_frame'] = 'ICRS'

    aper = stnode.Aperture()
    aper['name'] = 'The big one'
    aper['position_angle'] = 90.

    point = stnode.Pointing()
    point['ra_v1'] = 10.
    point['dec_v1'] = -15.
    point['pa_v3'] = 271.

    targ = stnode.Target()
    targ['proposer_name'] = 'Bozo'
    targ['catalog_name'] = 'Clown tricks'
    targ['type'] = 'circus'
    targ['ra'] = 12.3
    targ['dec'] = -10
    targ['ra_uncertainty'] = 0.1
    targ['dec_uncertainty'] = 0.1
    targ['proper_motion_ra'] = 0.001
    targ['proper_motion_dec'] = 0.0005
    targ['proper_motion_epoch'] = '2000'
    targ['proposer_ra'] = 17.1
    targ['proposer_dec'] = -89.
    targ['source_type_apt'] = 'EXTENDED'
    targ['source_type'] = 'EXTENDED'

    vab = stnode.VelocityAberration()
    vab['ra_offset'] = 0.0001
    vab['dec_offset'] = 0.0001
    vab['scale_factor'] = 1.000001

    wcsi = stnode.Wcsinfo()
    wcsi['v2_ref'] = 250.
    wcsi['v3_ref'] = 300.
    wcsi['vparity'] = 1
    wcsi['v3yangle'] = 25.
    wcsi['ra_ref'] = 10.3
    wcsi['dec_ref'] = 23.5
    wcsi['roll_ref'] = 120.

    # guide = stnode.Guidestar()
    # guide['gs_start_time'] = 'tomorrow'
    # guide['gs_stop_time'] = 'end of the universe'
    # guide['gs_id'] = 'last guide star'
    # guide['gs_ra'] = 8
    # guide['gs_dec'] = 55
    # guide['gs_ura'] = 0.01
    # guide['gs_udec'] = .01
    # guide['gs_mag'] = -19
    # guide['gs_umag'] = 0.5
    # guide['gs_pcs_mode'] = 'wild guessing'
    # guide['gs_function_start_time'] = 'yesterday'
    # guide['gs_function_end_time'] =  'today'
    # guide['data_start'] = 99
    # guide['data_end'] = 111
    # guide['gs_acq_exec_stat'] = 'fantastic'
    # guide['gs_ctd_x'] = 25
    # guide['gs_ctd_y'] = 25
    # guide['gs_ctd_ux'] = 0.01
    # guide['gs_ctd_uy'] = 0.01
    # guide['gs_epoch'] = '2000'
    # guide['gs_mura'] = 0.0001
    # guide['gs_mudec'] = 0.0001
    # guide['gs_para'] = 0.2
    # guide['gs_window_xstart'] = 100
    # guide['gs_window_ystart'] = 100
    # guide['gs_window_xsize'] = 50
    # guide['gs_window_ysize'] = 50

    meta = {}
    meta['filename'] = 'bozo.asdf'
    meta['date'] = Time(
        '1999-01-01T00:00:00.123456789', format='isot', scale='utc')
    meta['exposure'] = exp
    meta['instrument'] = mode
    meta['observation'] = obs
    meta['program'] = prog
    meta['ephemeris'] = ephem
    meta['visit'] = visit
    meta['photometry'] = phot
    meta['coordinates'] = coord
    meta['aperture'] = aper
    meta['pointing'] = point
    meta['target'] = targ
    meta['velocity_aberration'] = vab
    meta['wcsinfo'] = wcsi
    # meta['guidestar'] = guide
    wfi = stnode.WfiScienceRaw()
    wfi['meta'] = meta
    wfi['data'] = np.zeros((100, 100, 10, 1), dtype=np.uint16)
    return wfi
