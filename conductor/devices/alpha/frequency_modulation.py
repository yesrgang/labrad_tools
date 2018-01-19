from twisted.internet.defer import inlineCallbacks
from labrad.wrappers import connectAsync
import vxi11

from conductor_device.conductor_parameter import ConductorParameter

class FrequencyModulation(ConductorParameter):
    priority = 1
    waveforms = {
        'red_mot': 'INT:\\alpha.arb',
        'red_mot-fast': 'INT:\\alpha_fast.arb',
#        'red_mot': 'ALPHA',
#        'red_mot-fast': 'ALPHA_FAST',
        }

    @inlineCallbacks
    def initialize(self):
        yield None
        self.inst = vxi11.Instrument('sr3waveform.colorado.edu')
    
    @inlineCallbacks
    def update(self):
        yield None
        try:
            sequence = self.conductor.parameters['sequencer']['sequence'].value
        except:
            sequence = []
        for subsequence, waveform in self.waveforms.items():
            if subsequence in sequence:
#                self.inst.write('SOUR1:DATA:VOL:CLE')
#                self.inst.write('MMEM:LOAD:DATA1 "{}"'.format(waveform))
                self.inst.write('SOUR1:FUNC:ARB "{}"'.format(waveform))
