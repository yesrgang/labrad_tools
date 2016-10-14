from time import sleep

import labrad.types as T

from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet.reactor import callLater

from server_tools.device_server import DeviceWrapper
from lib.helpers import seconds_til_start, cancel_delayed_calls

class Verdi(DeviceWrapper):
    def __init__(self, config):
        self.timeout = .1
        self.baudrate = 19200
        self.delayed_calls = []
        self.update_parameters = []
        for key, value in config.items():
            setattr(self, key, value)

        super(Verdi, self).__init__({})

    @inlineCallbacks
    def initialize(self):
        yield None

    @inlineCallbacks
    def get_state(self):
        yield self.connection.write_line('Print Laser')
        ans = yield self.connection.read_line()
        returnValue(bool(ans))

    @inlineCallbacks
    def set_state(self, state):
        if state:
            yield self.connection.write_line('Laser: 1')
        else:
            yield self.connection.write_line('Laser: 0')
        ans = yield self.connection.read_line()


    @inlineCallbacks
    def get_shutter_state(self):
        yield self.connection.write_line('Print Shutter')
        ans = yield self.connection.read_line()
        returnValue(bool(int(ans)))

    @inlineCallbacks
    def set_shutter_state(self, shutter_state):
        if shutter_state:
            yield self.connection.write_line('Shutter: 1')
        else:
            yield self.connection.write_line('Shutter: 0')
        ans = yield self.connection.read_line()

    @inlineCallbacks
    def get_power(self):
        yield self.connection.write_line('Print Light')
        ans = yield self.connection.read_line()
        returnValue(float(ans))

    @inlineCallbacks
    def set_power(self, power):
        yield self.connection.write_line('Light: {}'.format(power))
        ans = yield self.connection.read_line()

    @inlineCallbacks
    def get_current(self):
        yield self.connection.write_line('Print Current')
        ans = yield self.connection.read_line()
        returnValue(float(ans))

    @inlineCallbacks
    def set_current(self, current):
        yield none

    @inlineCallbacks
    def warmup(self):
        yield cancel_delayed_calls(self)
        yield self.set_power(self.init_power)
        yield self.set_state(True)
        shutter_call = callLater(self.shutter_delay, self.set_shutter_state, True)
        self.delayed_calls.append(shutter_call)
        full_power_call = callLater(self.full_power_delay, self.set_power, 
                                    self.full_power)
        self.delayed_calls.append(full_power_call)
        returnValue(1.)

    @inlineCallbacks
    def shutdown(self):
        yield cancel_delayed_calls(self)
        yield self.set_shutter_state(False)
        yield self.set_power(self.init_power)
        yield self.set_state(False)
        returnValue(1.)
