from twisted.internet.defer import inlineCallbacks
from labrad.wrappers import connectAsync

from conductor_device.conductor_parameter import ConductorParameter

class Frequency(ConductorParameter):
    priority = 1

    @inlineCallbacks
    def initialize(self):
        yield self.connect()
        yield self.cxn.rf.select_device('beta')
    
    @inlineCallbacks
    def update(self):
        self.value = yield self.cxn.rf.frequency()
