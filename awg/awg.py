"""
### BEGIN NODE INFO
[info]
name = awg
version = 1.0
description = 
instancename = awg

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

from server_tools.device_server import DeviceServer
from server_tools.decorators import quickSetting

UPDATE_ID = 693038

class AWGServer(DeviceServer):
    """ Provides basic control for arbitrary waveform generators"""
    update = Signal(UPDATE_ID, 'signal: update', 's')
    name = 'awg'

    @quickSetting(10, 's')
    def waveform(self, c, waveform):
        """ get or change waveform """

if __name__ == "__main__":
    from labrad import util
    util.runServer(AWGServer())
