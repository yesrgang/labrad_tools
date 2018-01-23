"""
### BEGIN NODE INFO
[info]
name = picomotor
version = 1.0
description = 
instancename = picomotor

[startup]
cmdline = %PYTHON% %FILE%
timeout = 20

[shutdown]
message = 987654321
timeout = 5
### END NODE INFO
"""
from labrad.server import Signal, setting
from twisted.internet.defer import DeferredLock, returnValue

from server_tools.device_server import DeviceServer
from server_tools.decorators import quickSetting

UPDATE_ID = 699043

class PicomotorServer(DeviceServer):
    """
    picomotor LabRAD server
    """
    update = Signal(UPDATE_ID, 'signal: update', 's')
    name = 'picomotor'
    
#    @setting(11, position='i', returns='i')
#    def position(self, c, position=None):
#        """ get or set position """
#        device = self.get_device(c)
#        if position is not None:
#            yield device.set_position(position)
#        device.position = yield device.get_position()
#        yield self.send_update(c)
#        returnValue(device.position)
    
    @quickSetting(11, 'i')
    def position(self, c, position=None):
        """ get or set position """
    
if __name__ == '__main__':
    from labrad import util
    util.runServer(PicomotorServer())
