from twisted.internet.defer import inlineCallbacks
from labrad.wrappers import connectAsync

from conductor_device.conductor_parameter import ConductorParameter

class CenterDemodFrequency(ConductorParameter):
    priority = 2
    dark_frequency = 135.27e6
#    ramp_range = 1e6
#    dark_offset = 1e6
    ramp_rate = 1

    @inlineCallbacks
    def initialize(self):
        yield self.connect()
        yield self.cxn.rf.select_device('ad9959_3')
        yield self.cxn.rf.linear_ramp(0, 0, self.ramp_rate)
    
    @inlineCallbacks
    def update(self):
        if self.value is not None:
#            min_freq = min([self.value, self.dark_frequency])
#            max_freq = max([self.value, self.dark_frequency])
#            yield self.cxn.rf.linear_ramp(min_freq, max_freq)
            min_freq = min([self.value, self.value + self.dark_offset])
            max_freq = max([self.value, self.value + self.dark_offset])
            yield self.cxn.rf.linear_ramp(min_freq, max_freq, self.ramp_rate)
