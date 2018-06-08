import json
from copy import deepcopy

from labrad.wrappers import connectAsync
from twisted.internet.defer import inlineCallbacks

from conductor_device.conductor_parameter import ConductorParameter

class Plot(ConductorParameter):
    priority = 1

    @inlineCallbacks
    def initialize(self):
        yield self.connect()
    
    @inlineCallbacks
    def update(self):
        data_copy = deepcopy(self.conductor.data)
        if self.value:
            yield self.cxn.plotter.plot(json.dumps(self.value), 
                    json.dumps(data_copy, default=lambda x: None))
