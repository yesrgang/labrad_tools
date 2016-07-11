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

UPDATE_ID = 698034

class RFServer(DeviceServer):
    """ Provides basic control for RF sources"""
    update = Signal(UPDATE_ID, 'signal: update', 's')
    name = 'rf'

if __name__ == "__main__":
    from labrad import util
    util.runServer(RFServer())
