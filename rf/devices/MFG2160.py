from twisted.internet.defer import inlineCallbacks, returnValue

from rf_wrapper import RFWrapper

class MFG2160(RFWrapper):
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
        command = 'SOUR3RF:FREQ {}'.format(frequency)
        yield self.connection.write(command)

    @inlineCallbacks
    def get_frequency(self):
        ans = yield self.connection.query('SOUR3RF:FREQ?')
        returnValue(float(ans))

    @inlineCallbacks
    def set_amplitude(self, amplitude):
        command = 'SOUR3RF:AMPL {}'.format(amplitude)
        yield self.connection.write(command)

    @inlineCallbacks
    def get_amplitude(self):
        ans = yield self.connection.query('SOUR3RF:AMPL?')
        returnValue(float(ans[:-2]))

