from twisted.internet.defer import inlineCallbacks, returnValue

from generic_signal_generator import SignalGenerator

class AG335XXX(SignalGenerator):
    @inlineCallbacks
    def set_state(self, state):
        command = 'OUTP{}:STAT {}'.format(self.source, int(bool(state)))
        yield self.gpib_connection.write(command)

    @inlineCallbacks
    def get_state(self):
        command = 'OUTP{}?'.format(self.source)
        ans = yield self.gpib_connection.query(command)
        returnValue(bool(int(ans)))

    @inlineCallbacks
    def set_frequency(self, frequency):
        command = 'SOUR{}:FREQ {}'.format(self.source, frequency)
        yield self.gpib_connection.write(command)

    @inlineCallbacks
    def get_frequency(self):
        command = 'SOUR{}:FREQ?'.format(self.source)
        ans = yield self.gpib_connection.query(command)
        returnValue(float(ans))

    @inlineCallbacks
    def set_amplitude(self, amplitude):
        command = 'SOUR{}:VOLT {}'.format(self.cource, amplitude)
        yield self.gpib_connection.write(command)

    @inlineCallbacks
    def get_amplitude(self):
        command = 'SOUR{}:VOLT?'.format(self.source)
        ans = yield self.gpib_connection.query(command)
        returnValue(float(ans))
