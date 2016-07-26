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

from labrad.server import Signal, setting

from server_tools.device_server import DeviceServer
from server_tools.decorators import quickSetting

UPDATE_ID = 698034

class RFServer(DeviceServer):
    """ Provides basic control for RF sources """
    update = Signal(UPDATE_ID, 'signal: update', 's')
    name = 'rf'

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

if __name__ == "__main__":
    from labrad import util
    util.runServer(RFServer())
