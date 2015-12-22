import json
import labrad

cxn = labrad.connect()
conductor = cxn.vagabond_conductor
parameters = {
    'Spin Pol. AOM': {
        'frequency': {
            'init command': "self.client.ds345.select_device_by_name('Spin Pol. AOM')", 
            'command': "lambda value, self=self: self.client.ds345.frequency(value)",
            'value': [20.115e6, 20.116e6, 20.117e6],
            },
        'amplitude': {
            'init command': "self.client.ds345.select_device_by_name('Spin Pol. AOM')", 
            'command': "lambda value, self=self: self.client.ds345.amplitude(value)",
            'value': [6, 6.01, 5.99],
            },
        },
    }

conductor.set_device_parameters(json.dumps(parameters))

