from twisted.internet.defer import inlineCallbacks

from server_tools.device_server import DeviceWrapper


class PowerSupply(DeviceWrapper):
    """" template for configuration """
    def __init__(self, config):
        self.update_parameters = ['state', 'current', 'voltage', 'current_limit', 'voltage_limit']
        self.init_commands = []
        for key, value in config.items():
            setattr(self, key, value)
    
        super(PowerSupply, self).__init__({})
