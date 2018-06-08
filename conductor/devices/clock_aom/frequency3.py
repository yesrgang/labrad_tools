from twisted.internet.defer import inlineCallbacks
from labrad.wrappers import connectAsync

from conductor_device.conductor_parameter import ConductorParameter

class Frequency3(ConductorParameter):
    priority = 1

    @inlineCallbacks
    def initialize(self):
        yield self.connect()
        yield self.cxn.rf.select_device('clock_steer3')
    
    @inlineCallbacks
    def update(self):
        yield self.cxn.rf.frequency(self.value)
