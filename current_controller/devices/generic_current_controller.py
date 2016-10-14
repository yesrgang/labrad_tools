from twisted.internet.defer import inlineCallbacks

from server_tools.device_server import DeviceWrapper


class CurrentController(DeviceWrapper):
    """" template for configuration """
    def __init__(self, config):
        self.update_parameters = ['state', 'current', 'power']
        self.init_commands = []
        for key, value in config.items():
            setattr(self, key, value)
    
        super(CurrentController, self).__init__({})
