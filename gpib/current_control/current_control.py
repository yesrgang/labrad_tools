"""
### BEGIN NODE INFO
[info]
name = current_control
version = 1.0
description = 
instancename = current_control

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

UPDATE_ID = 698027

class CurrentControlServer(GPIBDeviceServer):
    """ Provides basic control for current controllers """
    update = Signal(UPDATE_ID, 'signal: update', 's')
    name = 'gpib_current_control'
    
    @setting(2, state='b', returns='b')
    def state(self, c, state=None):
        device = self.get_device(c)
        if state is not None:
            yield device.set_state(state)
        device.state = yield device.get_state()
        yield self.send_update(c)
        returnValue(device.state)

    @setting(3, current='v', returns='v')
    def current(self, c, current=None):
        device = self.get_device(c)
        if current is not None:
            yield device.set_current(current)
        device.current = yield device.get_current()
        yield self.send_update(c)
        returnValue(device.current)

    @setting(4, power='v', returns='v')
    def power(self, c, power=None):
        device = self.get_device(c)
        if power is not None:
            yield device.set_power(power)
        device.power = yield device.get_power()
        yield self.send_update(c)
        returnValue(device.power)

    @setting(5, warmup='b', returns='b')
    def warmup(self, c, warmup=None):
        device = self.get_device(c)
        if warmup:
            yield device.warmup()
        callLater(10, self.send_update, c)
        returnValue(bool(warmup))

    @setting(6, shutdown='b', returns='b')
    def shutdown(self, c, shutdown=None):
        device = self.get_device(c)
        if shutdown:
            yield device.shutdown()
        callLater(10, self.send_update, c)
        returnValue(bool(shutdown))

    @setting(7)
    def send_update(self, c):
        device = self.get_device(c)
        update = {c['name']: {p: getattr(device, p) 
                  for p in device.update_parameters}}
        yield self.update(json.dumps(update))

if __name__ == '__main__':
    from labrad import util
    util.runServer(CurrentControlServer())
