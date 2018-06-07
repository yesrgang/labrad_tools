from twisted.internet.defer import inlineCallbacks
from labrad.wrappers import connectAsync

from conductor_device.conductor_parameter import ConductorParameter

class Frequency(ConductorParameter):
    priority = 1
    sweep_range = 1e6

    @inlineCallbacks
    def initialize(self):
        yield self.connect()
        yield self.cxn.rf.select_device('clock_fiber_aom')
    
    @inlineCallbacks
    def update(self):
        yield self.cxn.rf.frequency(self.value)
