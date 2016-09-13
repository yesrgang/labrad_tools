import os

from datetime import date, timedelta
from itertools import chain

from twisted.internet.defer import inlineCallbacks

SEQUENCE_DIRECTORY = 'Z:\\SrQ\\data\\{}\\sequences\\'
DB_QUERY_STRING = 'SELECT value FROM "experiment parameters" WHERE "device" = \
                  \'sequence\' AND "parameter" = \'{}\' ORDER BY time \
                  DESC LIMIT 1'

#def read_sequence_file(self, filename):
#    if not os.path.exists(filename):
#        for i in range(365):
#            day = date.today() - timedelta(i)
#            path = SEQ_DIRECTORY.format(day.strftime('%Y%m%d')) + filename
#            if os.path.exists(filename):
#    with open(sequence_filename, 'r') as infile:
#         sequence = json.load(infile)
#    return sequence

def combine_sequences(self, sequence_list):
    combined_sequence = sequence_list.pop(0)
    for sequence in sequence_list:
        for k in sequence.keys():
            combined_sequence[k] += sequence[k]
    return combined_sequence

def get_sequence_parameters(x):
    """ determine which parameters we need to get from conductor or db """
    if type(x).__name__ in ['str', 'unicode'] and x[0] == '*':
        return [x]
    elif type(x).__name__ == 'list':
        return list(chain.from_iterable([get_sequence_parameters(xx) for xx in x]))
    elif type(x).__name__ == 'dict':
        return list(chain.from_iterable([get_sequence_parameters(v) for v in x.values()]))
    else:
        return []

def substitute_sequence_parameters(x, parameter_values)
    if type(x).__name__ in ['str', 'unicode']:
        if x[0] == '*':
            return parameters[x]
        else:
            return x
    elif type(x).__name__ == 'list':
        return [substitute_sequence_parameters(xx, parameter_values) for xx in x]
    elif type(x).__name__ == 'dict':
        return {k: substitute_sequence_parameters(v, parameter_values) for k, v in x.items()}

class Sequence(object):
    def __init__(self):
        self.priority = 2
        self.value_type = 'dict'
        self.value = None

    @inlineCallbacks
    def initialize(self):
        self.cxn = yield connectAsync()
        yield self.cxn.sequencer.select_device('ABCD')

    @inlineCallbacks
    def stop(self):
        yield None

    @inlineCallbacks
    def update(self, value):
        """ value can be sequence or list of sequences """
        try:
            parameterized_sequence = single_sequence(value)
            parameters = get_parameters(sequence)
            parameter_values = yield self.get_parameter_values(parameters)
            substituted_sequence = substitute_sequence_parameters(sequence, 
                                                               parameter_values)
            yield self.cxn.sequencer.run_sequence(substituted_sequence)
        except Exception, e:
            print e
            callLater(5, self.cxn.conductor.advance)

    @inlineCallbacks
    def get_parameter_values(self, parameters):
        parameter_values = {}
        ans = yield self.cxn.conductor.get_parameter_values()
        conductor_parameters = json.loads(ans)['sequencer']
        for parameter in parameters:
            if parameter in conductor_parameters:
                parameter_values[parameter] = conductor_parameters[parameter]
            else:
                try:
                    dbqs = DB_QUERY_STRING.format(parameter)
                    from_db = self.dbclient.query(dbqs)
                    value = from_db.get_points().next()['value']
                    parameter_values[parameter] = value
                except:
                    msg = 'could not substitute variable {}'.format(parameter)
                    raise Exception(msg)
        return parameter_values
