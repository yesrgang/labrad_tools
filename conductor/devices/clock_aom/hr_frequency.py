from twisted.internet.defer import inlineCallbacks
from labrad.wrappers import connectAsync

from conductor_device.conductor_parameter import ConductorParameter

class HrFrequency(ConductorParameter):
    priority = 2
    dark_frequency = 43.49e6
    ramp_rate = 1

    @inlineCallbacks
    def initialize(self):
        yield self.connect()
        yield self.cxn.rf.select_device('ad9956_1')
        yield self.cxn.rf.linear_ramp(0, 0, self.ramp_rate)
#        print 'hr_frequency init\'d with rr: {}'.format(self.ramp_rate)
    
    @inlineCallbacks
    def update(self):
        if self.value is not None:
            print '?'
#            min_freq = min([self.value, self.dark_frequency])
#            max_freq = max([self.value, self.dark_frequency])
#            yield self.cxn.rf.linear_ramp(min_freq, max_freq, self.ramp_rate)
            min_freq = min([self.value, self.value + self.dark_offset])
            max_freq = max([self.value, self.value + self.dark_offset])
            yield self.cxn.rf.linear_ramp(min_freq, max_freq, self.ramp_rate)
