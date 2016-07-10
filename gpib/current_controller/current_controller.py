"""
### BEGIN NODE INFO
[info]
name = gpib_current_controller
version = 1.0
description = 
instancename = gpib_current_controller

[startup]
cmdline = %PYTHON% %FILE%
timeout = 20

[shutdown]
message = 987654321
timeout = 5
### END NODE INFO
"""

import json
import sys

from labrad.server import Signal, setting
from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet.reactor import callLater

sys.path.append('../')
from gpib_device_server import GPIBDeviceServer
sys.path.append('../../')
from extras.decorators import quickSetting

UPDATE_ID = 698027

class CurrentControllerServer(GPIBDeviceServer):
    """ Provides basic control for current controllers """
    update = Signal(UPDATE_ID, 'signal: update', 's')
    name = 'gpib_current_controller'

    @quickSetting(10, 'b')
    def state(self, c, state=None):
        """ get or change output state """

    @quickSetting(11, 'v')
    def current(self, c, current=None):
        """ get or change output current """

    @quickSetting(12, 'v')
    def power(self, c, power=None):
        """ get or change output power """

    @setting(13, warmup='b', returns='b')
    def warmup(self, c, warmup=True):
        device = self.get_device(c)
        if warmup:
            yield device.warmup()
        callLater(10, self.send_update, c)
        returnValue(warmup)

    @setting(14, shutdown='b', returns='b')
    def shutdown(self, c, shutdown=True):
        device = self.get_device(c)
        if shutdown:
            yield device.shutdown()
        callLater(10, self.send_update, c)
        returnValue(shutdown)

if __name__ == '__main__':
    from labrad import util
    util.runServer(CurrentControllerServer())
