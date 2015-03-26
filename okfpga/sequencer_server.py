from labrad.server import LabradServer, setting, Signal
from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks, returnValue
from sequencer_configuration import SequencerConfiguration
from sequencer_api import SequencerAPI

class SequencerServer(LabradServer):
    name = 'sequencer'

    @inlineCallbacks
    def initServer(self):
        self.api = SequencerAPI()
        self.channels = SequencerConfiguration.channels
        
        self.initialize_board()

    def initialize_board(self):
        connected = self.api.connect_ok_board()
        if not connected:  raise Exception "sequencer not found"




