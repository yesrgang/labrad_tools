from time import sleep

import labrad.types as T

from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet.reactor import callLater

from server_tools.device_server import DeviceWrapper
from lib.helpers import seconds_til_start, cancel_delayed_calls

class Sprout(DeviceWrapper):
    def __init__(self, config):
        self.timeout = .25
        self.baudrate = 19200
        self.delayed_calls = []
        self.update_parameters = []
        for key, value in config.items():
            setattr(self, key, value)

        super(Sprout, self).__init__({})

    @inlineCallbacks
    def initialize(self):
        yield None

    @inlineCallbacks
    def get_state(self):
        yield self.connection.write_line('OPMODE?')
        ans = yield self.connection.read_lines()
        if ans == 'OPMODE=ON':
            out = 1
        else:
            out = 0
        returnValue(out)

    @inlineCallbacks
    def set_state(self, state):
        if state:
            yield self.connection.write_line('OPMODE=ON')
        else:
            yield self.connection.write_line('OPMODE=OFF')
        ans = yield self.connection.read_lines()


    @inlineCallbacks
    def get_shutter_state(self):
        yield self.connection.write_line('Shutter?')
        ans = yield self.connection.read_lines()
#        returnValue(bool(int(ans[0])))

#    @inlineCallbacks
#    def set_shutter_state(self, shutter_state):
#        if shutter_state:
#            yield self.connection.write_line('Shutter: 1')
#        else:
#            yield self.connection.write_line('Shutter: 0')
#        ans = yield self.connection.read_lines()

    @inlineCallbacks
    def get_power(self):
        yield self.connection.write_line('Power?')
        ans = yield self.connection.read_lines()
        returnValue(float(ans[0][6:]))

    @inlineCallbacks
    def set_power(self, power):
        yield self.connection.write_line('Power set={}'.format(power))
        ans = yield self.connection.read_lines()

#    @inlineCallbacks
#    def get_current(self):
#        yield self.connection.write_line('Print Current')
#        ans = yield self.connection.read_lines()
#        returnValue(float(ans[0]))

#    @inlineCallbacks
#    def set_current(self, current):
#        yield none

    @inlineCallbacks
    def warmup(self):
        yield cancel_delayed_calls(self)
        yield self.set_power(self.full_power)
        yield self.set_state(True)
        
#        shutter_call = callLater(self.shutter_delay, self.set_shutter_state, True)
#        self.delayed_calls.append(shutter_call)
#        full_power_call = callLater(self.full_power_delay, self.set_power, 
#                                    self.full_power)
#        self.delayed_calls.append(full_power_call)
        returnValue(1.)



    @inlineCallbacks
    def shutdown(self):
        yield cancel_delayed_calls(self)
#        yield self.set_shutter_state(False)
        yield self.set_power(self.init_power)
        yield self.set_state(False)
        returnValue(1.)
