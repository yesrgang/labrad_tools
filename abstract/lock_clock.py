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
            'init commands': [
                "self.client.clock_servo.init_pid({})".format(
                    json.dumps(pid_config))
            ],
            'update commands': [
                "lambda value: self.client.clock_servo.update({}).format(\
                    .format(json.dumps({value[0]: value[1]}))",
            ],
            'default_value': (None, None)
        },
        'dither': {
            'init commands': [
                "self.client.clock_servo.init_dither({})".format(
                    json.dumps(dither_config))
            ],
            'update commands': [
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

lock_points = [('9/2', 'left'), ('9/2', 'left')]
loop = Loop(
    name='clock lock',
    parameters=conductor_config,
    loop=1,
)

loop.start()
