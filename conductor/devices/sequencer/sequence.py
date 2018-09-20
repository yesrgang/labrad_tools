import sys
import json
import time

from twisted.internet.defer import inlineCallbacks
from twisted.internet.reactor import callInThread
from labrad.wrappers import connectAsync

from conductor_device.conductor_parameter import ConductorParameter
from lib.helpers import *

class Sequence(ConductorParameter):
    priority = 11
    value_type = 'list'

    auto_trigger = True
#    auto_trigger = False

    def __init__(self, config={}):
        super(Sequence, self).__init__(config)
        self.value = [self.default_sequence]

    @inlineCallbacks
    def initialize(self):
        yield self.connect()
        yield self.cxn.yesr20_okfpga.select_interface('Sr2 dev.')
        yield self.update()

    @inlineCallbacks
    def update(self):
        """ value can be sequence or list of sub-sequences """
        t_advance = 5
        if self.value:
            parameterized_sequence = value_to_sequence(self)
            parameters = get_parameters(parameterized_sequence)
            parameters_json = json.dumps({'sequencer': parameters})
            pv_json = yield self.cxn.conductor.get_parameter_values(
                    parameters_json, True)
            parameter_values = json.loads(pv_json)['sequencer']
            sequence = substitute_sequence_parameters(parameterized_sequence,
                                                      parameter_values)
            yield self.cxn.sequencer.run_sequence(json.dumps(sequence))
            t_advance = get_duration(sequence)
        
        yield self.conductor.set_parameter_value('sequencer', 'cycle_time', t_advance, True)
        if self.auto_trigger:
           callInThread(auto_trigger_advance, self.cxn.yesr20_okfpga, self.conductor)
        else:    
            yield self.cxn.conductor.advance(t_advance)
