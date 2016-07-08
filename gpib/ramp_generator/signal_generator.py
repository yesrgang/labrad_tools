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
from datetime import datetime
sys.path.append('../')

from labrad.server import Signal, setting
from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks, returnValue

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

    @setting(5, ramprate='v', returns='v')
    def ramprate(self, c, ramprate=None):
        device = self.get_device(c)
        for attr in ['set_ramprate', 'get_ramprate', 'get_counter_frequency']:
            if not hasattr(device, 'set_ramprate'):
                raise Exception('ramping is not configured for this device')
        if ramprate is not None:
            yield self.set_ramprate(device, ramprate)
        device.ramprate = yield device.get_ramprate()
        yield self.send_update(c)
        returnValue(device.ramprate)
    
    @inlineCallbacks
    def set_ramprate(self, device, ramprate):
        f_start = yield device.get_counter_frequency()
        f_stop = f_start + ramprate*device.t_ramp
        yield device.set_ramprate(f_start, f_stop)
        if device.delayed_call.active()
            device.delayed_call.cancel()
        device.delayed_call = reactor.callLater(device.t_ramp/2., self.set_ramprate, device, ramprate)

    @inlineCallbacks
    def get_counter_frequency(self, device):
        server = getattr(self.client, device.counter_server_name)
        yield server.address(device.counter_address)
        ans = yield server.query('MEAS:FREQ? DEF, DEF, (@1)')
        returnValue(float(ans)

    @setting(6)
    def send_update(self, c):
        d = self.get_device(c)
        parameters = dict([(p, getattr(d, p)) for p in d.update_parameters])
        yield self.update(json.dumps(parameters))

if __name__ == "__main__":
    from labrad import util
    util.runServer(SignalGeneratorServer())
