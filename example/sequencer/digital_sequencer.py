import json
import numpy as np

from labrad.server import LabradServer, setting, Signal
from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks, returnValue

class DigitalSequencerServer(LabradServer):
    def __init__(self, config_name):
        LabradServer.__init__(self)
        self.config_name = config_name
        self.load_configuration()
        self.update = Signal(self.update_id, 'signal: update', 's')

    def load_configuration(self):
        config = __import__(self.config_name).DigitalSequencerConfig()
        for key, value in config.__dict__.items():
            setattr(self, key, value)

    def initServer(self):
        pass
   
    def program_sequence(self, sequence):
        pass

    def set_board_mode(self, board, mode):
        pass

    def id2channel(self, channel_id):
        """
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

    @setting(1, 'get channels')
    def get_channels(self, c):
        channels = np.concatenate([[c.key for c in b.channels] for n, b in sorted(self.boards.items())]).tolist()
        return json.dumps(channels)
    
    @setting(11, 'get timing channel')
    def get_timing_channel(self, c):
        return json.dumps(self.timing_channel.name)

    @setting(2, 'run sequence', sequence='s')
    def run_sequence(self, c, sequence):
        sequence = json.loads(sequence)
        self.program_sequence(sequence)

    @setting(3, 'sequencer mode', mode='s')
    def sequencer_mode(self, c, mode=None):
        if mode is not None:
            for board in self.boards.values():
                self.set_board_mode(board, mode)
            self.mode = mode
        return self.mode

    @setting(4, 'channel mode', channel_id='s', mode='s')
    def channel_mode(self, c, channel_id, mode=None):
        channel = self.id2channel(channel_id)
        if mode is not None:
            channel.mode = mode
            board = self.boards[channel.board]
            self.write_channel_modes(board)
        self.notify_listeners(c)
        return channel.mode
    
    def write_channel_modes(self, board): 
        pass

    
    @setting(5, 'channel manual state', channel_id='s', state='i')
    def channel_manual_state(self, c, channel_id, state=None):
        channel = self.id2channel(channel_id)
        if state is not None:
            channel.manual_state = state
            board = self.boards[channel.board]
            self.write_channel_modes(board)
	self.notify_listeners(c)
        return channel.manual_state

    @setting(6, 'channel invert', channel_id='s', invert='i')
    def channel_invert(self, c, channel_id, invert=None):
        channel = self.id2channel(channel_id)
        if invert is not None:
            channel.invert = invert
            board = self.boards[channel.board]
            self.write_channel_modes(board)
        return channel.invert

    @setting(7, 'get channel configuration', channel_id='s')
    def get_channel_configuration(self, c, channel_id):
        channel = self.id2channel(channel_id)
        return json.dumps(channel.__dict__)

    @setting(8, 'notify listeners')
    def notify_listeners(self, c):
        d = {}
        for b in self.boards.values():
            for c in b.channels:
                d[c.key] = c.__dict__
        self.update(json.dumps(d))

    @setting(9, 'fix sequence keys', sequence='s', returns='s')
    def fix_sequence_keys(self, c, sequence):
        sequence = json.loads(sequence)
        sequence_keyfix =  self._fix_sequence_keys(sequence)
        return json.dumps(sequence)
    
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
                        sequence.update({c.key: [c.manual_state for dt in sequence['digital@T']]})
        return sequence
    
    @setting(10, 'reload configuration')
    def reload_configuration(self, c):
        self.load_configuration()


if __name__ == "__main__":
    config_name = 'digital_sequencer_config'
    __server__ = DigitalSequencerServer(config_name)
    from labrad import util
    util.runServer(__server__)
