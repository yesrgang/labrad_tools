import labrad
import json
import numpy as np

filename = 'evap'
vi_1 = -1.0
vf_1 = -.3
T_1 = 2.5
tau_1 = -T_1/2.
a = (vf_1-vi_1)/(np.exp(T_1/tau_1) - 1)
c = vi_1 - a

v_1 = np.linspace(vi_1, vf_1, 10)
T_l1 = tau_1 * np.log((v_1 - c)/a)

take_1 = -7
vi_2 = v_1[take_1]
vf_2 = -.14
T_2 = 5
tau_2 = -T_2/2.
a = (vf_2-vi_2)/(np.exp(T_2/tau_2) - 1)
c = vi_2 - a

v_2 = np.linspace(vi_2, vf_2, 10)
T_l2 = tau_2 * np.log((v_2 - c)/a)

vi_vert = -.2
vf_vert = -.2
v_vert = np.linspace(vi_vert, vf_vert, 10)

take = -1

scan_parameters = {
    '*HODTi': vi_1,
    '*HODTm': v_1[take_1],
    '*HODTf': v_2[1:].tolist()[take],
    '*T1': T_l1[take_1],
    '*Tevap': T_l2[1:].tolist()[take],
    '*tau_1': tau_1,
    '*tau_2': tau_2,
    '*tau_3': tau_2,
    '*VODTi': vi_vert,
    '*VODTf': v_vert[1:].tolist()[take], 
    'description': 'watch evaporation, new VODT waist (~60um)'
}

print scan_parameters['*T1'] + scan_parameters['*Tevap']

cxn = labrad.connect()
c = cxn.yesr20_conductor
r = cxn.yesr20_receiver
c.update_sequence_parameters(json.dumps(scan_parameters))
#r.record(filename, len(scan_parameters['*HODTf']))
