"""
### BEGIN NODE INFO
[info]
name = msquared
version = 1.0
description = 
instancename = msquared

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

sys.path.append('../')
from server_tools.device_server import DeviceServer
from server_tools.decorators import quickSetting

UPDATE_ID = 698043

class MSquaredServer(DeviceServer):
    """
    M-squared LabRAD server
    """
    update = Signal(UPDATE_ID, 'signal: update', 's')
    name = 'msquared'
    
    @quickSetting(10, 's')
    def system_status(self, c, status=None):
        """ get system status """

    @quickSetting(11, 'b')
    def etalon_lock(self, c, state=None):
        """ get or set etalon lock state """
    
    @quickSetting(12, 'v')
    def etalon_tune(self, c, percentage=None):
        """ get or set etalon tune percentage """

    @quickSetting(13, 'v')
    def resonator_tune(self, c, percentage=None):
        """ get or set resonator tune percentage """

    @quickSetting(14, 'v')
    def resonator_fine_tune(self, c, percentage=None):
        """ get or set resonator fine tune percentage """

if __name__ == '__main__':
    from labrad import util
    util.runServer(MSquaredServer())
