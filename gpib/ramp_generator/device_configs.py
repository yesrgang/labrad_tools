import labrad.units as U
from twisted.internet.defer import inlineCallbacks, returnValue

class SignalGenerator(object):
    """" template for configuration """
    def __init__(self, **kwargs):
        self.update_parameters = ['state', 'frequency', 'amplitude']
        self.timeout = 1 * U.s
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def initialize(self):
        """ runs on first connection """

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

class AG335XXX(SignalGenerator):
    @inlineCallbacks
    def initialize(self):
        for command in self.init_commands:
            yield self.gpib_connection.write(command)

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

class AG335XXXRamp(AG335XXX):
    @inlineCallbacks
    def set_ramprate(self, f_start, f_stop):
        ramp_rate = (f_stop-f_stop)/self.t_ramp
        commands = [
            'SOUR{}:FREQ {}'.format(self.source, f_start),
            'SOUR{}:FREQ:STAR {}'.format(self.source, f_start),
            'SOUR{}:FREQ:STOP {}'.format(self.source, f_stop),
            'SOUR{}:SWEEp:TIME {}'.format(self.source, self.t_ramp),
            'SOUR{}:FREQ:MODE SWE'.format(self.source),
            'TRIG{}:SOUR IMM'.format(self.source),
        ]
        for command in commands:
            self.gpib_connection.write(command)

    @inlineCallbacks
    def get_ramprate(self):
        start_command = 'SOUR{}:FREQ:STAR?'.format(self.source)
        stop_command = 'SOUR{}:FREQ:STOP?'.format(self.source)
        T_command = 'SOUR{}:SWEEp:TIME?'.format(self.source)
        f_start = yield self.query(start_command)
        f_stop = yield self.gpib_connection.query(stop_command)
        T_ramp = yield self.gpib_connection.query(T_command)
        ramprate = (float(f_stop) - float(f_start))/float(T_ramp)
        returnValue(ramprate)
