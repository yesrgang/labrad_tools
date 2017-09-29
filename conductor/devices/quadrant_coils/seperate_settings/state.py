import json
from twisted.internet.defer import inlineCallbacks
from labrad.wrappers import connectAsync
from lib.helpers import sleep

from conductor_device.conductor_parameter import ConductorParameter

class State(ConductorParameter):
    priority = 1

    @inlineCallbacks
    def initialize(self):
        self.cxn = yield connectAsync(name=self.name)
        yield self.cxn.power_supply.select_device('quadrant_coils')
    
    @inlineCallbacks
    def update(self):
        parameter_values = yield self.cxn.conductor.get_parameter_values()
        sequence = json.loads(parameter_values)['sequencer']['sequence']
        yield self.cxn.power_supply.state(False)
        if 'evaporate' in sequence:
            yield sleep(6)
            yield self.cxn.power_supply.state(self._value)
