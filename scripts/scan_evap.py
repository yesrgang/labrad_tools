import labrad
import json
import numpy as np

filename = 'evap_rampVODT1000mV'
vi = -1.2
vf = -.17
T = 10.
tau = -5
a = (vf-vi)/(np.exp(T/tau) - 1)
c = vi - a

v = np.linspace(vi, vf, 20)
print v[-7]
T_list = tau * np.log((v - c)/a)
print T_list[-7]

vi_vert = -.2
vf_vert = -1
v_vert = np.linspace(vi_vert, vf_vert, 20)

scan_parameters = {
    '*HODTi': vi,
    '*tau': tau,
    '*Tevap': T_list[1:].tolist()[-1],
    '*HODTf': v[1:].tolist()[-1],
    '*VODTi': -.2,
    '*VODTf': v_vert[1:].tolist()[-1], 
    'description': 'watch evaporation, new VODT waist (~60um)'
}

cxn = labrad.connect()
c = cxn.yesr20_conductor
r = cxn.yesr20_receiver
#c.update_sequence_parameters(json.dumps(scan_parameters))
#r.record(filename, len(scan_parameters['*HODTf']))
