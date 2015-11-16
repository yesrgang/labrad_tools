import json
import numpy as np
import time

import labrad

SAMPLE_RATE = 100e3 # [Hz]
MODULATION_FREQUENCY = 30e3 # [Hz]

waveform = {
            'channel name': 'alpha fm', 
            'name': 'test', 
            'sample rate': 1e5,
            'points': np.linspace(0, 1, 1e4).tolist(),
           }

times = [('T_cap', 50e-3), ('T_bb', 400e-3), ('T_sf', 200e-3), ('T_load', 50e-3)]


T = np.arange(0, sum([t for n, t in times]), 1/SAMPLE_RATE)

cxn = labrad.connect()
awg = cxn.AG33522A
#awg.program_waveform(json.dumps(waveform))
