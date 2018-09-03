"""
### BEGIN NODE INFO
[info]
name = andor
version = 1.0
description = 
instancename = andor

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
from twisted.internet.defer import returnValue

from server_tools.device_server import DeviceServer

UPDATE_ID = 23883841

class AndorServer(DeviceServer):
    update = Signal(UPDATE_ID, 'signal: update', 's')
    name = '%LABRADNODE%_andor'

    @setting(11, record_path='s', record_type='s', recorder_config_json='s', returns='b')
    def record(self, c, record_path, record_type, recorder_config_json='{}'):
        recorder_config = json.loads(recorder_config_json)
        device = self.get_selected_device(c)
        yield device.record(record_path, record_type, recorder_config)
        returnValue(True)
    
    @setting(12, record_path=['s', 'i'], processor_type='s', processor_config='s', returns='s')
    def retrive(self, c, record_path, processor_type, processor_config):
        device = self.get_selected_device(c)
        data = yield device.process(record_name, processor_config)
        returnValue(json.dumps(data))

if __name__ == "__main__":
    from labrad import util
    util.runServer(AndorServer())
