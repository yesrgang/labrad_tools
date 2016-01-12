import labrad
import json
import numpy as np

filename = 'Z:\\SrQ\\data\\20160108\\vodt_300mV'
scan_parameters = {
    '*HODTi': -.9,
    '*HODTf': -.2,
    '*Thold': np.arange(1e-3, 10e-3, .2e-3).tolist(),
}

cxn = labrad.connect()
c = cxn.yesr20_conductor
r = cxn.yesr20_receiver
c.update_sequence_parameters(json.dumps(scan_parameters))
r.record(filename, len(scan_parameters['*Thold']))
