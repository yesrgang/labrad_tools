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

import json
import sys
from datetime import datetime
sys.path.append('../')

from labrad.server import Signal, setting
from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks, returnValue

from serial_device_server import SerialDeviceServer


UPDATE_ID = 698044

def seconds_til_start(delta_day, hour):
    now = datetime.now()
    start = now.replace(day=now.day+delta_day, hour=hour, minute=0, second=0, 
                        microsecond=0)
    if now > start:
        raise Exception('start time is in the past')
    return (start-now).seconds

def cancel_delayed_calls(device):
    for call in device.delayed_calls:
        call.cancel()
    device.delayed_calls = []

class VerdiServer(SerialDeviceServer):
    update = Signal(UPDATE_ID, 'signal: update', 's')
    name='verdi'

    @setting(2, state='b', returns='b')
    def state(self, c, state=None):
        device = self.get_device(c)
        if state is not None:
            yield device.set_state(state)
        device.state = yield device.get_state()
        returnValue(device.state)

    @setting(3, shutter_state='b', returns='b')
    def shutter_state(self, c, shutter_state=None):
        device = self.get_device(c)
        if shutter_state is not None:
            yield device.set_shutter_state(shutter_state)
        device.shutter_state = yield device.get_shutter_state()
        returnValue(device_shutter_state)

    @setting(4, power='v', returns='v')
    def power(self, c, power=None):
        device = self.get_device(c)
        if power is not None:
            yield device.set_power(power)
        device.power = yield device.get_power()
        returnValue(device.power)

    @setting(5, current='v', returns='v')
    def current(self, c, current=None):
        device = self.get_device(c)
        if current is not None:
            yield device.set_current(current)
        device.current = yield device.get_current()
        returnValue(device.current)

    @setting(6, warmup='b', returns='b')
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

    @setting(7, delta_day='i', hour='i', returns='i')
    def queue_warmup(self, c, delta_day=0, hour=10):
        device = self.get_device(c)
        delay = seconds_til_start(delta_day, hour)
        warmup_call = reactor.callLater(delay, self.warmup, c)
        device.delayed_calls.append(warmup_call)
        return delay

    @setting(8, shutdown='b', returns='b')
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
