from time import sleep

import labrad.types as T

from twisted.internet.defer import inlineCallbacks, returnValue

from server_tools.device_server import DeviceWrapper

class V18(DeviceWrapper):
    def __init__(self, config):
        self.timeout = .1
        self.baudrate = 19200
        self.delayed_calls = []
        for key, value in config.items():
            setattr(self, key, value)

        super(V18, self).__init__({})

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
