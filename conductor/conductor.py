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
import inflection
import json
import os
import time

from collections import deque

from labrad.server import LabradServer, setting, Signal
from twisted.internet.reactor import callLater
from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet.task import LoopingCall

from devices.generic_parameter import GenericParameter

def get_device_config(device_name):
    path = 'devices.{}'.format(device_name)
    module = __import__(path, fromlist=['config'])
    return module.config

def import_parameter(device_name, parameter_name):
    path = 'devices.{}'.format(device_name)
    class_name = inflection.camelize(parameter_name)
    module = __import__(path, fromlist=[class_name])
    return getattr(module, class_name)

def remaining_points(parameters):
    try:
        return min([len(p.value) for dp in parameters.values() for p in dp.values()])
    except:
        return 0

def advance_parameter_value(parameter):
    value = parameter.value
    if type(value).__name__ == 'list':
        old = value.pop(0)
        if len(value) <= 1:
            parameter.value = value[0]

def get_parameter_value(parameter):
    value = parameter.value
    if parameter.value_type == 'single' and type(value).__name__ == 'list':
        return value[0]
    else: 
        return value

class ConductorServer(LabradServer):
    parameters_updated = Signal(698124, 'signal: parameters_updated', 'b')
    name = 'conductor'

    def __init__(self, config_name):
        self.parameters = {}
        self.experiment_queue = deque([])
        self.data = {}
        self.data_path = None

        self.config_name = config_name
        self.load_config()
        LabradServer.__init__(self)
    
    def load_config(self):
        config = __import__(self.config_name).ConductorConfig()
        for key, value in config.__dict__.items():
            setattr(self, key, value)

    @inlineCallbacks
    def initServer(self):
        yield LabradServer.initServer(self)
        yield self.register_parameters(None, self.default_parameters)

    @setting(2, config='s', returns='b')
    def register_parameters(self, c, config):
        """
        config = {
            device_name: {
                parameter_name: {
                    parameter_object... needs 'initialize', 'update', 'stop' callables
                                              'value' is pretty much anything.
                }
        }
        """
        if type(config).__name__ == 'str':
            config = json.loads(config)

        for device_name, device_parameters in config.items():
            if not self.parameters.get(device_name):
                self.parameters[device_name] = {}
            for parameter_name, Parameter in device_parameters.items():
                if not self.parameters.get(parameter_name):
                    self.parameters[device_name][parameter_name] = []
                if not Parameter:
                    Parameter = import_parameter(device_name, parameter_name)
                parameter = Parameter()
                self.parameters[device_name][parameter_name] = parameter
                yield parameter.initialize()
                yield self.update_parameter(device_name, parameter_name)

        returnValue(True)

    @setting(3, config='s', returns='b')
    def remove_parameters(self, c, config):
        """ remove specified device_parameter

        config = {
            device_name: parameter_name,
        }
        """
        if config in self.parameters:
            device_name = config
            for parameter_name in self.parameters[device_name].items():
                yield self.remove_parameter(device_name, parameter_name)
        else:
            for device_name, parameter_name in json.loads(config).items():
                yield self.remove_device_parameter(device_name, parameter_name)
        returnValue(True)
    
    @inlineCallbacks
    def remove_parameter(self, device_name, parameter_name):
        parameter = self.parameters[device_name].pop(parameter_name)
        if not self.parameters[device_name]:
            self.parameters.pop(device_name)
        try:
            yield parameter.stop()
        except:
            print '{} {} was improperly removed from available devices.'.format(
                                                    device_name, parameter_name)

    @setting(4, config='s', returns='b')
    def set_parameter_values(self, c, config):
        for device_name, device_parameters in json.loads(config).items():
            if not self.parameters.get(device_name):
                self.parameters[device_name] = {}
            for parameter_name, parameter_value in device_parameters.items():
                if not self.parameters[device_name].get(parameter_name):
                    self.parameters[device_name][parameter_name] = GenericParameter()
                self.parameters[device_name][parameter_name].value = parameter_value
        return True

    @setting(5, returns='s')
    def get_parameter_values(self, c):
        return json.dumps({dn: {pn: get_parameter_value(p)} 
                           for pn, p in d.items()
                           for dn, d in self.parameters.items()})
    
    @setting(8, experiment='s', returns='i')
    def queue_experiment(self, c, experiment):
        """ load experiment into queue

        experiments are json object 
        keys...
            'name': some string. required.

            'parameter_values': {name: value}. optional.
            'append data': bool, save data to previous file? optional.
            'loop': bool, inserts experiment back into begining of queue optional.
        """
        self.experiment_queue.append(json.loads(experiment))
        return len(self.experiment_queue)

    @setting(9, experiment_queue='s', returns='i')
    def set_experiment_queue(self, c, experiment_queue=None):
        self.experiment_queue = deque([])
        if experiment_queue:
            experiment_queue = json.loads(experiment_queue)
            for experiment in experiment_queue:
                self.experiment_queue.append(experiment)
        return len(self.experiment_queue)

    @setting(10, returns='b')
    def stop_experiment(self, c):
        # !!! replace parameter value lists with single value.
        self.data = {}
        return True

    @setting(13, returns='s')
    def get_data(self, c):
        return json.dumps(self.data)
    
    @inlineCallbacks
    def advance_experiment(self):
        if len(self.experiment_queue):
            # get next experiment from queue and keep a copy
            experiment = self.experiment_queue.popleft()
            experiment_copy = copy.deepcopy(experiment)
            
            parameter_values = experiment.get('parameter_values')
            if parameter_values:
                yield self.set_parameter_values(None, json.dumps(parameter_values))

            # if this experiment should loop, append to begining of queue
            if experiment.get('loop'):
                # now we require appending data
                experiment_copy['append_data'] = True
                # add experiment to begining of queue
                self.experiment_queue.appendleft(experiment_copy)
            
            if not experiment.get('append_data'):
                self.data = {}

                # determine data path
                data_directory = self.data_directory()
                data_path = lambda i: str(data_directory 
                                          + experiment['name'] 
                                          + '#{}'.format(i))
                iteration = 0 
                while os.path.isfile(data_path(iteration)):
                    iteration += 1
                self.data_path = data_path(iteration)
                
                print 'saving data to {}'.format(self.data_path)
                if not os.path.exists(data_directory):
                    os.mkdir(data_directory)

                returnValue(True)
        else:
            self.data = {}
            if self.data_path:
                print 'experiment queue is empty'
            self.data_path = None
            returnValue(False)

    @inlineCallbacks
    def advance_parameters(self):
        advanced = False
        # check if we need to load next experiment
        if not remaining_points(self.parameters):
            advanced = self.advance_experiment()

        # sort by priority. higher priority is called first. 
        # keep in mind still async...
        # maybe in the future we can make some priority level blocking.
        priority_parameters = [(dn, pn, p) for dn, dp in self.parameters.items()
                                 for pn, p in dp.items()
                                 if p.priority]

        # advance parameter values if parameter has priority
        for device_name, parameter_name, parameter in priority_parameters:
            if not advanced:
                advance_parameter_value(parameter)
        
        # call parameter updates in order of priority. 
        # 1 is called last. 0 is never called.
        for device_name, parameter_name, parameter in sorted(
                priority_parameters, key=lambda x: x[2].priority):
            yield self.update_parameter(device_name, parameter_name)

        # signal update
        yield self.parameters_updated(True)

    @inlineCallbacks
    def update_parameter(self, device_name, parameter_name):
        parameter = self.parameters[device_name][parameter_name]
        try:
            value = get_parameter_value(parameter)
            yield parameter.update(value)
        except Exception, e:
            print e
            print 'could not update {} {}. removing parameter'
            self.remove_parameter(device_name, parameter_name)

    def save_parameters(self):
        if self.data:
            data_length = max([len(p) for dp in self.data.values()
                                      for p in dp.values()])
        else:
            data_length = 0
        
        for device_name, device_parameters in self.parameters.items():
            if not self.data.get(device_name):
                self.data[device_name] = {}
            for parameter_name, parameter in device_parameters.items():
                if not self.data[device_name].get(parameter_name):
                    self.data[device_name][parameter_name] = []
                parameter_data = self.data[device_name][parameter_name] 
                while len(parameter_data) < data_length:
                    parameter_data.append(None)
                new_value = get_parameter_value(parameter)
                parameter_data.append(new_value)
        
        if self.data_path:
            with open(self.data_path, 'w+') as outfile:
                json.dump(self.data, outfile)

    @setting(14)
    def advance(self, c):
        self.save_parameters()
        yield self.advance_parameters()

if __name__ == "__main__":
    from labrad import util
    config_name = 'config'
    server = ConductorServer(config_name)
    util.runServer(server)
