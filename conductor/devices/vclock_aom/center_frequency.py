from twisted.internet.defer import inlineCallbacks
from labrad.wrappers import connectAsync

from conductor_device.conductor_parameter import ConductorParameter

class CenterFrequency(ConductorParameter):
    priority = 2

    @inlineCallbacks
    def initialize(self):
        yield self.connect()
        yield self.cxn.rf.select_device('vclock_center')
    
    @inlineCallbacks
    def update(self):
        yield self.cxn.rf.frequency(self.value)
