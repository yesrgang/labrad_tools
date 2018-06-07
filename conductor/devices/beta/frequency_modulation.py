from twisted.internet.defer import inlineCallbacks
from labrad.wrappers import connectAsync
import vxi11

from conductor_device.conductor_parameter import ConductorParameter

class FrequencyModulation(ConductorParameter):
    priority = 1
    waveforms = {
        'red_mot': 'INT:\\BETA.ARB',
        'rm_tof': 'INT:\\BETA.ARB',
        'red_mot-fast': 'INT:\\BETA_FAST.ARB',
        'red_mot-fast-tof': 'INT:\\BETA_FAST.ARB',
        }

    @inlineCallbacks
    def initialize(self):
        yield self.connect()
        yield self.cxn.awg.select_device('beta_fm')
    
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
