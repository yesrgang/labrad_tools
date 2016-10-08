"""
### BEGIN NODE INFO
[info]
name = verdi
version = 1.0
description = 
instancename = verdi

[startup]
cmdline = %PYTHON% %FILE%
timeout = 20

[shutdown]
message = 987654321
timeout = 20
### END NODE INFO
"""
import sys

from labrad.server import Signal, setting
from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks, returnValue

sys.path.append('../')
from server_tools.device_server import DeviceServer
from server_tools.decorators import quickSetting
from lib.helpers import seconds_til_start, cancel_delayed_calls

UPDATE_ID = 698044

class VerdiServer(DeviceServer):
    update = Signal(UPDATE_ID, 'signal: update', 's')
    name='verdi'

    @quickSetting(10, 'b')
    def state(self, c, state=None):
        """ get or change state """

    @quickSetting(11, 'b')
    def shutter_state(self, c, shutter_state=None):
        """ get or change shutter_state """

    @quickSetting(12, 'v')
    def power(self, c, power=None):
        """ get or change power """

    @quickSetting(13, 'v')
    def current(self, c, current=None):
        """ get or change current """

    @setting(14, warmup='b', returns='b')
    def warmup(self, c, warmup=True):
        device = self.get_device(c)
        if warmup:
            cancel_delayed_calls(device)
            yield self.power(c, device.init_power)
            yield self.state(c, True)
            shutter_call = reactor.callLater(device.shutter_delay, 
                                             self.shutter_state, c, True)
            full_power_call = reactor.callLater(device.full_power_delay, self.power, 
                                                c, device.full_power)
            device.delayed_calls.append(shutter_call)
            device.delayed_calls.append(full_power_call)
        returnValue(warmup)

    @setting(15, delta_day='i', hour='i', returns='i')
    def queue_warmup(self, c, delta_day=0, hour=10):
        device = self.get_device(c)
        delay = seconds_til_start(delta_day, hour)
        warmup_call = reactor.callLater(delay, self.warmup, c)
        device.delayed_calls.append(warmup_call)
        return delay

    @setting(16, shutdown='b', returns='b')
    def shutdown(self, c, shutdown=True):
        device = self.get_device(c)
        if shutdown:
            yield self.shutter_state(c, False)
            yield self.power(c, device.init_power)
            yield self.state(c, False)
        returnValue(shutdown)

if __name__ == "__main__":
    from labrad import util
    util.runServer(VerdiServer())
