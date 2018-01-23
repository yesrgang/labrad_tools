from twisted.internet.defer import inlineCallbacks, returnValue

from server_tools.device_server import Device

class MFG2160(Device):
    serial_server_name = None
    serial_address = None
    serial_timeout = 0.2 # [s]
    
    source = 3

    state = None

    amplitude = None
    amplitude_range = None

    frequency = None
    frequency_range = None

    update_parameters = ['state', 'frequency', 'amplitude']

    @inlineCallbacks
    def initialize(self):
        yield self.connect_labrad()
        self.serial_server = yield self.cxn[self.serial_server_name]
        yield self.serial_server.select_interface(self.serial_address)
        yield self.serial_server.disconnect()
        yield self.serial_server.select_interface(self.serial_address)
        yield self.serial_server.timeout(self.serial_timeout)

    @inlineCallbacks
    def do_update_parameters(self):
        self.state = self.get_state()
        self.frequency = yield self.get_frequency()
        self.amplitude = yield self.get_amplitude()

    def get_state(self):
        return True
    
    def set_state(self):
        pass
    
    @inlineCallbacks
    def set_frequency(self, frequency):
        command = 'SOUR3RF:FREQ {}'.format(frequency)
        yield self.serial_server.write_line(command)

    @inlineCallbacks
    def get_frequency(self):
        yield self.serial_server.write_line('SOUR3RF:FREQ?')
        ans = yield self.serial_server.read_lines()
        returnValue(float(ans[0]))

    @inlineCallbacks
    def set_amplitude(self, amplitude):
        command = 'SOUR3RF:AMP {}'.format(amplitude)
        yield self.serial_server.write_line(command)

    @inlineCallbacks
    def get_amplitude(self):
        yield self.serial_server.write_line('SOUR3RF:AMP?')
        ans = yield self.serial_server.read_lines()
        returnValue(float(ans[0]))

