import json

from twisted.internet.defer import inlineCallbacks
from labrad.wrappers import connectAsync


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
