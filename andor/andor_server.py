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
timeout = 5
### END NODE INFO
"""
import sys

from labrad.server import Signal, setting

from server_tools.device_server import DeviceServer

UPDATE_ID = 693334

class AndorServer(DeviceServer):
    """ Provides control of andor cameras """
    update = Signal(UPDATE_ID, 'signal: update', 's')
    name = '%LABRADNODE%_andor'

    @setting(10, 'record', record_name='s', record_type='s', recorder_config='s', returns='b')
    def record(self, c, record_name, record_type, recorder_config='{}'):
        device = self.get_device(c)
        device.record(record_name, record_type, recorder_config)
        return True

if __name__ == "__main__":
    from labrad import util
    util.runServer(AndorServer())
