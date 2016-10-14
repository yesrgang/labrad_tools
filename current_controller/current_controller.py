"""
### BEGIN NODE INFO
[info]
name = current_controller
version = 1.0
description = 
instancename = current_controller

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
from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet.reactor import callLater

sys.path.append('../')
from server_tools.device_server import DeviceServer
from server_tools.decorators import quickSetting

UPDATE_ID = 698027

class CurrentControllerServer(DeviceServer):
    """ Provides basic control for current controllers """
    update = Signal(UPDATE_ID, 'signal: update', 's')
    name = 'current_controller'

    @quickSetting(10, 'b')
    def state(self, c, state=None):
        """ get or update state """

    @quickSetting(11, 'v')
    def current(self, c, current=None):
        """ get or update current """

    @quickSetting(12, 'v')
    def power(self, c, power=None):
        """ get or update power """

    @setting(13, warmup='b', returns='b')
    def warmup(self, c, warmup=True):
        device = self.get_device(c)
        if warmup:
            update_delay = yield device.warmup()
        callLater(update_delay, self.send_update, c)
        returnValue(warmup)

    @setting(15, delta_day='i', hour='i', returns='i')
    def queue_warmup(self, c, delta_day=0, hour=10):
        device = self.get_device(c)
        delay = seconds_til_start(delta_day, hour)
        warmup_call = callLater(delay, self.warmup, c)
        device.delayed_calls.append(warmup_call)
        return delay

    @setting(14, shutdown='b', returns='b')
    def shutdown(self, c, shutdown=True):
        device = self.get_device(c)
        if shutdown:
            update_delay = yield device.shutdown()
        callLater(update_delay, self.send_update, c)
        returnValue(shutdown)

if __name__ == '__main__':
    from labrad import util
    util.runServer(CurrentControllerServer())
