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

import copy
import json
import marshal
import os
import sys
import time
import types

from collections import deque

from labrad.server import LabradServer, setting, Signal
from twisted.internet.reactor import callLater
from twisted.internet.defer import inlineCallbacks, returnValue, DeferredLock
from twisted.internet.task import LoopingCall

from devices.parameter_wrapper import ParameterWrapper

def get_device_config(device_name):
    path = 'devices.{}'.format(device_name)
    module = __import__(path, fromlist=['config'])
    return module.config

class ConductorServer(LabradServer):
    parameters_updated = Signal(698124, 'signal: parameters_updated', 'b')
    name = '%LABRADNODE%_conductor'
    def __init__(self, config_name):
        self.data = {}
        self.default_sequence = {'digital@T': [1, 5, 1]}
        self.devices = {}
        self.do_save = 0
        self.experiment_queue = deque([])
        self.experiment = {}
        self.parameters = {'sequence': {}}
        self.received_data = {}
        self.default_devices = {}

        self.config_name = config_name
        self.load_config()
        self.in_communication = DeferredLock()
        LabradServer.__init__(self)

    @inlineCallbacks
    def initServer(self):
        yield LabradServer.initServer(self)
        yield self.set_sequence(None, json.dumps(self.default_sequence))
        yield self.register_device(None, self.default_devices)
        yield self.run_sequence()

    def load_config(self):
        config = __import__(self.config_name).ConductorConfig()
        for key, value in config.__dict__.items():
            setattr(self, key, value)

    @setting(2, config='s'):
    def register_device_parameters(self, c, config):
        """
        config = {
            device_name: {
                parameter_name: {
                    'initialize': initialize(),
                    'update': update(value),
                    'stop': stop(),
                    'value': value,
                }
        }
        """
        if type(config).__name__ == 'str':
            config = json.loads(config)

        for device_name, device_config in config.items():
            if not device_config:
                device_config = get_device_config(device_name)
            else:
                device_config = json.loads(device_config, encoding='ISO-8859-1')
            if not self.devices.has_key(device_name):
                self.devices[device_name] = {}
            if not self.parameters.has_key(device_name):
                self.parameters[device_name] = {}

            for parameter_name, parameter_config in device_config.items():
                parameter = ParameterWrapper(parameter_config)
                value = parameter.value
                yield parameter.connect()
                yield parameter.initialize()
                yield parameter.update(value)
                self.devices[device_name][parameter_name] = parameter
                self.parameters[device_name][parameter_name] = value
            returnValue(True)

    @setting(2, device_name='s', returns='b')
    def remove_devices(self, c, device_name):
        """ remove entire device """
        config = {device_name: parameter_name 
                for parameter_name in self.devices[device_name].keys()}
        yield self.remove_device_parameters(json.dumps(config))
        returnValue(True)
    
    @setting(2, config='s', returns='b')
    def remove_device_parameters(self, c, config):
        """ remove specified device_parameter

        config = {
            device_name: parameter_name,
        }
        """
        for device_name, parameter_name in json.loads(config).items():
            parameter = self.devices[device_name].pop(parameter_name)
            value = self.parameters[device_name].pop(parameter_name)
            yield parameter.stop()
            if not self.devices[device_name]:
                self.devices.pop(device_name)
            if not self.parameters[device_name]:
                self.parameters.pop(device_name)
        returnValue(True)

    @setting(3, returns='s')
    def get_device_list(self, c):
        return json.dumps(self.devices.keys())

    @setting(3, returns='s')
    def get_parameters(self, c):
        return json.dumps(self.parameters)
    
    @setting(4, config='s', returns='s')
    def set_parameter_values(self, c, config):
        config = json.loads(config)
        for device_name, device_config in config.items():
            if not self.parameters.has_key(device_name):
                self.parameters[device_name] = {}
            for parameter_name, parameter_value in device_config.items():
                self.parameters[device_name][parameter_name] = parameter_value
        return True

    @setting(6, sequence='s', returns='s')
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
        return combined_sequence

    def read_sequence_file(self, sequence_filename):
        try:
            if not os.path.exists(sequence_filename):
                sequence_filename = self.data_directory() + 'sequences' + \
                                    os.path.sep + sequence_filename
            with open(sequence_filename, 'r') as infile:
                sequence = json.load(infile)
            return sequence
        except Exception, e:
            return sequence_filename

    @setting(7, sequence='s', returns='s')
    def set_sequence(self, c, sequence):
        try:
            sequence = json.loads(sequence)
            if type(sequence).__name__ == 'list':
                sequence = self.combine_sequences([self.read_sequence_file(s) 
                                                   for s in sequence])
            else:
                sequence = self.read_sequence_file(sequence)
            fixed_sequence = yield self.fix_sequence_keys(c, json.dumps(sequence))
            self.sequence = json.loads(fixed_sequence)
            returnValue(fixed_sequence)
        except Exception, e: 
            print 'unable to load sequence'
            print e

    @setting(8, experiment='s', returns='i')
    def queue_experiment(self, c, experiment):
        """ load experiment into queue

        experiments are json object 
        keys...
            'name': some string
            'sequence': can be sequence, sequence path, or json.dumps(list of either).
                      lists are concatenated to form larger sequence.
            'parameters': {name: value}
            'append data': bool, save data to previous file?
            'loop': bool, inserts experiment back into begining of queue
        """
        self.experiment_queue.append(json.loads(experiment))
        return len(self.experiment_queue)

    @setting(9, experiment_queue='s', returns='i')
    def set_experiment_queue(self, c, experiment_queue=None):
        if experiment_queue:
            experiment_queue = json.loads(experiment_queue)
            for experiment in experiment_queue:
                self.experiment_queue.append(experiment)
        else:
            self.experiment_queue = deque([])
        return len(self.experiment_queue)

    @setting(10, returns='b')
    def stop_experiment(self, c):
        self.do_save = 0
        self.experiment = {}
        return True

    @inlineCallbacks
    def evaluate_device_parameters(self):
        for device_name, parameters in self.devices.items():
            for parameter_name, parameter in parameters.items():
                value = self.parameters[device_name][parameter_name]
                yield parameter.update(value)

    def do_evaluate_sequence_parameters(self, x):
        if type(x).__name__ in ['str', 'unicode']:
            if x[0] == '*':
                value = None
                if self.parameters['sequence'].has_key(x):
                    value = self.parameters['sequence'][x]
                else:
                    try:
                        dqs = self.db_query_str.format(str(x))
                        print 'taking {} from db'.format(x)
                        from_db = self.dbclient.query(dqs)
                        value = from_db.get_points().next()['value']
                        self.parameters['sequence'][x] = value
                    except:
                        raise Exception('could not sub var {}'.format(x))
                        #print 'could not sub var {}. setting to zero'.format(x)
                        #self.parameters['sequence'][x] = 0
                return value
            else:
                return x
        elif type(x).__name__ == 'list':
            return [self.do_evaluate_sequence_parameters(xx) for xx in x]
        elif type(x).__name__ == 'dict':
            return {k: self.do_evaluate_sequence_parameters(v) for k, v in x.items()}
        else:
            return x
    
    @setting(11, sequence='s', returns='s')
    def evaluate_sequence_parameters(self, c, sequence=None):
        if sequence is None:
            evaluated_sequence = self.do_evaluate_sequence_parameters(self.sequence)
        else:
            sequence = json.loads(sequence)
            evaluated_sequence = self.do_evaluate_sequence_parameters(sequence)
            evaluated_sequence = json.dumps(evaluated_sequence)
        return evaluated_sequence

    @inlineCallbacks
    def program_sequencers(self):
        sequence = self.evaluate_sequence_parameters(None)
        for sequencer in self.sequencers:
            server = getattr(self.client, sequencer)
            self.in_communication.acquire()
            yield server.run_sequence(json.dumps(sequence))
            self.in_communication.release()
        returnValue(sequence)

    @setting(12, data='s', returns='s')
    def send_data(self, c, data):
        data = json.loads(data)
        for d in data.values():
            d['timestamp'] = time.time()
        self.received_data.update(data)
        return json.dumps(data)

    @setting(13, returns='s')
    def get_data(self, c):
        return json.dumps(self.data)

    @setting(14, returns='s')
    def get_received_data(self, c):
        return json.dumps(self.received_data)

    def update_data(self, data_key):
        new_data = copy.deepcopy(getattr(self, data_key))
        if data_key == 'sequence':
            print new_data.keys()
        self.data = self.append_data(self.data, new_data)

    def write_data(self):
        with open(self.data_path, 'w') as outfile:
            json.dump(self.data, outfile)
 
    def append_data(self, x1, x2):
        """ recursivly append dict to {..{[]}..} """
        if type(x2).__name__ == 'dict':
            for k in x2.keys():
                if not x1.has_key(k):
                    x1[k] = x2.pop(k) 
            appended = {k: self.append_data(x1[k], x2[k]) for k in x2.keys()}
            x1.update(appended)
            return x1
        else:
            if not type(x1).__name__ == 'list':
                x1 = [x1]
            if not type(x2).__name__ == 'list':
                x2 = [x2]
            return x1 + x2

    def do_advance(self, x):
        """ get next values from current experiment """
        if type(x).__name__ == 'list':
            return x.pop(0)
        elif type(x).__name__ == 'dict':
            return {k: self.do_advance(v) for k, v in x.items()}
        else:
            return x

    @inlineCallbacks
    def advance(self):
        do_save = 1
        try:
            if not self.experiment:
                raise IndexError
            advanced = self.do_advance(self.experiment)

        # IndexError means experiment is over/need to get next experiment in queue
        except IndexError:
            if len(self.experiment_queue):
                # get next experiment from queue
                self.experiment = self.experiment_queue.popleft()
                experiment_copy = copy.deepcopy(self.experiment)
                
                # set defaults if no value
                if not self.experiment.has_key('loop'):
                    self.experiment.update({'loop': 0})
                if not self.experiment.has_key('append_data'):
                    self.experiment.update({'append_data': 0})
                
                # if this experiment should loop, append to begining of queue
                if self.experiment['loop']:
                    if not experiment_copy['append_data']:
                        self.data = {}
                    experiment_copy['append_data'] = 1
                    self.experiment_queue.appendleft(experiment_copy)

                advanced = self.do_advance(self.experiment)
                
                # determine where to save data
                data_directory = self.data_directory()
                if not os.path.exists(data_directory):
                    os.mkdir(data_directory )
                data_name = advanced['name']
                data_path = lambda i: data_directory + data_name + '#{}'.format(i)
                iteration = 0 
                while os.path.isfile(data_path(iteration)):
                    iteration += 1
                if advanced['append_data']:
                    iteration -= 1
                    iteration = max(iteration, 0)
                    try: 
                        if not advanced['loop']:
                            with open(data_path(iteration), 'r') as infile:
                                self.data = json.load(infile)
                    except: 
                        self.data = {}
                else: 
                    self.data = {}
                self.data_path = data_path(iteration)
                if not (advanced['loop'] and advanced['append_data']):
                    print 'saving data to {}'.format(self.data_path)
            else:
                print 'experiment queue is empty'
                advanced = {}
                do_save = 0

        self.do_save = do_save
        if advanced.has_key('parameters'):
            parameters = advanced['parameters']
            p = yield self.update_parameters(None, json.dumps(parameters))
        if advanced.has_key('sequence'):
            self.set_sequence(None, json.dumps(advanced['sequence']))
    
    @inlineCallbacks
    def run_sequence(self):
        try:
            sequence = self.evaluate_sequence_parameters(None)
            duration = sum(sequence['digital@T'])
            if self.do_save:
                self.update_data('parameters')
                self.update_data_call = callLater(duration-2, self.update_data, 'received_data')
                self.write_data_call = callLater(duration-1., self.write_data)
            yield self.advance()
            sequence = yield self.program_sequencers()
            yield self.parameters_updated(True)
            duration = sum(sequence['digital@T'])
            self.run_sequence_call = callLater(duration, self.run_sequence)
            yield self.evaluate_device_parameters()
        except Exception, e:
            print "error running sequence. will try again in 10 seconds"
            print e
            self.run_sequence_call = callLater(10, self.run_sequence)


if __name__ == "__main__":
    from labrad import util
    config_name = 'config'
    server = ConductorServer(config_name)
    util.runServer(server)
