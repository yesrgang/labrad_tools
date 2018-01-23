"""
### BEGIN NODE INFO
[info]
name = frequency_counter
version = 1.0
description = 
instancename = frequency_counter

[startup]
cmdline = %PYTHON% %FILE%
timeout = 20

[shutdown]
message = 987654321
timeout = 20
### END NODE INFO
"""
from labrad.server import Signal, setting
from twisted.internet.defer import returnValue

from server_tools.device_server import DeviceServer

UPDATE_ID = 698327

class FrequencyCounterServer(DeviceServer):
    update = Signal(UPDATE_ID, 'signal: update', 's')
    name = 'frequency_counter'

    @setting(10, returns='v')
    def frequency(self, c):
        device = self.get_selected_device(c)
        frequency = yield device.get_frequency()
        returnValue(frequency)

if __name__ == "__main__":
    from labrad import util
    util.runServer(FrequencyCounterServer())
