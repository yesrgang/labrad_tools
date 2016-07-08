from twisted.internet.defer import inlineCallbacks, returnValue

from generic_signal_generator import SignalGenerator

class DS345(SignalGenerator):
    def get_state(self):
        return True
    
    @inlineCallbacks
    def set_frequency(self, frequency):
        command = 'FREQ {}'.format(frequency)
        yield self.gpib_connection.write(command)

    @inlineCallbacks
    def get_frequency(self):
        ans = yield self.gpib_connection.query('FREQ?')
        returnValue(float(ans))

    @inlineCallbacks
    def set_amplitude(self, amplitude):
        command = 'AMPL {}{}'.fomat(amplitude, self.amplitude_units)
        yield self.gpib_connection.write(command)

    @inlineCallbacks
    def get_amplitude(self):
        ans = yield self.gpib_connection.query('AMPL?')
        returnValue(float(ans[:-2]))

