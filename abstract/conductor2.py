"""
### BEGIN NODE INFO
[info]
name = conductor
version = 1.0
description = 
instancename = %LABRADNODE%_conductor

[startup]
cmdline = %PYTHON% %FILE%
timeout = 20

[shutdown]
message = 987654321
timeout = 20
### END NODE INFO
"""

import json
import ok
import os
import types

from collections import deque
from influxdb import InfluxDBClient
from labrad.server import LabradServer, setting, Signal
from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks, returnValue, DeferredLock
from twisted.internet.task import LoopingCall
from twisted.internet.threads import deferToThread

from okfpga.sequencer.sequence import Sequence

class ConductorServer(LabradServer):
    update_sp = Signal(698123, 'signal: update_sp', 'b')
    def __init__(self, config_name):
        self.experiment_queue = deque([])
        self.experiment = {}
        self.parameters = {}
        self.parameters_history = deque([])
        self.devices = {}

        self.config_name = config_name
        self.load_configuration()
        self.in_communication = DeferredLock()
        LabradServer.__init__(self)

    @inlineCallbacks
    def initServer(self):
        yield LabradServer.initServer(self)
        yield self.run_sequence()
        if self.db_write_period:
            self.dbclient = InfluxDBClient.from_DSN(os.getenv('INFLUXDBDSN'))
            self.write_to_db()

    def load_configuration(self):
        config = __import__(self.config_name).ConductorConfig()
        for key, value in config.__dict__.items():
            setattr(self, key, value)

    @setting(1, 'register device', configuration='s', returns='s')
    def register_device(self, c, configuration):
        """ register device

        configuration = {*device_name: {
            *parameter: {
                'init commands': [*init_command],
                'update commands': [lambda v: *update_command(v)],
                'default value': *default_value,
            }
        }
        """
        configuration = json.loads(configuration)
        for device, parameters in configuration.items():
            self.parameters['devices'][device] = {}
            for parameter, d in paramerers.items():
                value = d['default value']
                for init_command in d['init commands']:
                    yield eval(init_command)
                for update_command in d['update commands']:
                    yield eval(update_command)(value)
                self.parameters[device][parameter] = value
        self.devices.update(configuration)
        returnValue(json.dumps(self.devices))

    @setting(2, 'remove device', device_name='s', returns='s')
    def remove_device(self, c, device_name=None):
        if device_name is not None:
            device = self.devices.pop(device_name)
            value = self.parameters['devices'].pop(device_name)
        return json.dumps(self.devices)

    @setting(3, 'set parameters', parameters='s', returns='s')
    def set_parameters(self, c, parameters=None):
        """ set parameters

        parameters = {*device_name: {*parameter: *value}}
        e.g. {'Clock AOM': {'frequency': {'value': x}}}
             {'sequence': {'T_evap': {'value': x}}}
        """
        if parameters is not None:
            self.parameters = json.loads(parameters)
        returnValue(json.dumps(self.parameters))
    
    @setting(3, 'update parameters', parameters='s', returns='s')
    def set_parameters(self, c, parameters=None):
        if parameters is not None:
            self.parameters.update(json.loads(parameters))
        returnValue(json.dumps(self.parameters))

    @setting(4, 'fix sequence keys', sequence='s', returns='s')
    def fix_sequence_keys(self, c, sequence):
        sequence = json.loads(sequence)
        for sequencer in self.sequencers:
            server = getattr(self.client, sequencer)
            ans = yield server.fix_sequence_keys(json.dumps(sequence))
            sequence = json.loads(ans)
        returnValue(json.dumps(sequence))

    def combine_sequences(self, sequence_list):
        combined_sequence = sequence_list.pop(0)
        for sequence in sequence_list:
            for k in sequence.keys():
                combined_sequence[k] += sequence[k]
        return combined_sequences

    @setting(5, 'set sequence', sequence='s', returns='s')
    def set_sequence(self, c, sequence):
        try:
            sequence = json.loads(sequence)
        except:
            with open(sequence, 'r') as infile:
                sequence = json.load(sequence)
        if type(sequence).__name__ == 'list':
            sequence = self.combine_sequences(sequence)

        fixed_sequence = yield self.fix_sequence_keys(c, sequence)
        self.sequence = json.loads(fixed_sequence)
        returnValue(fixed_sequence)

    @setting(6, 'queue experiment', experiment='s', returns='s')
    def queue_experiment(self, c, experiment):
        """ load experiment into queue

        experiments are json object 
        keys...
            name: some string
            sequence: can be sequence, sequence path, or list of either. 
                      lists are concatenated to form larger sequence.
            parameters: {name: value}
        """
        self.experiment_queue.append(json.loads(experiment))

    def evaluate_device_parameters(self):
        for device, parameters in self.devices.items():
            for parameter, d in paramerers.items():
                value = self.parameters[device][parameter]
                for update_command in d['update commands']:
                    yield eval(update_command)(value)

    def do_evaluate_sequence_parameters(self, x):
        if type(x).__name__ in ['str', 'unicode']:
            if x[0] == '*':
                value = None
                if self.parameters['sequence'].has_key(x):
                    value = self.parameters['sequence'][x]
                else:
                    try:
                        dqs = self.db_query_str.format(str(x))
                        from_db = self.dbclient.query(dqs)
                        print 'taking {} from db'.format(x)
                        value = from_db.get_points().next()['value']
                        self.parameters['sequence'][x] = value
                    except:
                        raise Exception('could not sub var {}'.format(x))
                return value
            else:
                return x
        elif type(x).__name__ == 'list':
            return [self.do_evaluate_sequence_parameters(xx) for xx in x]
        elif type(x).__name__ == 'dict':
            return {k: self.do_evaluate_sequence_parameters(v) for k, v in x.items()}
        else:
            return x
    
    @setting(6, 'evaluate sequence parameters', sequence='s', returns='s')
    def evaluate_sequence_parameters(self, c, sequence=None):
        if sequence is None:
            evaluated_sequence = self.do_evaluate_sequence_parameters(self.sequence)
        else:
            evaluated_sequence = self.do_evaluate_sequence_parameters(sequence)
        return evaluated_sequence

    @inlineCallbacks
    def program_sequencers(self, sequence):
        sequence = self.evaluate_sequence_parameters(sequence)
        for sequencer in self.sequencers:
            server = getattr(self.client, sequencer)
            self.in_communication.acquire()
            yield server.run_sequence(json.dumps(sequence))
            self.in_communication.release()
        returnValue(sequence)

    def do_advance(self, x):
        """ get next values from current experiment """
        if type(x).__name__ == 'list':
            return x.pop(0)
        elif type(x).__name__ == 'dict':
            return {k: self.do_advance(v) for k, v in x.items()}
        else:
            return x

    def advance(self):
        try:
            advanced = self.do_advance(self.expreiment)
        except IndexError:
            if len(self.experiment_queue):
                self.experiment = self.experiment_queue.popleft()
                advanced = self.do_advance(self.expreiment)
                if not advanced.has_key('append data'):
                    advanced.update({'append data': 0})
                if not advanced['append data']:
                    self.data_directory = lambda: 'Z:\\SrQ\\data\\' + time.strftime('%Y%m%d') + '\\'
                    data_directory = self.data_ditectory()
                    if not os.path.exists(data_directory):
                        os.mkdir(data_directory)
                    data_name = advanced.pop['name']
                    data_path = lambda i: data_directory + data_name + '#{}'.format(i)
                    iteration = 0 
                    while os.path.isfile(dat_path(iteration)):
                        iteration += 1
                    self.data_path = data_path(iteration)
            else:
                advanced = {}
        
        if advanced.has_key('parameters'):
            self.parameters.update(advanced.pop('parameters'))
        if advanced.has_key('sequence'):
            self.set_sequence(advanced.pop('sequence'))
        for k, v in advanced.items():
            setattr(self, k, v)
    
    @inlineCallbacks
    def run_sequence(self):
        self.advance()
        yield self.evaluate_device_parameters()
        sequence = self.evaluate_sequence_parameters()
        yield self.program_sequencers(sequence)
        yield self.parameters_updated(True)
        self.history.update(self.parameters)
        duration = sum(sequence['digital@T'])
        reactor.callLater(duration, self.run_sequence)

if __name__ == "__main__":
    from labrad import util
    config_name = 'conductor_config'
    server = ConductorServer(config_name)
    util.runServer(server)