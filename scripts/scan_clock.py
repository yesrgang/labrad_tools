import labrad
import json
import numpy as np

filename = 'scan_clock'

c_freq = 27.05e6
f_range = 100e3
f_step = 1e3

freqs = np.arange(c_freq-f_range, c_freq + f_range, f_step)

f_start = 27.1173e6
f_range = 220e3
f_step = .1e3
f_stop = 27.1185e6
freqs = np.arange(f_start, f_stop, f_step)

device_parameters = {
    'Clock AOM': {
        'frequency': {
            'init command': "self.client._33500b.select_device_by_name('clock steer')", 
            'command': "lambda value, self=self: self.client._33500b.frequency(value)",
            'value': 27.1179e6 #freqs.tolist(),
            },
        },
    }

sequence_parameters = {
    '*813H1f': -2,
    '*813H2f': -2,
    '*Iclk': -.09,
}

cxn = labrad.connect()
c = cxn.yesr20_conductor
r = cxn.yesr20_receiver
c.set_device_parameters(json.dumps(device_parameters))
c.update_sequence_parameters(json.dumps(sequence_parameters))
#r.record(filename, len(device_parameters['Clock AOM']['frequency']['value']))
