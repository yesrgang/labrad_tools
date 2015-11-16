import json
import numpy as np
import time

import labrad

waveform = {
            'channel name': 'alpha fm', 
            'name': 'test', 
            'sample rate': 1e5,
            'points': np.linspace(0, 1, 1e4).tolist(),
           }

cxn = labrad.connect()
awg = cxn.AG33522A
awg.program_waveform(json.dumps(waveform))
