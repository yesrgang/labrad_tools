import json
import labrad
import numpy as np

cxn = labrad.connect()
conductor = cxn.yesr20_conductor
parameters = {
    'Y Comp. Coil': {
        'voltage': {
            'init command': "None", 
            'command': "lambda value, self=self: self.client.yesr20_analog_sequencer.channel_manual_voltage('Y Comp. Coil', value)",
            'value': np.arange(-.1, .1, .01).tolist(),
            },
        },
    }

print np.arange(-.1, .1, .01).tolist()
conductor.set_device_parameters(json.dumps(parameters))
