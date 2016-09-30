import sys
sys.path.append('../')
from generic_device.generic_parameter import GenericParameter

from twisted.internet.defer import inlineCallbacks
from labrad.wrappers import connectAsync

class Frequency(GenericParameter):
    @inlineCallbacks
    def initialize(self):
        self.cxn = yield connectAsync()
        yield self.cxn.rf.select_device('clock_steer')
    
    @inlineCallbacks
    def update(self, value):
        ans = yield self.cxn.rf.frequency(value)
