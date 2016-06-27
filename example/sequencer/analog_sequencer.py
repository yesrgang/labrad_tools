import time
import numpy as np
import json

from labrad.server import LabradServer, setting, Signal
from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet.threads import deferToThread

from analog_ramps import *

class AnalogSequencerServer(LabradServer):
    """Communicate with DAC board"""
    def __init__(self, config_name):
        LabradServer.__init__(self)
        self.config_name = config_name
        self.load_configuration()
        self.update = Signal(self.update_id, 'signal: update', 's')

    def load_configuration(self):
        config = __import__(self.config_name).AnalogSequencerConfig()
        for key, value in config.__dict__.items():
            setattr(self, key, value)

    def initServer(self):
        pass

    def id2channel(self, channel_id):
        """take generic id and try to match channel

        expect 3 possibilities for channel_id.
        1) name -> return channel with that name
        2) @loc -> return channel at that location
        3) name@loc -> first try name, then location
        """
        channel = None
        try:
            name, loc = channel_id.split('@')
        except:
            name = channel_id
            loc = None
        if name:
            for b in self.boards.values():
                for c in b.channels:
                    if c.name == name:
                        channel = c
        if not channel:
            for b in self.boards.values():
                for c in b.channels:
                    if c.loc == loc:
                        channel = c
        return channel

    def time_to_ticks(self, board, time):
        """specify time in seconds return number of ticks at board clock rate"""
        return int(board.clk_frequency*time)

    def program_sequence(self, sequence):
        pass
    
    def set_board_mode(self, board, mode):
        pass

    @setting(01, 'get channels')
    def get_channels(self, c):
        """returns json object of {channelname: config}"""
        channels = np.concatenate([[c.key for c in b.channels] for n, b in sorted(self.boards.items())]).tolist()
        return json.dumps(channels)

    @setting(07, 'run sequence', sequence='s')
    def run_sequence(self, c, sequence):
        """program sequence and then set board mode to run"""
        sequence = json.loads(sequence)
        self.program_sequence(sequence)

    @setting(04, 'channel mode', channel_id='s', mode='s')
    def channel_mode(self, c, channel_id, mode=None):
        """who does the DAC listen to?

        'auto': listen to programmed sequence
        'manual': listen to manual voltage
        """
        channel = self.id2channel(channel_id)
        if mode is not None:
            channel.mode = mode
            board = self.boards[channel.loc[0]]
            self.write_channel_modes(board)
        self.notify_listeners(c)
        return channel.mode
    
    def write_channel_modes(self, board):
        pass
    
    @setting(05, 'channel manual voltage', channel_id='s', voltage='v')
    def channel_manual_voltage(self, c, channel_id, voltage=None):
        """set channel output value for manual mode"""
        channel = self.id2channel(channel_id)
        if voltage is not None:
            voltage = sorted([-10, voltage, 10])[1]
            channel.manual_voltage = voltage
            self.write_manual_voltage(channel)
        self.notify_listeners(c)
        return channel.manual_voltage

    def write_manual_voltage(self, channel): 
        pass


    @setting(06, 'get channel configuration', channel_id='s')
    def get_channel_configuration(self, c, channel_id):
        """returns JSON channel configuration"""
        channel = self.id2channel(channel_id)
        return json.dumps(channel.__dict__)


    @setting(10, 'notify listeners')
    def notify_listeners(self, c):
        """emit update signal
        
        call to update clients
        """
        d = {}
    	for b in self.boards.values():
            for c in b.channels:
                d[c.key] = c.__dict__
        self.update(json.dumps(d))
    
    @setting(11, 'fix sequence keys', sequence='s', returns='s')
    def fix_sequence_keys(self, c, sequence):
        sequence = json.loads(sequence)
        sequence_keyfix =  self._fix_sequence_keys(sequence)
        return json.dumps(sequence_keyfix)
    
    def _fix_sequence_keys(self, sequence):
        # take sequence name@loc to configuration name@loc
        locs = [key.split('@')[1] for key in sequence.keys()]

        for key in sequence.keys():
            name, loc = key.split('@')
            for board in self.boards.values():
                for c in board.channels:
                    if c.loc == loc:
                        s = sequence.pop(key)
                        sequence.update({c.key: s})
                    elif c.loc not in locs:
                        sequence.update({c.key: [{'type': 'lin', 'vf': 0, 'dt': dt} for dt in sequence['digital@T']]})
        return sequence

if __name__ == "__main__":
    config_name = 'analog_sequencer_config'
    __server__ = AnalogSequencerServer(config_name)
    from labrad import util
    util.runServer(__server__)
