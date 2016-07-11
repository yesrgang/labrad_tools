"""
### BEGIN NODE INFO
[info]
name = stepper_device
version = 1.0
description = 
instancename = stepper_device

[startup]
cmdline = %PYTHON% %FILE%
timeout = 20

[shutdown]
message = 987654321
timeout = 20
### END NODE INFO
"""

from labrad.server import Signal, setting
from twisted.internet.defer import inlineCallbacks, returnValue

from server_toosl.device_server import DeviceServer

UPDATE_ID = 698021

class StepperMotorServer(DeviceServer):
    update = Signal(UPDATE_ID, 'signal: update', 's')

    @setting(10, 'move absolute', position='i', returns='b')
    def move_absolute(self, c, position=None):
        device = self.get_device(c)
        if position is not None:
            yield device.move_absolute(position)
        returnValue(device.position)

if __name__ == "__main__":
    from labrad import util
    util.runServer(StepperMotorServer())
