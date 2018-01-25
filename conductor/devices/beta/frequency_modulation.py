from twisted.internet.defer import inlineCallbacks
from labrad.wrappers import connectAsync
import vxi11

from conductor_device.conductor_parameter import ConductorParameter

class FrequencyModulation(ConductorParameter):
    priority = 1
    waveforms = {
        'red_mot': 'INT:\\BETA.ARB',
        'red_mot-fast': 'INT:\\BETA_FAST.ARB',
        }
    vxi11_address = '192.168.1.24'

    @inlineCallbacks
    def initialize(self):
        yield None
        self.inst = vxi11.Instrument(self.vxi11_address)
        self.inst.write('SOUR2:DATA:VOL:CLE')
        for waveform in self.waveforms.values():
            self.inst.write('MMEM:LOAD:DATA2 "{}"'.format(waveform))
            self.inst.write('SOUR2:FUNC:ARB "{}"'.format(waveform))
    
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
                self.inst.write('SOUR2:FUNC:ARB "{}"'.format(waveform))
