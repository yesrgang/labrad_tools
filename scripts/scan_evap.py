import labrad
import json
import numpy as np

filename = 'Z:\\SrQ\\data\\20160108\\evap'
vi = -1.1
vf = -.14
T = 20.
tau = -10
a = (vf-vi)/(np.exp(T/tau) - 1)
c = vi - a

v = np.linspace(vi, vf, 20)
T_list = tau * np.log((v - c)/a)
print T_list

scan_parameters = {
    '*HODTi': vi,
    '*tau': tau,
    '*Tevap': T_list[1:].tolist(),
    '*HODTf': v[1:].tolist(),
    'description': 'watch evaporation, VODT at 2.8V ->2V'
}

cxn = labrad.connect()
c = cxn.yesr20_conductor
r = cxn.yesr20_receiver
c.update_sequence_parameters(json.dumps(scan_parameters))
r.record(filename, len(scan_parameters['*HODTf']))
