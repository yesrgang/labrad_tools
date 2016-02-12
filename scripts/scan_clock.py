import labrad
import json
import numpy as np

filename = 'scan_clock'

c_freq = 27.1346e6 #- 34e3
f_range = 4e3
f_step = .5e3

freqs = np.arange(c_freq-f_range, c_freq + f_range, f_step)

device_parameters = {
    'Clock AOM': {
        'frequency': {
            'init command': "self.client._33500b.select_device_by_name('clock steer')", 
            'command': "lambda value, self=self: self.client._33500b.frequency(value)",
#            'value': c_freq
            'value': freqs.tolist(),
            },
        },
    }

sequence_parameters = {
    '*813H1f': -1,
    '*813H2f': -1,
    '*813Vf': -.2,
    '*Iclk': -8,
}

cxn = labrad.connect()
c = cxn.yesr20_conductor
r = cxn.yesr20_receiver
c.set_device_parameters(json.dumps(device_parameters))
c.update_sequence_parameters(json.dumps(sequence_parameters))
#r.record(filename, len(device_parameters['Clock AOM']['frequency']['value']))
