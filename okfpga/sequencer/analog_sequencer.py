"""
### BEGIN NODE INFO
[info]
name = analog_sequencer
version = 1.0
description = 
instancename = %LABRADNODE%_analog_sequencer

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
        for board in self.boards.values():
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
        for b in self.boards.values():
            self.write_channel_modes(b)
            for c in b.channels:
                self.write_manual_voltage(c)

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

    def voltage_to_signed(self, voltage):
        """for signed voltage difference to ramp"""
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
        """take readable {channel: [{}]} to programmable [ramp_rate[16], duration[32]]"""

        # channel keys might not match available channels, handle this
        #sequence = self._fix_sequence_keys(sequence)
        
        # ramp to zero at end
        for c in board.channels:
            sequence[c.key].append({'dt': 10e-3, 'type': 'lin', 'vf': 0})
            sequence[c.key].append({'dt': 10, 'type': 'lin', 'vf': 0})

        # break into smaller pieces [(T, loc, {dt, dv})]
        unsorted_ramps = []
        for c in board.channels:
            ramps = RampMaker(sequence[c.key]).get_programmable()
            T = 0
            for r in ramps:
                #T = float('{0:.7f}'.format(T)) # round to ns
                unsorted_ramps.append((T, c.loc, r))
                #T += r['dt']
                T += self.time_to_ticks(board, r['dt'])

        # order ramps by when the happen, then physical location on board
        sorted_ramps = sorted(unsorted_ramps)
        
        # ints to bytes
        ba = []
        for r in sorted_ramps:
            ba += [int(eval(hex(self.ramp_rate(board, r[2]['dv'], r[2]['dt']))) >> i & 0xff) for i in range(0, 16, 8)]
            ba += [int(eval(hex(self.time_to_ticks(board, r[2]['dt']))) >> i & 0xff) for i in range(0, 32, 8)]
#            dv = float('{0:.3f}'.format(r[2]['dv'])) # round to mV
#            dt = float('{0:.6f}'.format(r[2]['dt'])) # round to us
#            ba += [int(eval(hex(self.ramp_rate(board, dv, dt))) >> i & 0xff) for i in range(0, 16, 8)]
#            ba += [int(eval(hex(self.time_to_ticks(board, dt))) >> i & 0xff) for i in range(0, 32, 8)]
        
        # add dead space
        ba += [0]*24
        return bytearray(ba)
    
    def program_sequence(self, sequence):
        for board in self.boards.values():
            byte_array = self.make_sequence(board, sequence)
            self.set_board_mode(board, 'idle')
            self.set_board_mode(board, 'load')
            board.xem.WriteToPipeIn(0x80, byte_array)
            self.set_board_mode(board, 'idle')
    
    def set_board_mode(self, board, mode):
        board.xem.SetWireInValue(board.mode_wire, board.mode_nums[mode])
        board.xem.UpdateWireIns()
        board.mode = mode

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
        for board in self.boards.values():
            self.set_board_mode(board, 'run')

    @setting(03, 'sequencer mode', mode='s')
    def sequencer_mode(self, c, mode=None):
        """manually set sequencer mode
        
        'idle': does nothing
        'load': listens to USB interface
        'run': plays sequence after external trigger
        """
        if mode is not None:
            for board in self.boards.values():
                self.set_board_mode(board, mode)
            self.mode = mode
        return self.mode

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
        cm_list = [c.mode for c in board.channels]
        mode_value = sum([2**j for j, m in enumerate(cm_list) if m == 'manual'])
        board.xem.SetWireInValue(board.channel_mode_wire, mode_value)
        board.xem.UpdateWireIns()
    
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
        board = self.boards[channel.loc[0]]
        wire = board.manual_voltage_wires[channel.loc[1:]]
        voltage = self.voltage_to_unsigned(channel.manual_voltage)
        board.xem.SetWireInValue(wire, voltage)
        board.xem.UpdateWireIns()

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
