import json
import labrad

servo_config = {
    "test": {
        "pid_parameters": {
            'output': 27e6,
            'output_offset': 27e6,
        },
        "dither_parameters": {},
        "command": "lambda x: 0",
    },
}

conductor_config = {
    'clock_servo': {
        '9/2': {
            'init_commands': [
                "self.client.clock_servo.init_servo({})".format(
                    json.dumps(servo_config))
            ],
            'update_commands': [
                "lambda value: self.client.clock_servo.update({})".format(
                    json.dumps(self.data['gage']['exc'][-1]))
            ],
            'default_value': 'left',
        },
    },
}

cxn = labrad.connect()
cxn.clock_servo.init_servo(json.dumps(servo_config))
#cxn.yesr20_conductor.register_device(json.dumps(conductor_config))

