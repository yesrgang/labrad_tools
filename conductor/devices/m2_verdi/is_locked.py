from twisted.internet.defer import inlineCallbacks
from labrad.wrappers import connectAsync

from conductor_device.conductor_parameter import ConductorParameter
    
class IsLocked(ConductorParameter):
    priority = 1
    busy = False
    locked_threshold = -10
    
    @inlineCallbacks
    def initialize(self):
        yield self.connect()
        # device name looks wrong, but is correct
        yield self.cxn.spectrum_analyzer.select_device('red_mot')
    
    @inlineCallbacks
    def update(self):
        if not self.busy:
            try:
                self.busy = True
                trace = yield self.cxn.spectrum_analyzer.trace()
                if max(trace) >= self.locked_threshold:
                    self.value = True
                else:
                    self.value = False
                    yield self.cxn.beeper.beep('m2 verdi unlocked')
            except Exception as e:
                raise e
            finally:
                self.busy = False

