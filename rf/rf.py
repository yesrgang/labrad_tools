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
    def frequency(self, c, frequency=None):
        """ get or change frequency """

    @quickSetting(12, 'v')
    def amplitude(self, c, amplitude=None):
        """ get or change amplitude """

    @quickSetting(13, 'v')
    def ramprate(self, c, ramprate=None):
        """ get or change ramprate """

if __name__ == "__main__":
    from labrad import util
    util.runServer(RFServer())
