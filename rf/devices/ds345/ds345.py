from twisted.internet.defer import inlineCallbacks, returnValue

from server_tools.device_server import Device

class DS345(Device):
    gpib_server_name = None
    gpib_address = None
    
    state = None

    amplitude = None
    amplitude_range = (-36, 20)
    amplitude_units = 'dB'

    frequency = None
    frequency_range = (1e-6, 30e6)

    update_parameters = ['state', 'frequency', 'amplitude']

    @inlineCallbacks
    def initialize(self):
        yield self.connect_labrad()
        self.gpib_server = yield self.cxn[self.gpib_server_name]
        yield self.gpib_server.select_interface(self.gpib_address)

        yield self.do_update_parameters()

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
        frequency = sorted([min(self.frequency_range), 
            max(self.frequency_range), frequency])[1]
        command = 'FREQ {}'.format(frequency)
        yield self.gpib_server.write(command)

    @inlineCallbacks
    def get_frequency(self):
        ans = yield self.gpib_server.query('FREQ?')
        returnValue(float(ans))

    @inlineCallbacks
    def set_amplitude(self, amplitude):
        amplitude = sorted([min(self.amplitude_range), 
            max(self.amplitude_range), amplitude])[1]
        command = 'AMPL {}{}'.format(amplitude, self.amplitude_units)
        yield self.gpib_server.write(command)

    @inlineCallbacks
    def get_amplitude(self):
        ans = yield self.gpib_server.query('AMPL?')
        returnValue(float(ans[:-2]))

