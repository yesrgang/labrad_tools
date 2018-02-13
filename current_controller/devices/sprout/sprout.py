from time import sleep

import labrad.types as T

from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet.reactor import callLater

from server_tools.device_server import Device

class Sprout(Device):
    serial_server_name = None
    serial_address = None
    serial_timeout = 0.25
    serial_baudrate = 19200

    power_range = (0.0, 18.0)
    power_default = 18.0

    @inlineCallbacks
    def initialize(self):
        yield self.connect_labrad()
        self.serial_server = yield self.cxn[self.serial_server_name]
        yield self.serial_server.select_interface(self.serial_address)
        yield self.serial_server.disconnect()
        yield self.serial_server.select_interface(self.serial_address)
        yield self.serial_server.timeout(self.serial_timeout)
        yield self.serial_server.baudrate(self.serial_baudrate)
    
    @inlineCallbacks
    def set_state(self, state):
        if state:
            yield self.serial_server.write_line('OPMODE=ON')
        else:
            yield self.serial_server.write_line('OPMODE=OFF')
        ans = yield self.serial_server.read_lines()

    @inlineCallbacks
    def get_state(self):
        yield self.serial_server.write_line('OPMODE?')
        ans = yield self.serial_server.read_lines()
        if ans == 'OPMODE=ON':
            out = True
        else:
            out = False
        returnValue(out)

    @inlineCallbacks
    def set_power(self, power):
        yield self.serial_server.write_line('Power set={}'.format(power))
        ans = yield self.serial_server.read_lines()

    @inlineCallbacks
    def get_power(self):
        yield self.serial_server.write_line('Power?')
        ans = yield self.serial_server.read_lines()
        returnValue(float(ans[0][6:]))

    @inlineCallbacks
    def warmup(self):
        yield self.set_power(self.power_default)
        yield self.set_state(True)
        returnValue(1.)

    @inlineCallbacks
    def shutdown(self):
        yield self.set_power(0)
        yield self.set_state(False)
        returnValue(1.)
