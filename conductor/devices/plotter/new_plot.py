import json
from copy import deepcopy

from labrad.wrappers import connectAsync
from twisted.internet.defer import inlineCallbacks

from matplotlib import pyplot as plt

from conductor_device.conductor_parameter import ConductorParameter

class NewPlot(ConductorParameter):
    priority = 1

    @inlineCallbacks
    def initialize(self):
        yield self.connect()
    
    @inlineCallbacks
    def update(self):
        data_copy = deepcopy(self.conductor.data)
        if self.value:
            yield self.cxn.new_plotter.plot(json.dumps(self.value), 
                    json.dumps(data_copy, default=lambda x: None))
