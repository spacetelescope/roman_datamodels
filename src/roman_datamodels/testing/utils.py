import asdf
import astropy.time as time
import numpy as np

from .. import stnode

NONUM = -999999
NOSTR = "dummy value"


def mk_exposure():
    """
    Create a dummy Exposure instance with valid values for attributes
    required by the schema. Utilized by the model maker utilities below.

    Returns
    -------
    roman_datamodels.stnode.Exposure
    """
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
    """
    Create a dummy WFI mode instance with valid values for attributes
    required by the schema. Utilized by the model maker utilities below.

    Returns
    -------
    roman_datamodels.stnode.WfiMode
    """
    mode = stnode.WfiMode()
    mode['name'] = 'WFI'
    mode['detector'] = 'WFI01'
    mode['optical_element'] = 'F062'
    return mode


def mk_program():
    """
    Create a dummy Program instance with valid values for attributes
    required by the schema. Utilized by the model maker utilities below.

    Returns
    -------
    roman_datamodels.stnode.Program
    """
    prog = stnode.Program()
    prog['title'] = NOSTR
    prog['pi_name'] = NOSTR
    prog['category'] = NOSTR
    prog['subcategory'] = NOSTR
    prog['science_category'] = NOSTR
    prog['continuation_id'] = NONUM
    return prog


def mk_observation():
    """
    Create a dummy Observation instance with valid values for attributes
    required by the schema. Utilized by the model maker utilities below.

    Returns
    -------
    roman_datamodels.stnode.Observation
    """
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
    obs['template'] = NOSTR
    obs['observation_label'] = NOSTR
    obs['ma_table_name'] = NOSTR
    obs['survey'] = 'N/A'
    return obs


def mk_ephemeris():
    """
    Create a dummy Ephemeris instance with valid values for attributes
    required by the schema. Utilized by the model maker utilities below.

    Returns
    -------
    roman_datamodels.stnode.Ephemeris
    """
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
    """
    Create a dummy Visit instance with valid values for attributes
    required by the schema. Utilized by the model maker utilities below.

    Returns
    -------
    roman_datamodels.stnode.Visit
    """
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
    """
    Create a dummy Photometry instance with valid values for attributes
    required by the schema. Utilized by the model maker utilities below.

    Returns
    -------
    roman_datamodels.stnode.Photometry
    """
    phot = stnode.Photometry()
    phot['conversion_megajanskys'] = NONUM
    phot['conversion_microjanskys'] = NONUM
    phot['pixelarea_steradians'] = NONUM
    phot['pixelarea_arcsecsq'] = NONUM
    return phot


def mk_coordinates():
    """
    Create a dummy Coordinates instance with valid values for attributes
    required by the schema. Utilized by the model maker utilities below.

    Returns
    -------
    roman_datamodels.stnode.Coordinates
    """
    coord = stnode.Coordinates()
    coord['reference_frame'] = 'ICRS'
    return coord


def mk_aperture():
    """
    Create a dummy Aperture instance with valid values for attributes
    required by the schema. Utilized by the model maker utilities below.

    Returns
    -------
    roman_datamodels.stnode.Aperture
    """
    aper = stnode.Aperture()
    aper['name'] = NOSTR
    aper['position_angle'] = 30.
    return aper


def mk_pointing():
    """
    Create a dummy Pointing instance with valid values for attributes
    required by the schema. Utilized by the model maker utilities below.

    Returns
    -------
    roman_datamodels.stnode.Pointing
    """
    point = stnode.Pointing()
    point['ra_v1'] = NONUM
    point['dec_v1'] = NONUM
    point['pa_v3'] = NONUM
    return point


def mk_target():
    """
    Create a dummy Target instance with valid values for attributes
    required by the schema. Utilized by the model maker utilities below.

    Returns
    -------
    roman_datamodels.stnode.Target
    """
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
    """
    Create a dummy Velocity Aberration instance with valid values for attributes
    required by the schema. Utilized by the model maker utilities below.

    Returns
    -------
    roman_datamodels.stnode.VelocityAberration
    """
    vab = stnode.VelocityAberration()
    vab['ra_offset'] = NONUM
    vab['dec_offset'] = NONUM
    vab['scale_factor'] = NONUM
    return vab


def mk_wcsinfo():
    """
    Create a dummy WCS Info instance with valid values for attributes
    required by the schema. Utilized by the model maker utilities below.

    Returns
    -------
    roman_datamodels.stnode.Wcsinfo
    """
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
    """
    Create a dummy Cal Step instance with valid values for attributes
    required by the schema. Utilized by the model maker utilities below.

    Returns
    -------
    roman_datamodels.stnode.CalStep
    """
    calstep = stnode.CalStep()
    calstep['flat_field'] = 'INCOMPLETE'
    calstep['dq_init'] = 'INCOMPLETE'
    calstep['assign_wcs'] = 'INCOMPLETE'
    calstep['dark'] = 'INCOMPLETE'
    calstep['jump'] = 'INCOMPLETE'
    calstep['linearity'] = 'INCOMPLETE'
    calstep['ramp_fit'] = 'INCOMPLETE'
    calstep['saturation'] = 'INCOMPLETE'

    return calstep

def mk_cal_logs():
    """
    Create a dummy CalLogs instance with valid values for attributes
    required by the schema.

    Returns
    -------
    roman_datamodels.stnode.CalLogs
    """
    return stnode.CalLogs(
        [
            "2021-11-15T09:15:07.12Z :: FlatFieldStep :: INFO :: Completed",
            "2021-11-15T10:22.55.55Z :: RampFittingStep :: WARNING :: Wow, lots of Cosmic Rays detected",
        ]
    )

def mk_guide():
    """
    Create a dummy Guide Star instance with valid values for attributes
    required by the schema. Utilized by the model maker utilities below.

    Returns
    -------
    roman_datamodels.stnode.Guidestar
    """
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

def add_ref_common(meta):
    instrument = {'name': 'WFI', 'detector': 'WFI01',
                  'optical_element': 'F158'}
    meta['telescope'] = 'ROMAN'
    meta['instrument'] = instrument
    meta['origin'] = 'STSCI'
    meta['pedigree'] = 'GROUND'
    meta['author'] = 'test system'
    meta['description'] = 'blah blah blah'
    meta['useafter'] = time.Time(
        '2020-01-01T00:00:00.0', format='isot', scale='utc')
    meta['reftype'] = ''

def mk_level1_science_raw(shape=None, filepath=None):
    """
    Create a dummy level 1 ScienceRaw instance (or file) with arrays and valid values for attributes
    required by the schema.

    Parameters
    ----------
    shape
        (optional) Shape of arrays in the model.

    filepath
        (optional) File name and path to write model to.

    Returns
    -------
    roman_datamodels.stnode.WfiScienceRaw
    """
    meta = mk_common_meta()
    wfi_science_raw = stnode.WfiScienceRaw()
    wfi_science_raw['meta'] = meta

    if not shape:
        shape = (8, 4096, 4096)

    wfi_science_raw['data'] = np.zeros(shape, dtype=np.uint16)

    if filepath:
        af = asdf.AsdfFile()
        af.tree = {'roman': wfi_science_raw}
        af.write_to(filepath)
    else:
        return wfi_science_raw


def mk_level2_image(shape=None, filepath=None):
    """
    Create a dummy level 2 Image instance (or file) with arrays and valid values for attributes
    required by the schema.

    Parameters
    ----------
    shape
        (optional) Shape of arrays in the model.

    filepath
        (optional) File name and path to write model to.

    Returns
    -------
    roman_datamodels.stnode.WfiImage
    """
    meta = mk_common_meta()
    wfi_image = stnode.WfiImage()
    wfi_image['meta'] = meta

    if not shape:
        shape = (4096, 4096)

    wfi_image['data'] = np.zeros(shape, dtype=np.float32)
    wfi_image['dq'] = np.zeros(shape, dtype=np.uint32)
    wfi_image['err'] = np.zeros(shape, dtype=np.float32)
    wfi_image['var_poisson'] = np.zeros(shape, dtype=np.float32)
    wfi_image['var_rnoise'] = np.zeros(shape, dtype=np.float32)
    wfi_image['var_flat'] = np.zeros(shape, dtype=np.float32)
    wfi_image['area'] = np.zeros(shape, dtype=np.float32)
    wfi_image['cal_logs'] = mk_cal_logs()

    if filepath:
        af = asdf.AsdfFile()
        af.tree = {'roman': wfi_image}
        af.write_to(filepath)
    else:
        return wfi_image


def mk_flat(shape=None, filepath=None):
    """
    Create a dummy Flat instance (or file) with arrays and valid values for attributes
    required by the schema.

    Parameters
    ----------
    shape
        (optional) Shape of arrays in the model.

    filepath
        (optional) File name and path to write model to.

    Returns
    -------
    roman_datamodels.stnode.FlatRef
    """
    meta = {}
    add_ref_common(meta)
    flatref = stnode.FlatRef()
    meta['reftype'] = 'FLAT'
    flatref['meta'] = meta

    if not shape:
        shape = (4096, 4096)

    flatref['data'] = np.zeros(shape, dtype=np.float32)
    flatref['dq'] = np.zeros(shape, dtype=np.uint32)
    flatref['err'] = np.zeros(shape, dtype=np.float32)

    if filepath:
        af = asdf.AsdfFile()
        af.tree = {'roman': flatref}
        af.write_to(filepath)
    else:
        return flatref

def mk_dark(shape=None, filepath=None):
    """
    Create a dummy Dark instance (or file) with arrays and valid values for attributes
    required by the schema.

    Parameters
    ----------
    shape
        (optional) Shape of arrays in the model.

    filepath
        (optional) File name and path to write model to.

    Returns
    -------
    roman_datamodels.stnode.DarkRef
    """
    meta = {}
    add_ref_common(meta)
    darkref = stnode.DarkRef()
    meta['reftype'] = 'DARK'
    darkref['meta'] = meta
    observation = {}
    observation['ma_table_name']="ma_table.name"
    darkref['meta']['observation'] = observation
    exposure = {}
    exposure['type'] = 'WFI_IMAGE'
    darkref['meta']['exposure'] = exposure

    if not shape:
        shape = (2, 4096, 4096)

    darkref['data'] = np.zeros(shape, dtype=np.float32)
    darkref['dq'] = np.zeros(shape[1:], dtype=np.uint32)
    darkref['err'] = np.zeros(shape, dtype=np.float32)

    if filepath:
        af = asdf.AsdfFile()
        af.tree = {'roman': darkref}
        af.write_to(filepath)
    else:
        return darkref


def mk_gain(shape=None, filepath=None):
    """
    Create a dummy Gain instance (or file) with arrays and valid values for attributes
    required by the schema.

    Parameters
    ----------
    shape
        (optional) Shape of arrays in the model.

    filepath
        (optional) File name and path to write model to.

    Returns
    -------
    roman_datamodels.stnode.GainRef
    """
    meta = {}
    add_ref_common(meta)
    gainref = stnode.GainRef()
    meta['reftype'] = 'GAIN'
    gainref['meta'] = meta

    if not shape:
        shape = (4096, 4096)

    gainref['data'] = np.zeros(shape, dtype=np.float32)

    if filepath:
        af = asdf.AsdfFile()
        af.tree = {'roman': gainref}
        af.write_to(filepath)
    else:
        return gainref

def mk_linearity(shape=None, filepath=None):
    """
    Create a dummy Linearity instance (or file) with arrays and valid values for attributes
    required by the schema.

    Parameters
    ----------
    shape
        (optional) Shape of arrays in the model.

    filepath
        (optional) File name and path to write model to.

    Returns
    -------
    roman_datamodels.stnode.LinearityRef
    """
    meta = {}
    add_ref_common(meta)
    linearityref = stnode.LinearityRef()
    meta['reftype'] = 'LINEARITY'
    linearityref['meta'] = meta

    if not shape:
        shape = (2, 4096, 4096)

    linearityref['coeffs'] = np.zeros(shape, dtype=np.float32)
    linearityref['dq'] = np.zeros(shape[1:], dtype=np.uint32)

    if filepath:
        af = asdf.AsdfFile()
        af.tree = {'roman': linearityref}
        af.write_to(filepath)
    else:
        return linearityref


def mk_mask(shape=None, filepath=None):
    """
    Create a dummy Mask instance (or file) with arrays and valid values for attributes
    required by the schema.

    Parameters
    ----------
    shape
        (optional) Shape of arrays in the model.

    filepath
        (optional) File name and path to write model to.

    Returns
    -------
    roman_datamodels.stnode.MaskRef
    """
    meta = {}
    add_ref_common(meta)
    maskref = stnode.MaskRef()
    meta['reftype'] = 'MASK'
    maskref['meta'] = meta

    if not shape:
        shape = (4096, 4096)

    maskref['dq'] = np.zeros(shape, dtype=np.uint32)

    if filepath:
        af = asdf.AsdfFile()
        af.tree = {'roman': maskref}
        af.write_to(filepath)
    else:
        return maskref

def mk_pixelarea(shape=None, filepath=None):
    """
    Create a dummy Pixelarea instance (or file) with arrays and valid values for attributes
    required by the schema.

    Parameters
    ----------
    shape
        (optional) Shape of arrays in the model.

    filepath
        (optional) File name and path to write model to.

    Returns
    -------
    roman_datamodels.stnode.PixelareaRef
    """
    meta = {}
    add_ref_common(meta)
    pixelarearef = stnode.PixelareaRef()
    meta['reftype'] = 'AREA'
    meta['photometry'] = {
        'pixelarea_steradians': float(NONUM),
        'pixelarea_arcsecsq': float(NONUM),
    }
    pixelarearef['meta'] = meta

    if not shape:
        shape = (4096, 4096)

    pixelarearef['data'] = np.zeros(shape, dtype=np.float32)

    if filepath:
        af = asdf.AsdfFile()
        af.tree = {'roman': pixelarearef}
        af.write_to(filepath)
    else:
        return pixelarearef

def mk_wfi_img_photom(filepath=None):
    """
    Create a dummy WFI Img Photom instance (or file) with dictionary and valid values for attributes
    required by the schema.

    Parameters
    ----------
    filepath
        (optional) File name and path to write model to.

    Returns
    -------
    roman_datamodels.stnode.WfiImgPhotomRef
    """
    meta = {}
    add_ref_common(meta)
    wfi_img_photomref = stnode.WfiImgPhotomRef()
    meta['reftype'] = 'PHOTOM'
    wfi_img_photomref['meta'] = meta

    wfi_img_photo_dict = {
        "W146":
            {"photmjsr": (10 * np.random.random()),
             "uncertainty": np.random.random()},
        "F184":
            {"photmjsr": (10 * np.random.random()),
             "uncertainty": np.random.random()}
    }

    wfi_img_photomref['phot_table'] = wfi_img_photo_dict


    if filepath:
        af = asdf.AsdfFile()
        af.tree = {'roman': wfi_img_photomref}
        af.write_to(filepath)
    else:
        return wfi_img_photomref

def mk_readnoise(shape=None, filepath=None):
    """
    Create a dummy Readnoise instance (or file) with arrays and valid values for attributes
    required by the schema.

    Parameters
    ----------
    shape
        (optional) Shape of arrays in the model.

    filepath
        (optional) File name and path to write model to.

    Returns
    -------
    roman_datamodels.stnode.ReadnoiseRef
    """
    meta = {}
    add_ref_common(meta)
    readnoiseref = stnode.ReadnoiseRef()
    meta['reftype'] = 'READNOISE'
    readnoiseref['meta'] = meta
    exposure = {}
    exposure['type'] = 'WFI_IMAGE'
    readnoiseref['meta']['exposure'] = exposure

    if not shape:
        shape = (4096, 4096)

    readnoiseref['data'] = np.zeros(shape, dtype=np.float32)

    if filepath:
        af = asdf.AsdfFile()
        af.tree = {'roman': readnoiseref}
        af.write_to(filepath)
    else:
        return readnoiseref


def mk_ramp(shape=None, filepath=None):
    """
    Create a dummy Ramp instance (or file) with arrays and valid values for attributes
    required by the schema.

    Parameters
    ----------
    shape
        (optional) Shape of arrays in the model.

    filepath
        (optional) File name and path to write model to.

    Returns
    -------
    roman_datamodels.stnode.Ramp
    """
    meta = mk_common_meta()
    ramp = stnode.Ramp()
    ramp['meta'] = meta

    if not shape:
        shape = (8, 4096, 4096)

    ramp['data'] = np.full(shape, 1.0, dtype=np.float32)
    ramp['pixeldq'] = np.zeros(shape[1:], dtype=np.uint32)
    ramp['groupdq'] = np.zeros(shape, dtype=np.uint8)
    ramp['err'] = np.zeros(shape[1:], dtype=np.float32)

    if filepath:
        af = asdf.AsdfFile()
        af.tree = {'roman': ramp}
        af.write_to(filepath)
    else:
        return ramp

def mk_rampfitoutput(shape=None, filepath=None):
    """
    Create a dummy Rampfit Output instance (or file) with arrays and valid values for attributes
    required by the schema.

    Parameters
    ----------
    shape
        (optional) Shape of arrays in the model.

    filepath
        (optional) File name and path to write model to.

    Returns
    -------
    roman_datamodels.stnode.RampFitOutput
    """
    meta = mk_common_meta()
    rampfitoutput = stnode.RampFitOutput()
    rampfitoutput['meta'] = meta

    if not shape:
        shape = (8, 4096, 4096)

    rampfitoutput['slope'] = np.zeros(shape, dtype=np.float32)
    rampfitoutput['sigslope'] = np.zeros(shape, dtype=np.float32)
    rampfitoutput['yint'] = np.zeros(shape, dtype=np.float32)
    rampfitoutput['sigyint'] = np.zeros(shape, dtype=np.float32)
    rampfitoutput['pedestal'] = np.zeros(shape[1:], dtype=np.float32)
    rampfitoutput['weights'] = np.zeros(shape, dtype=np.float32)
    rampfitoutput['crmag'] = np.zeros(shape, dtype=np.float32)
    rampfitoutput['var_poisson'] = np.zeros(shape, dtype=np.float32)
    rampfitoutput['var_rnoise'] = np.zeros(shape, dtype=np.float32)

    if filepath:
        af = asdf.AsdfFile()
        af.tree = {'roman': rampfitoutput}
        af.write_to(filepath)
    else:
        return rampfitoutput


def mk_saturation(shape=None, filepath=None):
    """
    Create a dummy Saturation instance (or file) with arrays and valid values for attributes
    required by the schema.

    Parameters
    ----------
    shape
        (optional) Shape of arrays in the model.

    filepath
        (optional) File name and path to write model to.

    Returns
    -------
    roman_datamodels.stnode.SaturationRef
    """
    meta = {}
    add_ref_common(meta)
    saturationref = stnode.SaturationRef()
    meta['reftype'] = 'SATURATION'
    saturationref['meta'] = meta

    if not shape:
        shape = (4096, 4096)

    saturationref['data'] = np.zeros(shape, dtype=np.float32)
    saturationref['dq'] = np.zeros(shape, dtype=np.uint32)

    if filepath:
        af = asdf.AsdfFile()
        af.tree = {'roman': saturationref}
        af.write_to(filepath)
    else:
        return saturationref

def mk_superbias(shape=None, filepath=None):
    """
    Create a dummy Superbias instance (or file) with arrays and valid values for attributes
    required by the schema.

    Parameters
    ----------
    shape
        (optional) Shape of arrays in the model.

    filepath
        (optional) File name and path to write model to.

    Returns
    -------
    roman_datamodels.stnode.SuperbiasRef
    """
    meta = {}
    add_ref_common(meta)
    superbiasref = stnode.SuperbiasRef()
    meta['reftype'] = 'BIAS'
    superbiasref['meta'] = meta

    if not shape:
        shape = (4096, 4096)

    superbiasref['data'] = np.zeros(shape, dtype=np.float32)
    superbiasref['dq'] = np.zeros(shape, dtype=np.uint32)
    superbiasref['err'] = np.zeros(shape, dtype=np.float32)

    if filepath:
        af = asdf.AsdfFile()
        af.tree = {'roman': superbiasref}
        af.write_to(filepath)
    else:
        return superbiasref
