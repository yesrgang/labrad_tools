import json
from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet.reactor import callLater

from server_tools.device_server import Device
from lib.helpers import seconds_til_start, cancel_delayed_calls

class Verdi(Device):
    serial_server_name = None
    serial_address = None
    serial_timeout = 0.25
    serial_baudrate = 19200

    power_range = (0.0, 18.0)
    default_power = 18.0
    warmup_power = 14.0

    delayed_calls = []

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
            yield self.serial_server.write_line('Laser: 1')
        else:
            yield self.serial_server.write_line('Laser: 0')
        ans = yield self.serial_server.read_lines()

    @inlineCallbacks
    def get_state(self):
        yield self.serial_server.write_line('Print Laser')
        ans = yield self.serial_server.read_lines()
        returnValue(bool(ans[0]))

    @inlineCallbacks
    def set_shutter_state(self, shutter_state):
        if shutter_state:
            yield self.serial_server.write_line('Shutter: 1')
        else:
            yield self.serial_server.write_line('Shutter: 0')
        ans = yield self.serial_server.read_lines()

    @inlineCallbacks
    def get_shutter_state(self):
        yield self.serial_server.write_line('Print Shutter')
        ans = yield self.serial_server.read_lines()
        returnValue(bool(int(ans[0])))

    @inlineCallbacks
    def set_power(self, power, emit=False):
        yield self.serial_server.write_line('Light: {}'.format(power))
        ans = yield self.serial_server.read_lines()
        if emit:
            update = {self.name: {p: getattr(self, p) 
                      for p in self.update_parameters}}
            yield self.server.update(json.dumps(update))

    @inlineCallbacks
    def get_power(self):
        yield self.serial_server.write_line('Print Light')
        ans = yield self.serial_server.read_lines()
        returnValue(float(ans[0]))

    @inlineCallbacks
    def set_current(self, current):
        yield none

    @inlineCallbacks
    def get_current(self):
        yield self.serial_server.write_line('Print Current')
        ans = yield self.serial_server.read_lines()
        returnValue(float(ans[0]))

    @inlineCallbacks
    def warmup(self):
        yield cancel_delayed_calls(self)
        yield self.set_power(self.default_power)
        yield self.set_state(True)
        yield self.set_shutter_state(True)

    @inlineCallbacks
    def shutdown(self):
        yield cancel_delayed_calls(self)
        yield self.set_shutter_state(False)
        yield self.set_state(False)
        yield self.set_power(self.warmup_power)
