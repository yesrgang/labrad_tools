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
from datatime import datetime
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

    @setting(1, state='b', returns='b')
    def state(self, c, state=None):
        serial = self.get_device(c).serial_connection
        if state == True:
            yield serial.write_line('Laser: 1')
            ans = yield serial.read_line()
        elif state == False:
            yield serial.write_line('Laser: 0')
            ans = yield serial.read_line()
        yield serial.write_line('Print Laser')
        ans = yield serial.read_line()
        returnValue(bool(ans))

    @setting(2, state='b', returns='b')
    def shutter_state(self, c, state=None):
        serial = self.get_device(c).serial_connection
        if state == True:
            yield serial.write_line('Shutter: 1')
            ans = yield serial.read_line()
        elif state == False:
            yield serial.write_line('Shutter: 0')
            ans = yield serial.read_line()
        yield serial.write_line('Print Shutter')
        ans = yield serial.read_line()
        returnValue(bool(ans))

    @setting(3, power='v', returns='v')
    def power(self, c, power=None):
        serial = self.get_device(c).serial_connection
        if power:
            yield serial.write_line('Light: {}'.format(power))
            ans = yield serial.read_line()
        yield serial.write_line('Print Light')
        ans = yield serial.read_line()
        returnValue(float(ans))

    @setting(4, returns='v')
    def current(self, c):
        serial = self.get_device(c).serial_connection
        yield serial.write_line('Print Current')
        ans = yield serial.read_line()
        returnValue(float(ans))

    @setting(5, returns='b')
    def warmup(self, c):
        device = self.get_device(c)
        cancel_delayed_calls(device)
        yield self.power(c, device.init_power)
        yield self.state(c, True)
        shutter_call = reactor.callLater(device.shutter_delay, 
                                         self.shutter_state, c, True)
        full_power_call = reactor.callLater(device.full_power_delay, self.power, 
                                            c, device.full_power)
        device.delayed_calls.append(shutter_call)
        device.delayed_calls.append(full_power_call)
        returnValue(True)

    @setting(6, delta_day='i', hour='i', returns='i')
    def queue_warmup(self, c, delta_day=0, hour=10):
        device = self.get_device(c)
        delay = seconds_til_start(delta_day, hour)
        warmup_call = reactor.callLater(delay, self.warmup, c)
        device.delayed_calls.append(warmup_call)
        return delay

    @setting(7, returns='b')
    def shutdown(self, c):
        device = self.get_device(c)
        yield self.shutter_state(c, False)
        yield self.power(c, device.init_power)
        yield self.state(c, False)
        returnValue(True)

if __name__ == "__main__":
    from labrad import util
    util.runServer(VerdiServer())
