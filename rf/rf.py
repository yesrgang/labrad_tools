"""
### BEGIN NODE INFO
[info]
name = rf
version = 1.0
description = 
instancename = rf

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
from twisted.internet.defer import returnValue

sys.path.append('../')
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
    def frequency(self, c, frequency=None):
        """ get or change frequency """

    @quickSetting(12, 'v')
    def amplitude(self, c, amplitude=None):
        """ get or change amplitude """

    @quickSetting(13, 'v')
    def ramprate(self, c, ramprate=None):
        """ get or change ramprate """
    
    @quickSetting(14, 'v')
    def offset(self, c, offset=None):
        """ get or change offset """
    
    @setting(17, x='v', y='v', z='i')
    def linear_ramp(self, c, x=None, y=None, z=None):
        device = self.get_selected_device(c)
        yield device.set_linear_ramp(x, y, z)

#    @setting(18, z='i')
#    def linear_ramp_rate(self, c, z=None):
#        device = self.get_selected_device(c)
#        yield device.set_linear_ramp(None, None, z)


if __name__ == "__main__":
    from labrad import util
    util.runServer(RFServer())
