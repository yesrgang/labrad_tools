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
import types

import ok
from labrad.server import LabradServer, setting, Signal
from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks, returnValue, DeferredLock
from twisted.internet.task import LoopingCall
from twisted.internet.threads import deferToThread

from okfpga.sequencer.sequence import Sequence

class ConductorServer(LabradServer):
    update_sp = Signal(698123, 'signal: update_sp', 'b')
    previous_sequence_parameters = [None, None, None]
    previous_device_parameters = [None, None, None]
    def __init__(self, config_name):
        self.device_parameters = {}
        self.sequence_parameters = {}
        self.sequence = {}
        self.config_name = config_name
        self.load_configuration()
        self.in_communication = DeferredLock()
        LabradServer.__init__(self)

    @inlineCallbacks
    def initServer(self):
        yield LabradServer.initServer(self)
        yield self.run_sequence()

    def load_configuration(self):
        config = __import__(self.config_name).ConductorConfig()
        for key, value in config.__dict__.items():
            setattr(self, key, value)

    @setting(1, 'set device parameters', device_parameters='s', returns='s')
    def set_device_parameters(self, c, device_parameters=None):
        """ replace server device parameters with input!

        device parameters is "{*device_name: {*parameter_name: {command: *command, value: *value}}}"
        *command is something like "lambda value: sever_name.setting(value)"
        """
        if device_parameters is not None:
            device_parameters = json.loads(device_parameters)
            yield self.initialize_device_parameters(device_parameters)
            self.device_parameters = device_parameters
        returnValue(json.dumps(self.device_parameters))

    @setting(2, 'update device parameters', device_parameters='s', returns='s')
    def update_device_parameters(self, c, device_parameters=None):
        """ edit existing device parameters

        device parameters is "{*device_name: {*parameter_name: {command: *command, value: *value}}}"
        *command is something like "lambda value: sever_name.setting(value)"
        """
        if device_parameters is not None:
            device_parameters = json.loads(device_parameters)
            yield self.initialize_device_parameters(device_parameters)
            self.device_parameters.update(device_parameters)
        returnValue(json.dumps(self.device_parameters))
    
    @setting(3, 'update device parameter values', device_parameters='s', returns='s')
    def update_device_parameter_values(self, c, device_parameters='s'):
        """update device parameter value only
        
        give device parameters {device: {parameter: {value: *value}}}
        """
        for devname, dev in json.loads(device_parameters):
            for parname, par in dev:
                self.device_parameters[devname][parname]['value'] = par['value']
        return self.device_parameters

    @setting(4, 'remove device', device_name='s', returns='b')
    def remove_device(self, c, device_name):
        parameters = self.device_parameters.pop(device_name)
        if parameters:
            return True
        else: 
            return False

    @inlineCallbacks
    def initialize_device_parameters(self, device_parameters):
        value = None
        for device, parameters in device_parameters.items():
            for p, d in parameters.items():
                if type(d['value']) is types.ListType:
                    value = d['value'][0]
                else:
                    value = d['value']
            yield eval(d['init command'])
            yield eval(d['command'])(value)

    def evaluate_device_parameters(self):
        value = None
        current_parameters = {}
        for device, parameters in self.device_parameters.items():
            for p, d in parameters.items():
                if type(d['value']) is types.ListType:
                    value = d['value'][0]
                    d['value'].insert(len(d['value']), d['value'].pop(0))
                else:
                    value = d['value']
                current_parameters[device] = {}
                current_parameters[device][p] = value
                self = self
                eval(d['command'])(value)
        self.previous_device_parameters.pop(0)
        self.previous_device_parameters.append(current_parameters)
    
    @setting(5, 'set sequence parameters', sequence_parameters='s', returns='s')
    def set_sequence_parameters(self, c, sequence_parameters=None):
        """
        parameters is dictionary {name: value}
        """
        if sequence_parameters is not None:
            self.sequence_parameters = json.loads(sequence_parameters)
        yield self.update_sp(True)
        returnValue(json.dumps(self.sequence_parameters))
    
    @setting(6, 'update sequence parameters', sequence_parameters='s', returns='s')
    def update_sequence_parameters(self, c, sequence_parameters=None):
        """
        parameters is dictionary {name: value}
        """
        if sequence_parameters is not None:
            self.sequence_parameters.update(json.loads(sequence_parameters))
        yield self.update_sp(True)
        returnValue(json.dumps(self.sequence_parameters))
    
    @setting(7, 'evaluate sequence parameters', sequence='s', returns='s') 
    def evaluate_sequence_parameters(self, c, sequence):
        sequence = Sequence(sequence)
        return self._evaluate_sequence_parameters(sequence)

    def _evaluate_sequence_parameters(self, sequence):
        current_parameters = {}
        for p, v in self.sequence_parameters.items():
            if type(v) is types.ListType:
                current_parameters[p] = v[0]
            else:
                current_parameters[p] = v
        self.previous_sequence_parameters.pop(0)
        self.previous_sequence_parameters.append(current_parameters)
        current_sequence = sequence.dump()
        for p, v in current_parameters.items():
            current_sequence = current_sequence.replace('"{}"'.format(p), str(v))
        return current_sequence

    def advance_sequence_parameters(self):
        for p, v in self.sequence_parameters.items():
            if type(v) is types.ListType:
                v.insert(len(v), v.pop(0))

    @setting(8, 'get previous parameters', returns='s')
    def get_previous_parameters(self, c):
        previous_parameters = {}
        previous_parameters.update(self.previous_sequence_parameters[0])
        previous_parameters.update(self.previous_device_parameters[0])
        return json.dumps(previous_parameters)

    @setting(9, 'load sequence', sequence='s', returns='s')
    def load_sequence(self, c, sequence):
        sequence_keyfix = {}
        for sequencer in self.sequencers:
            server = getattr(self.client, sequencer)
            s = yield server.fix_sequence_keys(sequence)
            sequence_keyfix.update(json.loads(s))
        self.sequence = Sequence(sequence_keyfix)
        returnValue(self.sequence.dump())

    @setting(10, 'get sequence', returns='s')
    def get_sequence(self, c):
        return self.sequence.dump()

    @inlineCallbacks
    def run_sequence(self):
        self.evaluate_device_parameters()
        if self.sequence:
            sequence = self._evaluate_sequence_parameters(self.sequence)
            self.update_sp(True)
            for sequencer in self.sequencers:
                server = getattr(self.client, sequencer)
                self.in_communication.acquire()
                yield server.run_sequence(str(sequence))
                self.in_communication.release()
            reactor.callLater(Sequence(sequence).get_duration(), self.run_sequence)
	    self.advance_sequence_parameters()
        else:
            reactor.callLater(5, self.run_sequence)

if __name__ == "__main__":
    config_name = 'conductor_config'
    __server__ = ConductorServer(config_name)
    from labrad import util
    util.runServer(__server__)
