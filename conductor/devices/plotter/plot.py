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

SEP = os.path.sep

class Plot(GenericParameter):
    priority = 1
    @inlineCallbacks
    def initialize(self):
        self.cxn = yield connectAsync()
        self.has_set = False
    
    @inlineCallbacks
    def update(self):
#        if self.value and not self.has_set:
#            self.has_set = True
        if self.value:
            yield self.cxn.plotter.plot(json.dumps(self.value))
#            d = self.value
#            path = d['plotter_path']
#            function_name = d['plotter_function']
#            module_name = path.split(SEP)[-1].strip('.py')
#            module = imp.load_source(module_name, path)
#            plotter_function = getattr(module, d['plotter_function'])
#            try:
#                fig = plotter_function(*d['args'], **d['kwargs'])
#                data = mpld3.fig_to_dict(fig)
#                json_data = json.dumps(data)
#                yield self.cxn.plotter.plot(json_data)
#                plt.close(fig)
#            except Exception, e:
#                print e
