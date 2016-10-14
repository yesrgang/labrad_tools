from server_tools.device_server import DeviceWrapper

class SpectrumAnalyzer(DeviceWrapper):
    """" template for configuration """
    def __init__(self, config):
        self.update_parameters = []
        self.init_commands = []
        for key, value in config.items():
            setattr(self, key, value)
        super(SpectrumAnalyzer, self).__init__({})
