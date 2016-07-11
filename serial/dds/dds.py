"""
### BEGIN NODE INFO
[info]
name = dds
version = 1.0
description = 
instancename = dds

[startup]
cmdline = %PYTHON% %FILE%
timeout = 10

[shutdown]
message = 987654321
timeout = 10
### END NODE INFO
"""

import sys

from labrad.server import Signal, setting

sys.path.append('../../')
from serial.serial_device_server import SerialDeviceServer
from extras.decorators import quickSetting

UPDATE_ID = 698063

class DDSServer(SerialDeviceServer):
    name = 'dds'
    update = Signal(UPDATE_ID, 'signal: update', 's')

    @quickSetting(10, 'b')
    def state(self, c, state=None):
        """ get or set state """
   
    @quickSetting(10, 'b')
    def frequency(self, c, frequency=None):
        """ get or set frequency """

    @quickSetting(10, 'b')
    def amplitude(self, c, amplitude=None):
        """ get or set amplitude """

if __name__ == "__main__":
    from labrad import util
    util.runServer(DDSServer())
