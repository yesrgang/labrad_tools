import json
import numpy as np
import time

import labrad
import matplotlib.pyplot as plt

SAMPLE_RATE = 5e6/4 # [Hz]

waveform = {
            'channel name': 'alpha fm', 
            'name': 'test', 
            'sample rate': SAMPLE_RATE,
           }

times = [('T_cap', 50e-3), ('T_bb', 400e-3), ('T_sf', 200e-3), ('T_load', 50e-3)]
T_list = np.arange(0, sum([t for n, t in times]), 1/SAMPLE_RATE)
T = {
     'cap': (0, 50e-3),
     'bb': (50e-3, 400e-3),
     'sf': (450e-3, 200e-3),
     'load': (650e-3, 50e-3),
     }

fmod = 36e3

def H(x):
    """
    step function
    """
    return 0.5*(np.sign(x-1e-9)+1)

def G(T):
    """
    pulse
    """
    return lambda t: H(T[0]+T[1]-t) - H(T[0]-t) 

mod = lambda t: (.5 - .5 * np.cos(2*np.pi*fmod*t))

v = lambda t: mod(t) * ( G(T['cap'])(t) * 1  + G(T['bb'])(t) * (T['bb'][1] + T['bb'][0] - t) / T['bb'][1] + G(T['sf'])(t) * 0. + G(T['load'])(t)*0.)

waveform['points'] = v(T_list).tolist()
plt.plot(T_list, waveform['points'])
plt.show()


#cxn = labrad.connect()
#awg = cxn.AG33522A
#awg.program_waveform(json.dumps(waveform))
