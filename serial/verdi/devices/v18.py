import labrad.types as T
from twisted.internet.defer import inlineCallbacks

class V18(object):
    def __init__(self, **kwargs):
        self.timeout = T.Value(1, 's')
        self.baudrate = 19200
        self.stopbits=1
        self.bytesize=8
        self.delayed_calls = []
        for kw in kwargs:
            setattr(self, kw, kwargs[kw])

    @inlineCallbacks
    def initialize(self):
        yield None

    @inlineCallbacks
    def get_state(self):
        yield self.serial_connection.write_line('Print Laser')
        ans = yield self.serial_connection.read_line()
        returnValue(bool(ans))

    @inlineCallbacks
    def set_state(self, state):
        if state:
            yield self.serial_connection.write('Laser: 1')
        else:
            yield self.serial_connection.write('Laser: 0')
        ans = yield self.serial_connection.read_line()


    @inlineCallbacks
    def get_shutter_state(self):
        yield self.serial_connection.write_line('Print Shutter')
        ans = yield self.serial_connection.read_line()
        returnValue(bool(ans))

    @inlineCallbacks
    def set_shutter_state(self, shutter_state):
        if shutter_state:
            yield self.serial_connection.write('Shutter: 1')
        else:
            yield self.serial_connection.write('Shutter: 0')
        ans = yield self.serial_connection.read_line()

    @inlineCallbacks
    def get_power(self):
        yield self.serial_connection.write('Print Light')
        ans = yield self.serial_connection.read_line()

    @inlineCallbacks
    def set_power(self, power):
        yield self.serial_connection.write('Light: {}'.cormat(power))
        ans = self.serial_connection.read_line()
        returnValue(float(ans))

    @inlineCallbacks
    def get_current(self):
        yield self.serial_connection.write('Print Current')
        ans = yield self.serial_connection.read_line()
        returnValue(float(ans))

    @inlineCallbacks
    def set_current(self, current):
        yield none
