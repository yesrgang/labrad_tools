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

from influxdb import InfluxDBClient
from labrad.server import LabradServer, setting, Signal
from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks, returnValue, DeferredLock
from twisted.internet.task import LoopingCall
from twisted.internet.threads import deferToThread

def process_command(command):
    if type(command).__name__ != function:
        try:
            # if command is simple string like "lambda x: print(x)"
            command = eval(command)
        except:
            # if command is marshal dumps
            code = marshal.loads(x.encode('ISO-8859-1'))
            command = types.FunctionType(code, globals(), "marshal code")
    return inlineCallbacks(command)

class ConductorServer(LabradServer):
    parameters_updated = Signal(698124, 'signal: parameters_updated', 'b')
    def __init__(self, config_name):
        self.data = {}
        self.sequence = {'digital@T': [1, 5, 1]}
        self.devices = {}
        self.do_save = 0
        self.experiment_queue = deque([])
        self.experiment = {}
        self.parameters = {'sequence': {}}
        self.received_data = {}

        self.config_name = config_name
        self.load_configuration()
        self.in_communication = DeferredLock()
        LabradServer.__init__(self)

    @inlineCallbacks
    def initServer(self):
        yield LabradServer.initServer(self)
        yield self.set_sequence(None, json.dumps(self.sequence))
        yield self.register_device(None, self.default_devices)
        yield self.run_sequence()
        if self.db_write_period:
            self.dbclient = InfluxDBClient.from_DSN(os.getenv('INFLUXDBDSN'))
            self.write_to_db()

    def load_configuration(self):
        config = __import__(self.config_name).ConductorConfig()
        for key, value in config.__dict__.items():
            setattr(self, key, value)

    @setting(1, 'register device', configuration='s', returns='b')
    def register_device(self, c, configuration):
        """ register device

        configuration = {device_name: {
            parameter: {
                'init_command': init_command(device),
                'update_command': update_command(device, value),
                'value': *value,
            }
        }
        """
        if type(configuration).__name__ == 'str':
            configuration = json.loads(configuration, encoding='ISO-8859-1')
        elif type(configuration).__name__ == 'list':
            def get_device_config(device_name):
                path = 'devices.{}'.format(device_name)
                module = __import__(path, fromlist=['config'])
                return module.config
            configuration = {dn: get_device_config(dn) for dn in configuration}

        self.devices.update(configuration)
        for device, parameters in configuration.items():
            self.parameters[device] = {}
            for parameter, d in parameters.items():
                value = d['value']
                d['init_command'] = process_command(d['init_command'])
                d['update_command'] = process_command(d['update_command'])
                yield d['init_command'](device)
                yield d['update_command'](device, value)
                self.parameters[device][parameter] = value
        returnValue(True)

    @setting(2, 'remove device', device_name='s', returns='s')
    def remove_device(self, c, device_name=None):
        if device_name is not None:
            device = self.devices.pop(device_name)
            value = self.parameters.pop(device_name)
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
        return json.dumps(self.parameters)
    
    @setting(4, 'update parameters', parameters='s', returns='s')
    def update_parameters(self, c, parameters=None):
        if parameters is not None:
            parameters = json.loads(parameters)
            for device_name, device in parameters.items():
                if not self.parameters.has_key(device_name):
                    self.parameters[device_name] = {}
                for parameter_name, value in device.items():
                    self.parameters[device_name][parameter_name] = value
        return json.dumps(self.parameters)

    @setting(5, 'enable parameters', parameters='s', returns='s')
    def enable_parameters(self, c, parameters=None):
        if parameters is not None:
            for device_name, device in json.loads(parameters).items():
                for parameter_name, parameter in device.items():
                    self.devices[device_name][parameter_name]['enabled'] = parameter
        returns = {}
        for device_name, device in self.devices.items():
            returns[device_name] = {}
            for parameter_name, parameter in device.items():
                returns[device_name][parameter_name] = parameter['enabled']
        return json.dumps(returns)

    @setting(6, 'fix sequence keys', sequence='s', returns='s')
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

    @setting(7, 'set sequence', sequence='s', returns='s')
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

    @setting(8, 'queue experiment', experiment='s', returns='i')
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

    @setting(9, 'set experiment queue', experiment_queue='s', returns='i')
    def set_experiment_queue(self, c, experiment_queue=None):
        if experiment_queue:
            experiment_queue = json.loads(experiment_queue)
            for experiment in experiment_queue:
                self.experiment_queue.append(experiment)
        else:
            self.experiment_queue = deque([])
        return len(self.experiment_queue)

    @setting(10, 'stop experiment')
    def stop_experiment(self, c):
        self.do_save = 0
        self.experiment = {}

    @inlineCallbacks
    def evaluate_device_parameters(self):
        for device, parameters in self.devices.items():
            for parameter, d in parameters.items():
                value = self.parameters[device][parameter]
                yield d['update command'](idevice, value)

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
    
    @setting(11, 'evaluate sequence parameters', sequence='s', returns='s')
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

    @setting(12, 'send data', data='s', returns='s')
    def send_data(self, c, data):
        data = json.loads(data)
        for d in data.values():
            d['timestamp'] = time.time()
        self.received_data.update(data)
        print 'received data from {}'.format(data.keys())
        return json.dumps(data)

    @setting(13, 'get data', returns='s')
    def get_data(self, c):
        return json.dumps(self.data)

    @setting(14, 'get received data', returns='s')
    def get_data(self, c):
        return json.dumps(self.received_data)

    def update_data(self, data_key):
        new_data = copy.deepcopy(getattr(self, data_key))
        if data_key == 'sequence':
            print new_data.keys()
        self.data = self.append_data(self.data, new_data)

    def write_data(self):
        print 'writing: ', self.data.keys()
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

    def do_display(self):
        if self.experiment.has_key('display'):
            exec(str(self.experiment['display']))
            display(self.data)

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
        if advanced.has_key('display'):
            self.display = advanced['display']
    
    @inlineCallbacks
    def run_sequence(self):
        try:
            sequence = self.evaluate_sequence_parameters(None)
            duration = sum(sequence['digital@T'])
            if self.do_save:
                self.update_data('parameters')
                self.update_data_call = reactor.callLater(duration-2, self.update_data, 'received_data')
                self.write_data_call = reactor.callLater(duration-1., self.write_data)
            yield self.advance()
            sequence = yield self.program_sequencers()
            yield self.parameters_updated(True)
            duration = sum(sequence['digital@T'])
            self.run_sequence_call = reactor.callLater(duration, self.run_sequence)
            yield self.evaluate_device_parameters()
        except Exception, e:
            print "error running sequence. will try again in 10 seconds"
            print e
            self.run_sequence_call = reactor.callLater(10, self.run_sequence)

    def write_to_db(self):
        self.write_to_db_call = reactor.callLater(self.db_write_period, self.write_to_db)
        parameters = self.parameters

        def to_float(x):
            try:
                return float(x)
            except:
                return 0.

        to_db = [{
            "measurement": "experiment parameters",
            "tags": {"device": device_name, "parameter": p},
            "fields": {"value": to_float(v)},
        } for device_name, device in self.parameters.items() for p, v in device.items()]

        try:
            self.dbclient.write_points(to_db)
        except:
            print "failed to save parameters to database"

if __name__ == "__main__":
    from labrad import util
    config_name = 'config'
    server = ConductorServer(config_name)
    util.runServer(server)
