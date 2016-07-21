import labrad.units as U
from twisted.internet.defer import inlineCallbacks

class GenericECDL(object):
    """" template for configuration """
    def __init__(self, config):
        self.update_parameters = ['state', 'diode_current', 'piezo_voltage']
        self.init_commands = []
        for key, value in config.items():
            setattr(self, key, value)
    
