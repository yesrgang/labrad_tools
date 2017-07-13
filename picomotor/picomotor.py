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

import sys

from labrad.server import Signal, setting

sys.path.append('../')
from server_tools.device_server import DeviceServer
from server_tools.decorators import quickSetting

UPDATE_ID = 699043

class PicomotorServer(DeviceServer):
    """
    picomotor LabRAD server
    """
    update = Signal(UPDATE_ID, 'signal: update', 's')
    name = 'picomotor'
    
    @quickSetting(11, 'i')
    def position(self, c, position=None):
        """ get or set position """
    
if __name__ == '__main__':
    from labrad import util
    util.runServer(PicomotorServer())
