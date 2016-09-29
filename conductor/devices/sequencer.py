import json
import os
from datetime import date, timedelta
from itertools import chain

from twisted.internet.defer import inlineCallbacks
from twisted.internet.reactor import callLater
from labrad.wrappers import connectAsync

SEQUENCE_DIRECTORY = 'Z:\\SrQ\\data\\{}\\sequences\\'


def value_to_sequence(value):
    if type(value).__name__ == 'list':
        return combine_sequences([read_sequence_file(v) for v in value])
    else:
        return value

def read_sequence_file(filename):
    if type(filename).__name__ == 'dict':
        return filename
    if not os.path.exists(filename):
        for i in range(365):
            day = date.today() - timedelta(i)
            path = SEQ_DIRECTORY.format(day.strftime('%Y%m%d')) + filename
            if os.path.exists(path):
                filename = path
                break
    with open(filename, 'r') as infile:
         sequence = json.load(infile)
    return sequence

def combine_sequences(sequence_list):
    combined_sequence = sequence_list.pop(0)
    for sequence in sequence_list:
        for k in sequence.keys():
            combined_sequence[k] += sequence[k]
    return combined_sequence

def get_parameters(x):
    """ determine which parameters we need to get from conductor or db """
    if type(x).__name__ in ['str', 'unicode'] and x[0] == '*':
        return [x]
    elif type(x).__name__ == 'list':
        return list(chain.from_iterable([get_parameters(xx) for xx in x]))
    elif type(x).__name__ == 'dict':
        return list(chain.from_iterable([get_parameters(v) for v in x.values()]))
    else:
        return []

def substitute_sequence_parameters(x, parameter_values):
    if type(x).__name__ in ['str', 'unicode']:
        if x[0] == '*':
            return parameter_values[x]
        else:
            return x
    elif type(x).__name__ == 'list':
        return [substitute_sequence_parameters(xx, parameter_values) for xx in x]
    elif type(x).__name__ == 'dict':
        return {k: substitute_sequence_parameters(v, parameter_values) for k, v in x.items()}
    else:
        return x

def get_duration(sequence):
    return max([sum([s['dt'] for s in cs]) for cs in sequence.values()])

class Sequence(object):
    def __init__(self):
        self.priority = 2
        self.value_type = 'dict'
        self.value = None

    @inlineCallbacks
    def initialize(self):
        self.cxn = yield connectAsync()
    
    @inlineCallbacks
    def stop(self):
        yield None

    @inlineCallbacks
    def update(self, value):
        """ value can be sequence or list of sequences """
        t_advance = 5
        if value:
            parameterized_sequence = value_to_sequence(value)
            parameters = get_parameters(parameterized_sequence)
            parameters_json = json.dumps({'sequencer': parameters})
            pv_json = yield self.cxn.conductor.get_parameter_values(parameters_json,
                                                                    True)
            parameter_values = json.loads(pv_json)['sequencer']
            sequence = substitute_sequence_parameters(parameterized_sequence,
                                                      parameter_values)
            yield self.cxn.sequencer.run_sequence(json.dumps(sequence))
            t_advance = get_duration(sequence)
        yield self.cxn.conductor.advance(t_advance)
