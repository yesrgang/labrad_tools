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
        self.cxn = yield connectAsync(host='128.138.107.239')
        yield self.cxn.kk.filename(self.filename)
   
    @inlineCallbacks
    def update(self):
        self.value = yield self.cxn.kk.frequency(self.time_window)
