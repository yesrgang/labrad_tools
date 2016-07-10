import labrad.units as U
from twisted.internet.defer import inlineCallbacks

class CurrentController(object):
    """" template for configuration """
    def __init__(self, **kwargs):
        self.update_parameters = ['state', 'current', 'power']
        self.init_commands = []
        self.timeout = 1 * U.s
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    @inlineCallbacks
    def initialize(self):
        for command in self.init_commands:
            yield self.gpib_connection.write(command)
        self.state = yield self.get_state()
        self.current = yield self.get_current()
        self.power = yield self.get_power()

