from twisted.internet.defer import inlineCallbacks, returnValue

from generic_signal_generator import SignalGenerator

class HPSignalGenerator(SignalGenerator):
    @inlineCallbacks
    def set_state(self, state):
        command = 'OUTP:STAT {}'.format(int(bool(state)))
        yield self.gpib_connection.write(command)

    @inlineCallbacks
    def get_state(self):
        ans = yield self.gpib_connection.query('OUTP:STAT?')
        returnValue(bool(int(ans)))
    
    @inlineCallbacks
    def set_frequency(self, frequency):
        command = 'FREQ:CW {} Hz'.format(frequency)
        yield self.gpib_connection.write(command)

    @inlineCallbacks
    def get_frequency(self):
        ans = yield self.gpib_connection.query('FREQ:CW?')
        returnValue(float(ans)) # keep things in MHz 

    @inlineCallbacks
    def set_amplitude(self, amplitude):
        command = 'POW:AMPL {} {}'.format(amplitude, self.amplitude_units)
        yield self.gpib_connection.write(command)

    @inlineCallbacks
    def get_amplitude(self):
        ans = yield self.gpib_connection.query('POW:AMPL?')
        returnValue(float(ans))

