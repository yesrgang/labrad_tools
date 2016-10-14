from twisted.internet.defer import inlineCallbacks

from server_tools.device_server import DeviceWrapper

class GenericECDL(DeviceWrapper):
    """" template for configuration """
    def __init__(self, config):
        self.update_parameters = ['state', 'diode_current', 'piezo_voltage']
        self.init_commands = []
        for key, value in config.items():
            setattr(self, key, value)
    
        super(GenericECDL, self).__init__({})
