from . import stnode
import asdf
import astropy.time as time
import os.path

NONUM = -999999
NOSTR = "dummy value"


def mk_level2_image(filepath, outfilepath):
    '''
    Read in the tentative l2 image file that doesn't use tags
    and cast into a tagged version.
    '''
    afin = asdf.open(filepath)
    imeta = afin.tree['meta']
    exp = stnode.Exposure()
    exp['count'] = NONUM
    exp['type'] = NONUM
    exp['start_time'] = NONUM
    exp['mid_time'] = NONUM
    exp['end_time'] = NONUM
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
    # Fill from file
    for key in imeta['exposure'].keys():
        exp[key] = imeta['exposure'][key]

    mode = stnode.WfiMode()
    mode['name'] = NOSTR
    mode['detector'] = NOSTR
    mode['optical_element'] = NOSTR
    for key in imeta['instrument'].keys():
        mode[key] = imeta['instrument'][key]

    prog = stnode.Program()
    prog['title'] = NOSTR
    prog['pi_name'] = NOSTR
    prog['category'] = NOSTR
    prog['sub_category'] = NOSTR
    prog['science_category'] = NOSTR
    prog['continuation_id'] = NONUM
    for key in imeta['program'].keys():
        prog[key] = imeta['program'][key]

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
    for key in imeta['observation'].keys():
        obs[key] = imeta['observation'][key]

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
    for key in imeta['ephemeris'].keys():
        ephem[key] = imeta['ephemeris'][key]

    visit = stnode.Visit()
    visit['engineering_quality'] = 'OK'  # qqqq
    visit['pointing_engdb_quality'] = 'CALCULATED'  # qqqq
    visit['type'] = NOSTR
    visit['start_time'] = NOSTR
    visit['end_time'] = NOSTR
    visit['status'] = NOSTR
    visit['total_exposures'] = NONUM
    visit['internal_target'] = False
    for key in imeta['visit'].keys():
        visit[key] = imeta['visit'][key]

    phot = stnode.Photometry()
    phot['conversion_megajanskys'] = NONUM
    phot['conversion_microjanskys'] = NONUM
    phot['pixelarea_steradians'] = NONUM
    phot['pixelarea_arcsecsq'] = NONUM
    for key in imeta['photometry'].keys():
        phot[key] = imeta['photometry'][key]

    coord = stnode.Coordinates()
    coord['reference_frame'] = NOSTR
    for key in imeta['coordinates'].keys():
        coord[key] = imeta['coordinates'][key]

    aper = stnode.Aperture()
    aperlist = []
    aper['name'] = NOSTR
    aper['position_angle'] = NONUM
    for key in aperlist:
        aper[key] = imeta['aperture'][key]

    point = stnode.Pointing()
    point['ra_v1'] = NONUM
    point['dec_v1'] = NONUM
    point['pa_v3'] = NONUM
    for key in imeta['pointing'].keys():
        point[key] = imeta['pointing'][key]

    targ = stnode.Target()
    targ['proposer_name'] = NOSTR
    targ['catalog_name'] = NOSTR
    targ['type'] = NOSTR
    targ['ra'] = NONUM
    targ['dec'] = NONUM
    targ['ra_uncertainty'] = NONUM
    targ['dec_uncertainty'] = NONUM
    targ['proper_motion_ra'] = NONUM
    targ['proper_motion_dec'] = NONUM
    targ['proper_motion_epoch'] = NOSTR
    targ['proposer_ra'] = NONUM
    targ['proposer_dec'] = NONUM
    targ['source_type_apt'] = 'POINT'  # qqqq
    targ['source_type'] = 'POINT'  # qqqq
    for key in imeta['target'].keys():
        targ[key] = imeta['target'][key]

    vab = stnode.VelocityAberration()
    vab['ra_offset'] = NONUM
    vab['dec_offset'] = NONUM
    vab['scale_factor'] = NONUM
    for key in imeta['velocity_aberration'].keys():
        vab[key] = imeta['velocity_aberration'][key]

    wcsi = stnode.Wcsinfo()
    wcsi['v2_ref'] = NONUM
    wcsi['v3_ref'] = NONUM
    wcsi['vparity'] = NONUM
    wcsi['v3yangle'] = NONUM
    wcsi['ra_ref'] = NONUM
    wcsi['dec_ref'] = NONUM
    wcsi['roll_ref'] = NONUM

    # guide = stnode.Guidestar()
    # guide['gs_start_time'] = NOSTR
    # guide['gs_stop_time'] = NOSTR
    # guide['gs_id'] = NOSTR
    # guide['gs_ra'] = NONUM
    # guide['gs_dec'] = NONUM
    # guide['gs_ura'] = NONUM
    # guide['gs_udec'] = NONUM
    # guide['gs_mag'] = NONUM
    # guide['gs_umag'] = NONUM
    # guide['gs_pcs_mode'] = NOSTR
    # guide['gs_function_start_time'] = NOSTR
    # guide['gs_function_end_time'] =  NOSTR
    # guide['data_start'] = NONUM
    # guide['data_end'] = NONUM
    # guide['gs_acq_exec_stat'] = NOSTR
    # guide['gs_ctd_x'] = NONUM
    # guide['gs_ctd_y'] = NONUM
    # guide['gs_ctd_ux'] = NONUM
    # guide['gs_ctd_uy'] = NONUM
    # guide['gs_epoch'] = NOSTR
    # guide['gs_mura'] = NONUM
    # guide['gs_mudec'] = NONUM
    # guide['gs_para'] = NONUM
    # guide['gs_window_xstart'] = NONUM
    # guide['gs_window_ystart'] = NONUM
    # guide['gs_window_xsize'] = NONUM
    # guide['gs_window_ysize'] = NONUM
    # for key in imeta['guidestar'].keys():
    #   guide[key] = imeta['guidestar'][key]

    cstep = stnode.CalStep()
    cstep['flat_field'] = 'INCOMPLETE'

    meta = {}
    meta['filename'] = os.path.basename(outfilepath)
    meta['date'] = time.Time(imeta['date'], format='isot', scale='utc')
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
    #meta['guidestar'] = guide
    meta['cal_step'] = cstep
    wfi_image = stnode.WfiImage()
    wfi_image['meta'] = meta
    wfi_image['data'] = afin.tree['data']
    wfi_image['dq'] = afin.tree['dq']
    wfi_image['err'] = afin.tree['err']
    wfi_image['var_poisson'] = afin.tree['var_poisson']
    wfi_image['var_rnoise'] = afin.tree['var_rnoise']
    wfi_image['var_flat'] = afin.tree['var_rnoise'] * 0
    wfi_image['area'] = afin.tree['area']
    afout = asdf.AsdfFile()
    afout.tree = {'roman': wfi_image}
    afout.write_to(outfilepath)


def mk_flat(outfilepath):
    oldref = "/Users/perry/crds_cache/references/roman/wfi/roman_wfi_flat_0001.asdf"
    afoldref = asdf.open(oldref)
    afot = afoldref.tree
    wfimode = stnode.WfiMode()
    wfimode['name'] = 'WFI'
    wfimode['detector'] = 'WFI01'
    wfimode['optical_element'] = 'F158'
    meta = {}
    meta['telescope'] = 'ROMAN'
    meta['instrument'] = wfimode
    meta['reftype'] = 'FLAT'
    meta['pedigree'] = afot['meta']['pedigree']
    meta['description'] = afot['meta']['description']
    meta['author'] = afot['meta']['author']
    meta['useafter'] = afot['meta']['useafter']
    flatref = stnode.FlatRef()
    flatref['meta'] = meta

    flatref['data'] = afot['data']
    flatref['dq'] = afot['dq']
    flatref['err'] = afot['err']
    afout = asdf.AsdfFile()
    afout.tree = {'roman': flatref}
    afout.write_to(outfilepath)
