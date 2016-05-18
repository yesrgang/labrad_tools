import json
import numpy as np

import labrad

pid_config = {
    "test": {
        "parameters": {
            'output': 27e6,
            'output_offset': 27e6,
            'data_path': ('gage', 'exc'),
        },
        "command": "lambda: {'gage': {'exc': np.random.rand()}}",
    },
}

dither_config = {
    "test": {
        "parameters": {
        },
        "command": "lambda x: x",
    },
}

conductor_config = {
    'clock_servo': {
        'pid': {
            'init_commands': [
                "self.client.clock_servo.init_pid({})".format(
                    json.dumps(pid_config))
            ],
            'update_commands': [
                "lambda value: self.client.clock_servo.update({}).format(\
                    .format(json.dumps({value[0]: value[1]}))",
            ],
            'default_value': (None, None)
        },
        'dither': {
            'init_commands': [
                "self.client.clock_servo.init_dither({})".format(
                    json.dumps(dither_config))
            ],
            'update_commands': [
                "lambda value: self.client.clock_servo.advance({})\
                    .format(json.dumps({value[0]: value[1]}))",
            ],
            'default_value': (None, None)
        },

    },
}

cxn = labrad.connect()
s = cxn.clock_servo
s.init_pid(json.dumps(pid_config))
s.init_dither(json.dumps(dither_config))
#cxn.yesr20_conductor.register_device(json.dumps(conductor_config))

l = json.dumps({'test': 'left'})
r = json.dumps({'test': 'right'})
for i in range(1000):
    s.update(l)
    s.advance(r)
    s.update(r)
    s.advance(l)

