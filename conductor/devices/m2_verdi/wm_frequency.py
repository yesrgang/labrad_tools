from twisted.internet.defer import inlineCallbacks

from conductor_device.conductor_parameter import ConductorParameter
    
class WmFrequency(ConductorParameter):
    priority = 1
    center_frequency = 368.55468e12
    frequency_span = 200e6
    
    @inlineCallbacks
    def initialize(self):
        yield self.connect()
    
    @inlineCallbacks
    def update(self):
        response = yield self.cxn.yesr8_hfwm.get_frequency(1)
        if response is None:
            return

        frequency = float(response['Hz'])
        self.value = frequency
       
        min_frequency = self.center_frequency - self.frequency_span / 2
        max_frequency = self.center_frequency + self.frequency_span / 2
        if frequency != sorted([min_frequency, frequency, max_frequency])[1]:
            yield self.cxn.beeper.beep('m2 verdi mode hop')
