"""
### BEGIN NODE INFO
[info]
name = stepper_motor
version = 1.0
description = 
instancename = stepper_motor

[startup]
cmdline = %PYTHON% %FILE%
timeout = 20

[shutdown]
message = 987654321
timeout = 20
### END NODE INFO
"""

import json

import labrad.types as T
from labrad.server import Signal, setting
from labrad.types import Error
from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks, returnValue

from serial_device_server import SerialDeviceServer

UPDATE_ID = 698021

class StepperMotorServer(SerialDeviceServer):
    update = Signal(UPDATE_ID, 'signal: update', 's')
    def __init__(self, config_name):
        SerialDeviceServer.__init__(self)
        self.config_name = config_name
        self.load_configuration()

    def load_configuration(self):
        config = __import__(self.config_name).StepperMotorConfig()
        for key, value in config.__dict__.items():
            setattr(self, key, value)
    
    @setting(20, 'select device by name', name='s', returns='b')
    def select_device_by_name(self, c, name):
        c['name'] = name
        motor = self.motors[name]
        if not motor.serial_connection:
            params = dict(motor.__dict__)
            params.pop('serial_server_name')
            params.pop('port')
            motor.serial_connection = yield self.init_serial(
                motor.serial_server_name,
                motor.port,
                **params
            )
        for command in motor.init_commands:
            yield motor.serial_connection.write(command)
            ans = yield motor.serial_connection.read_line()

        returnValue(True)

    @setting(21, 'move absolute', position='i', returns='b')
    def move_absolute(self, c, position=None):
        motor = self.motors[c['name']]
        write_str = motor.move_absolute_str(position)
        yield motor.serial_connection.write(write_str)
        ans = yield motor.serial_connection.read_line()
        if ans:
            returnValue(True)
        else:
            returnValue(False)

if __name__ == "__main__":
    from labrad import util
    config_name = 'stepper_motor-config'
    util.runServer(StepperMotorServer(config_name))
