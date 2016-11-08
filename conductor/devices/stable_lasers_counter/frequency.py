import sys
sys.path.append('../')
from generic_device.generic_parameter import GenericParameter

import labrad

from twisted.internet.defer import inlineCallbacks
from twisted.internet.threads import deferToThread
from labrad.wrappers import connectAsync


class Frequency(GenericParameter):
    priority = 1
    @inlineCallbacks
    def initialize(self):
        self.cxn = yield connectAsync()
        yield self.cxn.frequency_counter.select_device('stable_lasers_beat')
   
    @inlineCallbacks
    def update(self):
        self._value = yield self.cxn.frequency_counter.frequency(wait=False)
