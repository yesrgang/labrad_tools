import labrad
import json
import numpy as np

sequence_parameters = {
    "*AHbm":-0.6,
    "*AHrm":-0.01,
    "*AIf":3,
    "*AIff":0.020,
    "*BIf":1,
    "*BIff":0.01,
    "*HODTf":-.7,
    "*HODTi":-.8,
    "*Tevap":20,
    "*Thold":0.001,
    "*VODTf":-2,
    "*VODTi":-2.8,
    "*ZCCbm":-5,
    "*ZCCi":-5,
    "*ZCCrm":.295,
    "ZCCimg": -10,
    "*YCCrm":-.03,
    "YCCimg": -9.9,
    "*kick":-1.2,
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
