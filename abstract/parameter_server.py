import json

import ok
from labrad.server import LabradServer, setting, Signal
from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks, returnValue, DeferredLock
from twisted.internet.task import LoopingCall
from twisted.internet.threads import deferToThread

class ParameterServer(LabradServer):
    def __init__(self, config_name):
        LabradServer.__init__(self)
        self.config_name = config_name
        self.load_configuration()

    def initServer(self):
        LabradServer.initServer(self)

    def load_configuration(self):
        config = __import__(self.config_name).ParameterConfig()
        for key, value in config.__dict__.items():
            setattr(self, key, value)

    @setting(01, 'asdf')
    def asdf(self, c):
        self.client.vagabond_conductor.register_device_parameters('a')

    
            

if __name__ == "__main__":
    config_name = 'parameter_config'
    __server__ = ParameterServer(config_name)
    from labrad import util
    util.runServer(__server__)
