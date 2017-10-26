from labrad.wrappers import connectAsync
import sys
from twisted.internet.defer import inlineCallbacks

sys.path.append('../')
from conductor_device.conductor_parameter import ConductorParameter

class PicomotorPosition(ConductorParameter):
    priority = 2
    previous_value = None

    @inlineCallbacks
    def initialize(self):
        yield self.connect()
        yield self.cxn.picomotor.select_device(self.name)
    
    @inlineCallbacks
    def update(self):
        if self.value != self.previous_value:
            yield self.cxn.picomotor.position(self.value)
            self.previous_value = self.value
