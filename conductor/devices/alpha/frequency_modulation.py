from twisted.internet.defer import inlineCallbacks
from labrad.wrappers import connectAsync
import vxi11

from conductor_device.conductor_parameter import ConductorParameter

class FrequencyModulation(ConductorParameter):
    priority = 1
    waveforms = {
#        'red_mot': 'INT:\\alpha.arb',
#        'rm_tof': 'INT:\\alpha.arb',
#        'red_mot-fast': 'INT:\\alpha_fast.arb',
#        'red_mot-fast-tof': 'INT:\\alpha_fast.arb',
        'red_mot': 'INT:\\ALPHA.ARB',
        'rm_tof': 'INT:\\ALPHA.ARB',
        'red_mot-fast': 'INT:\\ALPHA_FAST.ARB',
        'red_mot-fast-tof': 'INT:\\ALPHA_FAST.ARB',
        }

    @inlineCallbacks
    def initialize(self):
        yield self.connect()
        yield self.cxn.awg.select_device('alpha_fm')
    
    @inlineCallbacks
    def update(self):
        yield None
        try:
            sequence = self.conductor.parameters['sequencer']['sequence'].value
        except:
            sequence = []
        for subsequence, waveform in self.waveforms.items():
            if subsequence in sequence:
                yield self.cxn.awg.waveform(waveform)
