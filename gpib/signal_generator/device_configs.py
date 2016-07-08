import labrad.units as U
from twisted.internet.defer import inlineCallbacks, returnValue

class SignalGenerator(object):
    """" template for configuration """
    def __init__(self, **kwargs):
        self.update_parameters = ['state', 'frequency', 'amplitude']
        self.init_commands = []
        self.timeout = 1 * U.s
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    @inlineCallbacks
    def initialize(self):
        for command in self.init_commands:
            yield self.gpib_connection.write(command)

    def set_state(self, state):
        """ stuff to write state """

    def get_state(self):
        """ stuff to read state """

    def set_frequency(self, frequency):
        """ stuff to write frequency """

    def get_frequency(self):
        """ stuff to read frequency """

    def set_amplitude(self, amplitude):
        """ stuff to write amplitude """

    def get_amplitude(self):
        """ stuff to read amplitude """


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
        command = 'POW:AMPL {} {}'.format(amplitude, amplitude_units)
        yield self.gpib_connection.write(command)

    @inlineCallbacks
    def get_amplitude(self):
        ans = yield self.gpib_connection.query('POW:AMPL?')
        returnValue(float(ans))

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
