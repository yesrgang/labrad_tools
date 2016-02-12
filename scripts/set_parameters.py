import labrad
import json
import numpy as np

sequence_parameters = {
    '*AIf':3,
    '*AIff':0.020,
    '*BIf':1,
    '*BIff':0.01,

    '*AHbm':-0.6,
    '*AHrm':-0.01,
    '*XCCrm': .53,
    '*XCCclk': .53,
    '*YCCrm': .0,
    '*YCCclk': .0,
    '*ZCCrm': .275,
    '*XCCclk': .275,
    'XCCimg': -10.,
    'YCCimg': -9.99,
    'ZCCimg': -10,
    '*ZCCbm':-5,
    '*ZCCi':-5,
    
    '*HODTi': -1.2,
    '*HODTm': -.688,
    '*HODTf': -.12,
    '*VODTi': -.2,
    '*VODTf': -.5,
    '*T1': 1.1,
    '*Tevap': 5.6,
    '*tau_1': -2.5,
    '*tau_2': -5,
    '*tau_3': 5,
    
    '*813H1f': -.4,
    '*813H2f': -.4,
    '*813Vf': -3,
    '*Iclk': -.03,
    
    "*Thold":0.001,
    '*kick':-1.2,
}


device_parameters = {
    'Clock AOM': {
        'frequency': {
            'init command': "self.client._33500b.select_device_by_name('clock steer')", 
            'command': "lambda value, self=self: self.client._33500b.frequency(value)",
            'value': 27.1177e6,
        },
    },
}

cxn = labrad.connect()
c = cxn.yesr20_conductor
c.update_sequence_parameters(json.dumps(sequence_parameters))
c.set_device_parameters(json.dumps(device_parameters))
