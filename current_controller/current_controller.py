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
from twisted.internet import reactor

from server_tools.device_server import DeviceServer
from server_tools.decorators import quickSetting

UPDATE_ID = 698027
reactor.suggestThreadPoolSize(30)

class CurrentControllerServer(DeviceServer):
    """ Provides basic control for current controllers """
    update = Signal(UPDATE_ID, 'signal: update', 's')
    name = 'current_controller'

    @quickSetting(10, 'b')
    def state(self, c, state=None):
        """ get or update state """

    @quickSetting(11, 'b')
    def shutter_state(self, c, state=None):
        """ get or update shutter state """

    @quickSetting(12, 'v')
    def current(self, c, current=None):
        """ get or update current """

    @quickSetting(13, 'v')
    def power(self, c, power=None):
        """ get or update power """

    @setting(14, warmup='b', returns='b')
    def warmup(self, c, warmup=True):
        device = self.get_selected_device(c)
        if warmup:
            yield device.warmup()
        returnValue(warmup)

    @setting(15, delta_day='i', hour='i', returns='i')
    def queue_warmup(self, c, delta_day=0, hour=10):
        device = self.get_selected_device(c)
        delay = seconds_til_start(delta_day, hour)
        warmup_call = callLater(delay, self.warmup, c)
        device.delayed_calls.append(warmup_call)
        return delay

    @setting(16, shutdown='b', returns='b')
    def shutdown(self, c, shutdown=True):
        device = self.get_selected_device(c)
        if shutdown:
            yield device.shutdown()
        returnValue(shutdown)

if __name__ == '__main__':
    from labrad import util
    util.runServer(CurrentControllerServer())
