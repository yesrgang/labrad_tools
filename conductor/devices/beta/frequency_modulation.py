from twisted.internet.defer import inlineCallbacks
from labrad.wrappers import connectAsync
import vxi11

from conductor_device.conductor_parameter import ConductorParameter

class FrequencyModulation(ConductorParameter):
    priority = 1
    waveforms = {
        'red_mot': 'INT:\\BETA.ARB',
        'red_mot-fast': 'INT:\\BETA_FAST.ARB',
#        'red_mot': 'BETA',
#        'red_mot-fast': 'BETA_FAST',
        }

    @inlineCallbacks
    def initialize(self):
        yield None
        self.inst = vxi11.Instrument('sr3waveform.colorado.edu')
    
    @inlineCallbacks
    def terminate(self):
        yield None
        self.inst.close()
    
    @inlineCallbacks
    def update(self):
        yield None
        try:
            sequence = self.conductor.parameters['sequencer']['sequence'].value
        except:
            sequence = []
        for subsequence, waveform in self.waveforms.items():
            if subsequence in sequence:
#                self.inst.write('SOUR2:DATA:VOL:CLE')
#                self.inst.write('MMEM:LOAD:DATA2 "{}"'.format(waveform))
                self.inst.write('SOUR2:FUNC:ARB "{}"'.format(waveform))
