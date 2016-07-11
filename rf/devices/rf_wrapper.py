class RFWrapper(object):
    """" template for configuration """
    def __init__(self, config):
        self.update_parameters = ['state', 'frequency', 'amplitude']
        self.init_commands = []
        for key, value in config.items():
            setattr(self, key, value)
