from . import stnode
import astropy.time as time
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
    #return rd, exp, wfi
    rd['meta']['exposure'] = exp
    rd['meta']['instrument'] = wfi
    return rd
    
def mk_test2():
    exp = stnode.Exposure()
    exp['count'] = 10
    exp['type'] = 'WFI_IMAGE'
    exp['start_time'] = 1001.5
    exp['mid_time'] =   1002.
    exp['end_time'] =   1002.5
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

    meta = {}
    meta['filename'] = 'bozo.asdf'
    meta['date'] = time.Time('1999-01-01T00:00:00.123456789', format='isot', scale='utc')
    meta['exposure'] = exp
    meta['instrument'] = mode
    wfi = stnode.WfiScienceRaw()
    wfi['meta'] = meta
    return wfi 