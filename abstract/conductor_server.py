"""
### BEGIN NODE INFO
[info]
name = conductor
version = 1.0
description = 
instancename = %LABRADNODE% conductor

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
from labrad.server import LabradServer, setting, Signal
from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks, returnValue

from okfpga.sequencer.sequence import Sequence

class ConductorServer(LabradServer):
    def __init__(self, config_name):
        LabradServer.__init__(self)
        self.config_name = config_name
        self.load_configuration()
	self.update = Signal(self.update_id, 'signal: update', 's')

    def load_configuration(self):
        config = __import__(self.config_name).ConductorConfig()
        for key, value in config.__dict__.items():
            setattr(self, key, value)
    
    def initServer(self):
        dseq = getattr(self.client, 'yesr20_digital_sequencer')
        channels = yield dseq.get_channels()

    def run_sequence(self, sequence):
        for sequencer in self.sequencers:
            server = getattr(self.client, sequencer)
            yield server.run_sequence(sequence)
            

if __name__ == "__main__":
    config_name = 'conductor_config'
    __server__ = ConductorServer(config_name)
    from labrad import util
    util.runServer(__server__)
