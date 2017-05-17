import sys
sys.path.append('../')
from generic_device.generic_parameter import GenericParameter

from twisted.internet.defer import inlineCallbacks
from labrad.wrappers import connectAsync


class CenterFrequency(GenericParameter):
    priority = 1
    @inlineCallbacks
    def initialize(self):
        self.cxn = yield connectAsync()
        yield self.cxn.rf.select_device('clock_center')
    
    @inlineCallbacks
    def update(self):
        yield self.cxn.rf.frequency(self.value)
