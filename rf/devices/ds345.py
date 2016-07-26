from twisted.internet.defer import inlineCallbacks, returnValue

from rf_wrapper import RFWrapper

class DS345(RFWrapper):
    @inlineCallbacks
    def initialize(self):
        for command in self.init_commands:
            yield self.connection.write(command)

    def get_state(self):
        return True
    
    def set_state(self):
        pass
    
    @inlineCallbacks
    def set_frequency(self, frequency):
        command = 'FREQ {}'.format(frequency)
        yield self.connection.write(command)

    @inlineCallbacks
    def get_frequency(self):
        ans = yield self.connection.query('FREQ?')
        returnValue(float(ans))

    @inlineCallbacks
    def set_amplitude(self, amplitude):
        command = 'AMPL {}{}'.format(amplitude, self.amplitude_units)
        yield self.connection.write(command)

    @inlineCallbacks
    def get_amplitude(self):
        ans = yield self.connection.query('AMPL?')
        returnValue(float(ans[:-2]))

