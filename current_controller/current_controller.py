"""
### BEGIN NODE INFO
[info]
name = gpib_current_controller
version = 1.0
description = 
instancename = gpib_current_controller

[startup]
cmdline = %PYTHON% %FILE%
timeout = 20

[shutdown]
message = 987654321
timeout = 5
### END NODE INFO
"""

from labrad.server import Signal, setting
from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet.reactor import callLater

from server_tools.device_server import DeviceServer

UPDATE_ID = 698027

class CurrentControllerServer(DeviceServer):
    """ Provides basic control for current controllers """
    update = Signal(UPDATE_ID, 'signal: update', 's')
    name = 'gpib_current_controller'

    @setting(13, warmup='b', returns='b')
    def warmup(self, c, warmup=True):
        device = self.get_device(c)
        if warmup:
            yield device.warmup()
        callLater(10, self.send_update, c)
        returnValue(warmup)

    @setting(14, shutdown='b', returns='b')
    def shutdown(self, c, shutdown=True):
        device = self.get_device(c)
        if shutdown:
            yield device.shutdown()
        callLater(10, self.send_update, c)
        returnValue(shutdown)

if __name__ == '__main__':
    from labrad import util
    util.runServer(CurrentControllerServer())
