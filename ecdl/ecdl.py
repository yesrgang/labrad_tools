"""
### BEGIN NODE INFO
[info]
name = ecdl
version = 1.0
description = 
instancename = ecdl

[startup]
cmdline = %PYTHON% %FILE%
timeout = 20

[shutdown]
message = 987654321
timeout = 5
### END NODE INFO
"""
import sys

from labrad.server import Signal, setting
from twisted.internet.reactor import callLater
from twisted.internet.defer import returnValue

sys.path.append('../')
from server_tools.device_server import DeviceServer
from server_tools.decorators import quickSetting

UPDATE_ID = 698039

class ECDLServer(DeviceServer):
    update = Signal(UPDATE_ID, 'signal: update', 's')
    name = 'ecdl'

    @quickSetting(10, 'b')
    def state(self, c, state=None):
        """ get or change state """

    @quickSetting(11, 'v')
    def diode_current(self, c, frequency=None):
        """ get or change frequency """

    @quickSetting(12, 'v')
    def piezo_voltage(self, c, amplitude=None):
        """ get or change amplitude """
    
    @setting(13, warmup='b', returns='b')
    def warmup(self, c, warmup=True):
        device = self.get_selected_device(c)
        if warmup:
            yield device.warmup()
        returnValue(warmup)

    @setting(14, shutdown='b', returns='b')
    def shutdown(self, c, shutdown=True):
        device = self.get_selected_device(c)
        if shutdown:
            yield device.shutdown()
        returnValue(shutdown)

if __name__ == "__main__":
    from labrad import util
    util.runServer(ECDLServer())
