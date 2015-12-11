import json

import ok
from labrad.server import LabradServer, setting, Signal
from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks, returnValue, DeferredLock
from twisted.internet.task import LoopingCall
from twisted.internet.threads import deferToThread

from okfpga.sequencer.sequence import Sequence

class ConductorServer(LabradServer):
    name = '%LABRADNODE% Conductor'
    def __init__(self, config_name):
        self.sequence = {}
        self.parameters = {}
        LabradServer.__init__(self)
        self.config_name = config_name
        self.load_configuration()
        self.in_communication = DeferredLock()
	self.update = Signal(self.update_id, 'signal: update', 's')

    @inlineCallbacks
    def initServer(self):
        yield LabradServer.initServer(self)
        yield self.run_sequence()

    def load_configuration(self):
        config = __import__(self.config_name).ConductorConfig()
        for key, value in config.__dict__.items():
            setattr(self, key, value)
    
    @setting(2, 'load sequence', sequence='s', returns='s')
    def load_sequence(self, c, sequence):
        sequence_keyfix = {}
        for sequencer in self.sequencers:
            server = getattr(self.client, sequencer)
            s = yield server.fix_sequence_keys(sequence)
            sequence_keyfix.update(s)
        self.sequence = Sequence(sequence_keyfix)
        return self.sequence.dump()

    @setting(3, 'set parameters', parameters='s')
    def set_parameters(self, c, parameters):
        parameters = json.loads(parameters)
        """
        parameters is dictionary {name: value}
        """
        self.parameters = parameters

    def evaluate_next_parameters(self, sequence):
        next_parameters = {}
        for p, v in self.parameters.items():
            if type(v) is types.ListType:
                if len(v) == 1:
                    next_parameters[p] = v[0]
                else:
                    next_parameters[p] = v.pop(0)
            else:
                next_parameters[p] = v
        
        next_sequence = sequence.dump()
        for p, v in next_parameters:
            next_sequence.replace('"'+p+'"', str(v))
        return next_sequence

    @setting(4, 'asdf')
    def asdf(self, c):
        return '!'
   
    @inlineCallbacks
    def run_sequence(self):
        if self.sequence:
            sequence = self.evaluate_next_parameters(self.sequence)
            for sequencer in self.sequencers:
                server = getattr(self.client, sequencer)
                self.in_communication.acquire()
                yield None
#                yield server.run_sequence(sequence)
                self.in_communication.release()
            reactor.callLater(self.sequence.get_duration(), self.run_sequence)
        else:
            reactor.callLater(5, self.run_sequence)
            

if __name__ == "__main__":
    config_name = 'conductor_config'
    __server__ = ConductorServer(config_name)
    from labrad import util
    util.runServer(__server__)
