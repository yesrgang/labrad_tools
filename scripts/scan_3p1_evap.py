import labrad
import json
import numpy as np

filename = 'scan_3P1'
vi_1 = -1.2
vf_1 = -.3
T_1 = 2
tau_1 = -5
a = (vf_1-vi_1)/(np.exp(T_1/tau_1) - 1)
c = vi_1 - a

v_1 = np.linspace(vi_1, vf_1, 20)
T_l1 = tau_1 * np.log((v_1 - c)/a)
print T_l1[-7]

vi_2 = v_1[-7]
vf_2 = -.2
T_2 = 20.
tau_2 = -10
a = (vf_2-vi_2)/(np.exp(T_2/tau_2) - 1)
c = vi_2 - a

v_2 = np.linspace(vi_2, vf_2, 20)
T_l2 = tau_2 * np.log((v_2 - c)/a)



vi_vert = -.2
vf_vert = -.2
v_vert = np.linspace(vi_vert, vf_vert, 20)

scan_parameters = {
    '*HODTi': vi_1,
    '*HODTm': v_1[-7],
    '*HODTf': v_2[1:].tolist()[1],
    '*T1': T_l1[-7],
    '*Tevap': T_l2[1:].tolist()[1],
    '*tau_1': tau_1,
    '*tau_2': tau_2,
    '*VODTi': vi_vert,
    '*VODTf': v_vert[1:].tolist()[1], 
    '*ZCCimg': -10,
    '*ZCCrm': .275,
    '*YCCimg': -9,
    '*YCCrm': -.03,
}

device_parameters = {
    'Spin Pol. AOM': {
        'frequency': {
            'init command': "self.client.ds345.select_device_by_name('Spin Pol. AOM')",
            'command': "lambda value, self=self: self.client.ds345.frequency(value)",
            'value': np.arange(19.4e6, 20.6e6, .01e6).tolist(),
        }
    }
}

cxn = labrad.connect()
c = cxn.yesr20_conductor
r = cxn.yesr20_receiver
c.update_sequence_parameters(json.dumps(scan_parameters))
c.set_device_parameters(json.dumps(device_parameters))
r.record(filename, len(device_parameters['Spin Pol. AOM']['frequency']['value']))
