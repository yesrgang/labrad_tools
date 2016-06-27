import json
import numpy as np
import os

import labrad

node = os.getenv('LABRADNODE')

class Scan(object):
    def __init__(self, **kwargs):
        for kw in kwargs:
            setattr(self, kw, kwargs[kw])

    def queue(self, clear_all=False):
        cxn = labrad.connect()
        c = getattr(cxn, '{}_conductor'.format(node))
        experiment = {}
        for attr in ['name', 'parameters', 'display']:
            if hasattr(self, attr):
                experiment[attr] = getattr(self, attr)
        for attr in ['sequence']:
            if hasattr(self, attr):
                experiment[attr] = json.dumps(getattr(self, attr))
        if clear_all:
            c.set_experiment_queue()
            c.stop_experiment()
        c.queue_experiment(json.dumps(experiment))

class Loop(object):
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
    
    def queue(self, clear_all=False):
        cxn = labrad.connect()
        c = getattr(cxn, '{}_conductor'.format(node))
        experiment = {}
        for attr in ['name', 'parameters', 'display']:
            if hasattr(self, attr):
                experiment[attr] = getattr(self, attr)
        for attr in ['sequence']:
            if hasattr(self, attr):
                experiment[attr] = json.dumps(getattr(self, attr))
        experiment['loop'] = 1
        experiment['append_data'] = 0
        if clear_all:
            c.set_experiment_queue()
            c.stop_experiment()
        c.queue_experiment(json.dumps(experiment))


