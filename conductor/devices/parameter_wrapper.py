import types
import marshal
import pickle

from twisted.internet.defer import inlineCallbacks, returnValue
from labrad.wrappers import connectAsync

def add_device_method(device, method, method_name):
    if type(method).__name__ != 'function':
        try:
            # if method is simple string like "lambda x: print(x)"
            method = eval(method)
        except:
            # if method is marshal dumps
            method = marshal.loads(x.encode('ISO-8859-1'))
    method = types.MethodType(method, device)
    setattr(device, method_name, inlineCallbacks(method))

def add_device_method(device, method, method_name):
    if type(method).__name__ != 'function':
        method = pickle.loads(method.encode('ISO-8859-1'))
    method = types.MethodType(method, device)
    setattr(device, method_name, method)

class ParameterWrapper(object):
    def __init__(self, config):
        self.initialize = "yield lambda self: yield None"
        self.update = "yield lambda self, value: yield None"

        for key, value in config.items():
            setattr(self, key, value)
        
        add_device_method(self, self.initialize, 'initialize')
        add_device_method(self, self.update, 'update')

    @inlineCallbacks
    def connect(self):
        self.cxn = yield connectAsync()

