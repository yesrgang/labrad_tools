from twisted.internet.defer import inlineCallbacks, returnValue

from rf_wrapper import RFWrapper

class HPSignalGenerator(RFWrapper):
    @inlineCallbacks
    def initialize(self):
        for command in self.init_commands:
            yield self.connection.write(command)

    @inlineCallbacks
    def set_state(self, state):
        command = 'OUTP:STAT {}'.format(int(bool(state)))
        yield self.connection.write(command)

    @inlineCallbacks
    def get_state(self):
        ans = yield self.connection.query('OUTP:STAT?')
        returnValue(bool(int(ans)))
    
    @inlineCallbacks
    def set_frequency(self, frequency):
        command = 'FREQ:CW {} Hz'.format(frequency)
        yield self.connection.write(command)

    @inlineCallbacks
    def get_frequency(self):
        ans = yield self.connection.query('FREQ:CW?')
        returnValue(float(ans)) # keep things in MHz 

    @inlineCallbacks
    def set_amplitude(self, amplitude):
        command = 'POW:AMPL {} {}'.format(amplitude, self.amplitude_units)
        yield self.connection.write(command)

    @inlineCallbacks
    def get_amplitude(self):
        ans = yield self.connection.query('POW:AMPL?')
        returnValue(float(ans))

