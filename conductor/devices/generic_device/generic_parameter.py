from twisted.internet.defer import inlineCallbacks
from labrad.wrappers import connectAsync

class GenericParameter(object):
    def __init__(self, config):
        self.priority = 1
        self.value_type = 'single'
        self.value = None
        for key, value in config.items():
            setattr(self, key, value)

    @inlineCallbacks
    def initialize(self):
        yield None
    
    @inlineCallbacks
    def stop(self):
        yield None

    @inlineCallbacks
    def update(self, value):
        yield None
