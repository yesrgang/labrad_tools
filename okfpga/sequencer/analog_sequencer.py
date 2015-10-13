"""
### BEGIN NODE INFO
[info]
name = Analog Sequencer
version = 1.0
description = 
instancename = %LABRADNODE% Analog Sequencer

[startup]
cmdline = %PYTHON% %FILE%
timeout = 20

[shutdown]
message = 987654321
timeout = 20
### END NODE INFO
"""
import json
import time
import numpy as np
import ok

from labrad.server import LabradServer, setting, Signal
from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet.threads import deferToThread

from analog_errors import *

class AnalogSequencerServer(LabradServer):
    name = '%LABRADNODE% Analog Sequencer'
    mode='idle'

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
        for board in self.boards:
            success = self.initialize_board(board)
	        if not success:
                self.boards.pop(board)
        self.initialize_outputs()

    def initialize_board(self, board):
        fp = ok.FrontPanel()
        module_count = fp.GetDeviceCount()
        print "Found {} unused modules".format(module_count)
        for i in range(module_count):
            serial = fp.GetDeviceListSerial(i)
            tmp = ok.FrontPanel()
            tmp.OpenBySerial(serial)
            iden = tmp.GetDeviceID()
            if iden == board.device_id:
                board.xem = tmp
                print 'Connected to {}'.format(iden)
                board.xem.LoadDefaultPLLConfiguration() 
                prog = board.xem.ConfigureFPGA(board.bit_file)
                if prog:
                   print "unable to program sequencer"
				   return False
                return True
        return False

    def initialize_outputs(self):
        for b in self.boards:
            self.write_channel_modes(b)
            for c in b.channels:
                self.write_manual_voltage(c)

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
                for c in b.channels.values():
                    if c.name == name:
                        channel = c
        if not channel:
            for b in self.boards.values():
                for c in b.channels.values():
                    if c.loc == loc:
                        channel = c
        return channel

    def time_to_ticks(self, board, time):
        return int(board.clk_frequency*time)

    def voltage_to_signed(self, voltage):
        voltage = sorted([-20, voltage, 20])[1]
        return int(voltage/20.*(2**16-1))

    def voltage_to_unsigned(self, voltage):
        voltage = sorted([-10., voltage, 10.])[1] + 10.
        return int(voltage/20.*(2**16-1))

    def ramp_rate(self, board, voltage_diff, time):
        t = self.time_to_ticks(board, time)
        v = self.voltage_to_signed(voltage_diff)
        signed_ramp_rate = int(v*2.**int(np.log2(t)-1)/t)
        if signed_ramp_rate > 0:
            return signed_ramp_rate
        else:
            return signed_ramp_rate + 2**16

    def make_sequence(self, board, sequence):
        # sequence is list of tuples [(duration, {iden: {ramp_info}})] 
        
        # ramp to zero at end
        sequence.append((10e-3, {k: {'type': 'linear', 'vf': 0.} for k in board.channels.keys()}))

        # add parameter vi to each ramp, 
        for k in board.channels.keys():
            sequence[0][1][k]['vi'] = 0
            for i in range(len(sequence)):
                sequence[i+1][1][k]['vi'] = sequence[i][1][k]['vf']
        
        
        # break into smaller pieces [(T, loc, {dt, dv})]
        T = 0
        unsorted_sequence = []
        for s in sequence:
            for channel in board.channels.values():
                s[1][channel.key]['dt'] = s[0]
                ss = (s[0], channel.loc, s[1][channel.key])
                unsorted_sequence += ramps[ss[2]['type']](ss)
            T += s[0]
        
        sorted_sequence = sorted(sequence3)

        ba = []

        for s in sorted_sequence:
            ba += [int(eval(hex(self.ramp_rate(board, s[2]['dv'], s[2]['dt']))) >> i & 0xff) for i in range(0, 16, 8)]
            ba += [int(eval(hex(self.time_to_ticks(board, s[2]['dt']))) >> i & 0xff) for i in range(0, 32, 8)]
        
        ba += [0]*24
        print 'writing ', len(ba), ' bytes...'
        return ba
    
    def program_sequence(self, sequence):
        for board in self.boards.values():
            ba = self.make_sequence(board, sequence)
            self.set_board_mode(board, 'idle')
            self.set_board_mode(board, 'load')
            board.xem.WriteToPipeIn(0x80, bytearray(ba))
            self.set_board_mode(board, 'idle')
    
    def set_board_mode(self, board, mode):
        board.xem.SetWireInValue(board.mode_wire, board.mode_nums[mode])
        board.xem.UpdateWireIns()
        board.mode = mode

    @setting(01, 'get channels')
    def get_channels(self, c):
        channels = {}
        for b in self.boards.values():
            for k, c in b.channels.items():
                channels[k] = c.__dict__
        return str(channels)

    @setting(07, 'program sequence', sequence='s')
    def run_sequence(self, c, sequence):
        sequence = json.loads(sequence)
        self.program_sequence(sequence)
        for board in self.boards.values():
            self.set_board_mode(board, 'run')

    @setting(03, 'sequencer mode', mode='s')
    def sequencer_mode(self, c, mode=None):
        if mode is not None:
            for board in self.boards.values():
                self.set_board_mode(board, mode)
            self.mode = mode
        return self.mode

    @setting(04, 'channel mode', channel_id='s', mode='s')
    def channel_mode(self, c, channel_id, mode=None):
        channel = self.id2channel(channel_id)
        if not channel:
            raise ChannelNotFound()
        if mode is not None:
            channel.mode = mode
            board = self.boards[channel.loc[0]]
            self.write_channel_modes(board)
        self.notify_listeners(c)
        return channel.mode
    
    def write_channel_modes(self, board): 
        cm_list = [c.mode for k, c in sorted(board.channels.items())]
        mode_value = sum([2**j for j, m in enumerate(cm_list) if m == 'manual'])
        board.xem.SetWireInValue(board.channel_mode_wire, mode_value)
        board.xem.UpdateWireIns()
    
    @setting(05, 'channel manual voltage', channel_id='s', voltage='v')
    def channel_manual_voltage(self, c, channel_id, voltage=None):
        channel = self.id2channel(channel_id)
        if not channel:
            raise ChannelNotFound()
        if voltage is not None:
            voltage = sorted([-10, voltage, 10])[1]
            channel.manual_voltage = voltage
            self.write_manual_voltage(channel)
        self.notify_listeners(c)
        return channel.manual_voltage

    def write_manual_voltage(self, channel): 
        board = self.boards[channel.loc[0]]
        wire = board.manual_voltage_wires[channel.loc[1:]]
        voltage = self.voltage_to_unsigned(channel.manual_voltage)
        board.xem.SetWireInValue(wire, voltage)
        board.xem.UpdateWireIns()

    @setting(06, 'get channel configuration', channel_id='s')
    def get_channel_configuration(self, c, channel_id):
        channel = self.id2channel(channel_id)
        return json.dumps(channel.__dict__)

    @setting(10, 'notify listeners')
    def notify_listeners(self, c):
        self.update(json.dumps(self.channels))

if __name__ == "__main__":
    config_name = 'analog_config'
    __server__ = AnalogSequencerServer(config_name)
    from labrad import util
    util.runServer(__server__)
