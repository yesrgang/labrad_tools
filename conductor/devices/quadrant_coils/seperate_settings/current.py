import json
from twisted.internet.defer import inlineCallbacks
from labrad.wrappers import connectAsync
from lib.helpers import sleep

from conductor_device.conductor_parameter import ConductorParameter

class Current(ConductorParameter):
    priority = 1

    @inlineCallbacks
    def initialize(self):
        self.cxn = yield connectAsync(name=self.name)
        yield self.cxn.power_supply.select_device('quadrant_coils')
    
    @inlineCallbacks
    def update(self):
        yield self.cxn.power_supply.current_limit(self._value)
