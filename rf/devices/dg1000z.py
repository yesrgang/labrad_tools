from twisted.internet.defer import inlineCallbacks, returnValue

from rf_wrapper import RFWrapper

class DG1000Z(RFWrapper):
    servername = ''
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
        if ans == 'ON':
            state = True
        else:
            state = False
        returnValue(state)

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
        command = 'SOUR{}:VOLT {}'.format(self.source, amplitude)
        yield self.connection.write(command)

    @inlineCallbacks
    def get_amplitude(self):
        command = 'SOUR{}:VOLT?'.format(self.source)
        ans = yield self.connection.query(command)
        returnValue(float(ans))
        
    @inlineCallbacks
    def set_offset(self, offset):
        command = 'SOUR{}:VOLT:OFFS {}'.format(self.source, offset)
        yield self.connection.write(command)

    @inlineCallbacks
    def get_offset(self):
        command = 'SOUR{}:VOLT:OFFS?'.format(self.source)
        ans = yield self.connection.query(command)
        returnValue(float(ans))
