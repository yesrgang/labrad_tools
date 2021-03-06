from twisted.internet.defer import inlineCallbacks

from conductor_device.conductor_parameter import ConductorParameter

class Frequency(ConductorParameter):
    priority = 1

    @inlineCallbacks
    def initialize(self):
        yield self.connect()
    
    @inlineCallbacks
    def update(self):
        if self.value is None:
            response = yield self.cxn.si_demod.get_frequency()
            self.value = 8 * float(response)

