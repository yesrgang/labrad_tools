import json
import labrad
import numpy as np

cxn = labrad.connect()
conductor = cxn.yesr20_conductor
parameters = {
#    'Spin Pol. AOM': {
#        'frequency': {
#            'init command': "self.client.ds345.select_device_by_name('Spin Pol. AOM')", 
#            'command': "lambda value, self=self: self.client.ds345.frequency(value)",
#            'value': [20.115e6, 20.116e6, 20.117e6],
#            },
#        'amplitude': {
#            'init command': "self.client.ds345.select_device_by_name('Spin Pol. AOM')", 
#            'command': "lambda value, self=self: self.client.ds345.amplitude(value)",
#            'value': [6, 6.01, 5.99],
#            },
#        },
    'Z Comp. Coil': {
        'voltage': {
            'init command': "None", 
            'command': "lambda value, self=self: self.client.yesr20_analog_sequencer.channel_manual_voltage('Z Comp. Coil', value)",
            'value': .313,
            },
        },
    }

conductor.set_device_parameters(json.dumps(parameters))

