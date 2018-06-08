"""
### BEGIN NODE INFO
[info]
name = pmt
version = 1.0
description = 
instancename = pmt

[startup]
cmdline = %PYTHON% %FILE%
timeout = 20

[shutdown]
message = 987654321
timeout = 20
### END NODE INFO
"""
import json
from labrad.server import Signal
from labrad.server import setting
from twisted.internet.defer import inlineCallbacks
from twisted.internet.defer import returnValue

from server_tools.device_server import DeviceServer

UPDATE_ID = 64883241

class PMTServer(DeviceServer):
    update = Signal(UPDATE_ID, 'signal: update', 's')
    name = 'pmt'

    @setting(11, record_name='s', returns='b')
    def record(self, c, record_name):
        device = self.get_selected_device(c)
        yield device.record(record_name)
        returnValue(True)
    
    @setting(12, record_name=['s', 'i'], returns='s')
    def retrive(self, c, record_name):
        device = self.get_selected_device(c)
        data = yield device.retrive(record_name)
        returnValue(json.dumps(data))

if __name__ == "__main__":
    from labrad import util
    util.runServer(PMTServer())
