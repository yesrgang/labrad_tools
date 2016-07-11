from twisted.internet.defer import inlineCallbacks, returnValue

from rf_wrapper import RFWrapper

class AG335xxx(RFWrapper):
    @inlineCallbacks
    def initialize(self):
        for command in self.init_commands:
            yield self.connection.write(command)

    @inlineCallbacks
    def set_state(self, state):
        command = 'OUTP{}:STAT {}'.format(self.source, int(bool(state)))
        yield self.connection.write(command)

    @inlineCallbacks
    def get_state(self):
        command = 'OUTP{}?'.format(self.source)
        ans = yield self.connection.query(command)
        returnValue(bool(int(ans)))

    @inlineCallbacks
    def set_frequency(self, frequency):
        command = 'SOUR{}:FREQ {}'.format(self.source, frequency)
        yield self.connection.write(command)

    @inlineCallbacks
    def get_frequency(self):
        command = 'SOUR{}:FREQ?'.format(self.source)
        ans = yield self.connection.query(command)
        returnValue(float(ans))

    @inlineCallbacks
    def set_amplitude(self, amplitude):
        command = 'SOUR{}:VOLT {}'.format(self.cource, amplitude)
        yield self.connection.write(command)

    @inlineCallbacks
    def get_amplitude(self):
        command = 'SOUR{}:VOLT?'.format(self.source)
        ans = yield self.connection.query(command)
        returnValue(float(ans))
