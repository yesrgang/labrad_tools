import imp
import json
import os
import sys

import mpld3
from labrad.wrappers import connectAsync
from twisted.internet.defer import inlineCallbacks

from matplotlib import pyplot as plt

sys.path.append('../')
from generic_device.generic_parameter import GenericParameter

class Plot(GenericParameter):
    priority = 1
#    value_type = 'once'

    @inlineCallbacks
    def initialize(self):
        self.cxn = yield connectAsync()
    
    @inlineCallbacks
    def update(self):
        if self.value:
            yield self.cxn.plotter.plot(json.dumps(self.value))
