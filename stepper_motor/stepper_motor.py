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
import sys

from labrad.server import Signal, setting
from twisted.internet.defer import inlineCallbacks, returnValue

from server_tools.device_server import DeviceServer

UPDATE_ID = 698021

class StepperMotorServer(DeviceServer):
    update = Signal(UPDATE_ID, 'signal: update', 's')
    name = 'stepper_motor'

    @setting(10, 'move absolute', position='i', returns='i')
    def move_absolute(self, c, position=None):
        device = self.get_selected_device(c)
        if position is not None:
            yield device.move_absolute(position)
        returnValue(position)

    @setting(11, position1='i', position2='i')
    def toggle_absolute(self, c, position1=None, position2=None):
        device = self.get_selected_device(c)
        if (position1 is not None) and (position2 is not None):
            yield device.toggle_absolute(position1, position2)
        else:
            raise Exception('must specify two positions')

if __name__ == "__main__":
    from labrad import util
    util.runServer(StepperMotorServer())
