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


