import types
import marshal
import pickle

from twisted.internet.defer import inlineCallbacks, returnValue
from labrad.wrappers import connectAsync

def add_device_method(device, method, method_name):
    if type(method).__name__ != 'function':
        method = pickle.loads(method.encode('ISO-8859-1'))
    method = types.MethodType(method, device)
    setattr(device, method_name, method)

class ParameterWrapper(object):
    def __init__(self, config):
        for key, value in config.items():
            setattr(self, key, value)
        
        add_device_method(self, self.initialize, 'initialize')
        add_device_method(self, self.update, 'update')
        add_device_method(self, self.stop, 'stop')

    @inlineCallbacks
    def connect(self):
        self.cxn = yield connectAsync()

    @inlineCallbacks
    def initialize(self):
        yield None

    @inlineCallbacks
    def update(self, value):
        yield None
    
    @inlineCallbacks
    def stop(self):
        yield None

