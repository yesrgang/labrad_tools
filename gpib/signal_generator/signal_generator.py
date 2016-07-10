"""
### BEGIN NODE INFO
[info]
name = gpib_signal_generator
version = 1.0
description = 
instancename = gpib_signal_generator

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

sys.path.append('../')
from gpib_device_server import GPIBDeviceServer

UPDATE_ID = 698034

class SignalGeneratorServer(GPIBDeviceServer):
    """ Provides basic control for signal generators"""
    update = Signal(UPDATE_ID, 'signal: update', 's')
    name = 'gpib_signal_generator'

    @setting(2, state='b', returns='b')
    def state(self, c, state=None):
        device = self.get_device(c)
        if state is not None:
            yield device.set_state(state)
        device.state = yield device.get_state()
        yield self.send_update(c)
        returnValue(device.state)

    @setting(3, frequency='v', returns='v')
    def frequency(self, c, frequency=None):
        device = self.get_device(c)
        if frequency is not None:
            yield device.set_frequency(frequency)
        device.frequency = yield device.get_frequency()
        yield self.send_update(c)
        returnValue(device.frequency)

    @setting(4, amplitude='v', returns='v')
    def amplitude(self, c, amplitude=None):
        device = self.get_device(c)
        if amplitude is not None:
            yield device.set_amplitude(amplitude)
        device.amplitude = yield device.get_amplitude()
        yield self.send_update(c)
        returnValue(device.amplitude)

    @setting(5)
    def send_update(self, c):
        device = self.get_device(c)
        update = {c['name']: {p: getattr(device, p) 
                  for p in device.update_parameters}}
        yield self.update(json.dumps(update))

if __name__ == "__main__":
    from labrad import util
    util.runServer(SignalGeneratorServer())
