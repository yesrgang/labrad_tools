import labrad
import json
import numpy as np

filename = 'measure_trap_freq_vodt1500mV'
scan_parameters = {
    '*HODTi': -1.1,
    '*HODTf': -.5,
    '*Thold': np.arange(1e-3, 20e-3, .5e-3).tolist(),
    'description': '...'
}

cxn = labrad.connect()
c = cxn.yesr20_conductor
r = cxn.yesr20_receiver
c.update_sequence_parameters(json.dumps(scan_parameters))
r.record(filename, len(scan_parameters['*Thold']))
