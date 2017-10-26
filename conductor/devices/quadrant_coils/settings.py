import json
from twisted.internet.defer import inlineCallbacks
from labrad.wrappers import connectAsync
from lib.helpers import sleep

from conductor_device.conductor_parameter import ConductorParameter

class Settings(ConductorParameter):
    priority = 1

    @inlineCallbacks
    def initialize(self):
        yield self.connect()
        yield self.cxn.power_supply.select_device('quadrant_coils')
    
    @inlineCallbacks
    def update(self):
        parameter_values = yield self.cxn.conductor.get_parameter_values()
        sequence = json.loads(parameter_values)['sequencer']['sequence']
        yield self.cxn.power_supply.state(False)
        if self._value is not None:
            self.cxn.power_supply.voltage_limit(self._value['voltage'])
            self.cxn.power_supply.current_limit(self._value['current'])
            if 'evaporate' in sequence:
                yield sleep(6)
                yield self.cxn.power_supply.state(self._value['state'])

