from twisted.internet.defer import inlineCallbacks
from labrad.wrappers import connectAsync

from conductor_device.conductor_parameter import ConductorParameter

class PulseTime(ConductorParameter):
    priority = 1
    value = 0.5

    @inlineCallbacks
    def initialize(self):
        yield self.connect()
        yield self.cxn.yesr5_gpib.select_interface('USB0::0x0699::0x0345::C020003::INSTR')
    
    @inlineCallbacks
    def update(self):
        yield self.cxn.yesr5_gpib.write('SOUR1:SWE:HTIM {}'.format(self.value))
