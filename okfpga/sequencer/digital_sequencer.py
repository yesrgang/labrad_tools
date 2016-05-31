"""
### BEGIN NODE INFO
[info]
name = digital_sequencer
version = 1.0
description = 
instancename = %LABRADNODE%_digital_sequencer

[startup]
cmdline = %PYTHON% %FILE%
timeout = 20

[shutdown]
message = 987654321
timeout = 20
### END NODE INFO
"""
import json
import numpy as np

import ok
from labrad.server import LabradServer, setting, Signal
from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks, returnValue

from sequence import Sequence

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
        for board in self.boards.values():
            success = self.initialize_board(board)
            if not success:
                self.boards.pop(board)
        self.initialize_outputs()
    
    def initialize_board(self, board):
        fp = ok.FrontPanel()
        module_count = fp.GetDeviceCount()
        print "found {} unused devices".format(module_count)
        for i in range(module_count):
            serial = fp.GetDeviceListSerial(i)
            tmp = ok.FrontPanel()
            tmp.OpenBySerial(serial)
            iden = tmp.GetDeviceID()
            if iden == board.device_id:
                board.xem = tmp
                print 'connected to {}'.format(iden)
                board.xem.LoadDefaultPLLConfiguration() 
                prog = board.xem.ConfigureFPGA(board.bit_file)
                if prog:
                   print "unable to program sequencer"
                   return False
                return True
        return False
    
    def initialize_outputs(self):
        for b in self.boards.values():
	    self.write_channel_modes(b)
	    self.write_channel_stateinvs(b)

    def time_to_ticks(self, board, time):
        return int(board.clk_frequency*time)

    def make_sequence(self, board, sequence):
        #sequence = self._fix_sequence_keys(sequence)

        # make sure trigger happens on first run
        for c in board.channels:
            sequence[c.key].insert(0, sequence[c.key][0])
        sequence[self.timing_channel.name].insert(0, 10e-6)
        sequence['Trigger@D15'][0] = 1

	# allow for sequencer's ramp to zero
        for c in board.channels:
            sequence[c.key].append(sequence[c.key][-1])
        sequence[self.timing_channel.name].append(1)
        sequence['Trigger@D15'][-1] = 1

        # for now, assume each channel_sequence has same timings
        programmable_sequence = [(dt, [sequence[c.key][i] for c in board.channels]) for i, dt in enumerate(sequence[self.timing_channel.name])]
        
        ba = []
        for t, l in programmable_sequence:
            ba += list([sum([2**j for j, b in enumerate(l[i:i+8]) if b]) for i in range(0, 64, 8)])
            ba += list([int(eval(hex(self.time_to_ticks(board, t))) >> i & 0xff) for i in range(0, 32, 8)])
        ba += [0]*96
        return ba, sequence
    
    def program_sequence(self, sequence):
        updated_sequence = {}
        for board in self.boards.values():
            ba, s = self.make_sequence(board, sequence)
            self.set_board_mode(board, 'idle')
            self.set_board_mode(board, 'load')
            board.xem.WriteToPipeIn(board.pipe_wire, bytearray(ba))
            self.set_board_mode(board, 'idle')
            updated_sequence.update(s)
        return updated_sequence

    def set_board_mode(self, board, mode):
        board.xem.SetWireInValue(board.mode_wire, board.mode_nums[mode])
        board.xem.UpdateWireIns()
        board.seuqencer_mode = mode

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
        sequence = Sequence(sequence)
        self.program_sequence(sequence)
        for board in self.boards.values():
            self.set_board_mode(board, 'run')

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
            self.write_channel_stateinvs(board)
        self.notify_listeners(c)
        return channel.mode
    
    def write_channel_modes(self, board): 
        cm_list = [c.mode for c in board.channels]
        bas = [sum([2**j for j, m in enumerate(cm_list[i:i+16]) if m == 'manual']) for i in range(0, 64, 16)]
        for ba, wire in zip(bas, board.channel_mode_wires):
            board.xem.SetWireInValue(wire, ba)
        board.xem.UpdateWireIns()
    
    def write_channel_stateinvs(self, board): 
        cm_list = [c.mode for c in board.channels]
        cs_list = [c.manual_state for c in board.channels]
        ci_list = [c.invert for c in board.channels]
        bas = [sum([2**j for j, (m, s, i) in enumerate(zip(cm_list[i:i+16], cs_list[i:i+16], ci_list[i:i+16])) if (m=='manual' and s!=i) or (m=='auto' and i==True)]) for i in range(0, 64, 16)]
        for ba, wire in zip(bas, board.channel_stateinv_wires):
            board.xem.SetWireInValue(wire, ba)
        board.xem.UpdateWireIns()

    @setting(5, 'channel manual state', channel_id='s', state='i')
    def channel_manual_state(self, c, channel_id, state=None):
        channel = self.id2channel(channel_id)
        if state is not None:
            channel.manual_state = state
            board = self.boards[channel.board]
            self.write_channel_stateinvs(board)
	self.notify_listeners(c)
        return channel.manual_state

    @setting(6, 'channel invert', channel_id='s', invert='i')
    def channel_invert(self, c, channel_id, invert=None):
        channel = self.id2channel(channel_id)
        if invert is not None:
            channel.invert = invert
            board = self.boards[channel.board]
            self.write_channel_stateinvs(board)
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
