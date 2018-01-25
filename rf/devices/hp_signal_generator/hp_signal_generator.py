from twisted.internet.defer import inlineCallbacks, returnValue

from server_tools.device_server import Device

class HPSignalGenerator(Device):
    gpib_server_name = None
    gpib_address = None
    
    state = None

    amplitude = None
    amplitude_range = None
    amplitude_units = 'dB'

    frequency = None
    frequency_range = None

    update_parameters = ['state', 'frequency', 'amplitude']

    @inlineCallbacks
    def initialize(self):
        yield self.connect_labrad()
        self.gpib_server = yield self.cxn[self.gpib_server_name]
        yield self.gpib_server.select_interface(self.gpib_address)

        yield self.do_update_parameters()

    @inlineCallbacks
    def do_update_parameters(self):
        for parameter in self.update_parameters:
            yield getattr(self, 'get_{}'.format(parameter))()

    @inlineCallbacks
    def set_state(self, state):
        command = 'OUTP:STAT {}'.format(int(bool(state)))
        yield self.gpib_server.write(command)

    @inlineCallbacks
    def get_state(self):
        ans = yield self.gpib_server.query('OUTP:STAT?')
        returnValue(bool(int(ans)))
    
    @inlineCallbacks
    def set_frequency(self, frequency):
        command = 'FREQ:CW {} Hz'.format(frequency)
        yield self.gpib_server.write(command)

    @inlineCallbacks
    def get_frequency(self):
        ans = yield self.gpib_server.query('FREQ:CW?')
        returnValue(float(ans)) # keep things in MHz 

    @inlineCallbacks
    def set_amplitude(self, amplitude):
        command = 'POW:AMPL {} {}'.format(amplitude, self.amplitude_units)
        yield self.gpib_server.write(command)

    @inlineCallbacks
    def get_amplitude(self):
        ans = yield self.gpib_server.query('POW:AMPL?')
        returnValue(float(ans))

