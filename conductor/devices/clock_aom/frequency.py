from twisted.internet.defer import inlineCallbacks
from labrad.wrappers import connectAsync

from conductor_device.conductor_parameter import ConductorParameter

class Frequency(ConductorParameter):
    priority = 2
    dark_frequency = 43.49e6
    ramp_rate = 1

    @inlineCallbacks
    def initialize(self):
        yield self.connect()
        yield self.cxn.rf.select_device('ad9959_0')
        yield self.cxn.rf.linear_ramp(0, 0, self.ramp_rate)
    
    @inlineCallbacks
    def update(self):
        if self.value is not None:
            min_freq = min([self.value, self.dark_frequency])
            max_freq = max([self.value, self.dark_frequency])
            yield self.cxn.rf.linear_ramp(min_freq, max_freq)

#class Frequency(ConductorParameter):
#    priority = 2
#    dark_frequency = 43.49e6
#    sweep_time = 10e-3
#    ramp_rate = 1
#
#    @inlineCallbacks
#    def initialize(self):
##        yield self.connect()
##        yield self.cxn.rf.select_device('clock_steer')
#
#        yield self.connect()
#        yield self.cxn.rf.select_device('ad9959_0')
#        yield self.cxn.rf.linear_ramp(0, 0, self.ramp_rate)
##        yield self.cxn.rf.linear_ramp(42.495e6, 42.495e6 + 1e6, 1)
#
##        yield self.cxn.yesr5_gpib.select_interface('USB0::0x0699::0x0345::C020003::INSTR')
##        yield self.cxn.yesr5_gpib.write('SOUR1:SWE:RTIM {}'.format(self.sweep_time))
##        yield self.cxn.yesr5_gpib.write('SOUR1:SWE:TIMe {}'.format(self.sweep_time))
#
#    
#    @inlineCallbacks
#    def update(self):
##        start_freq = self.value + self.dark_offset
##        stop_freq = self.value
##        yield self.cxn.yesr5_gpib.write('SOUR1:FREQ {}'.format(stop_freq))
##        yield self.cxn.yesr5_gpib.write('SOUR1:FREQ:STAR {}'.format(start_freq))
##        yield self.cxn.yesr5_gpib.write('SOUR1:FREQ:STOP {}'.format(stop_freq))
#
#
#    #yield self.cxn.rf.frequency(self.value)
#
#        if self.value is not None:
#            yield self.cxn.rf.linear_ramp(self.value, self.dark_frequency)
