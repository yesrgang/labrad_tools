import json
from twisted.internet.defer import inlineCallbacks, returnValue

from server_tools.device_server import Device

from lib.helpers import time_to_ticks
from lib.helpers import get_output

T_TRIG = 10e-6

T_END = 10e-3 
T_WAIT_TRIGGER = 42.94967294 # (2**31 - 1) / clk

TRIGGER_CHANNEL = 'Trigger@D15'


class YeSrDigitalBoard(Device):
    sequencer_type = 'digital'

    okfpga_server_name = None
    okfpga_device_id = None

    channels = None
        
#    bitfile = 'digital_sequencer.bit'
#    bitfile = 'digital_sequencer-v2.bit'
    bitfile = 'digital_sequencer-v2b.bit'
    mode_ints = {'idle': 0, 'load': 1, 'run': 2}
    mode_wire = 0x00
    sequence_pipe = 0x80
    channel_mode_wires = [0x01, 0x03, 0x05, 0x07]
    state_invert_wires = [0x02, 0x04, 0x06, 0x08]
    clk = 50e6
    mode = 'idle'
    
    sequence_bytes = None

    @inlineCallbacks
    def initialize(self):
        self.mode = 'idle'
        assert len(self.channels) == 64
        for channel in self.channels:
            channel.set_board(self)
        
        yield self.connect_labrad()
        self.okfpga_server = yield self.cxn[self.okfpga_server_name]
        yield self.okfpga_server.select_interface(self.okfpga_device_id)

        yield self.okfpga_server.program_bitfile(self.bitfile)
        yield self.write_channel_modes()
        yield self.write_channel_manual_outputs()

    @inlineCallbacks
    def set_mode(self, mode):
        mode_int = self.mode_ints[mode]
        yield self.okfpga_server.set_wire_in(self.mode_wire, mode_int)
        yield self.okfpga_server.update_wire_ins()
        self.mode = mode

#    @inlineCallbacks
#    def program_sequence(self, sequence):
#        sequence_bytes = self.make_sequence_bytes(sequence)
#        yield self.set_mode('idle')
#        yield self.set_mode('load')
#        yield self.okfpga_server.write_to_pipe_in(self.sequence_pipe, json.dumps(sequence_bytes))
#        yield self.set_mode('idle')
    @inlineCallbacks
    def program_sequence(self, sequence):
        sequence_bytes = self.make_sequence_bytes(sequence)
        yield self.set_mode('idle')
        if sequence_bytes != self.sequence_bytes:
            yield self.set_mode('load')
            yield self.okfpga_server.write_to_pipe_in(self.sequence_pipe, json.dumps(sequence_bytes))
            yield self.set_mode('idle')
        self.sequence_bytes = sequence_bytes


    @inlineCallbacks
    def start_sequence(self):
        yield self.set_mode('run')

    def make_sequence_bytes(self, sequence):
        # make sure trigger happens on first run
        for c in self.channels:
            s = {'dt': T_TRIG, 'out': sequence[c.key][0]['out']}
            sequence[c.key].insert(0, s)

        # trigger other boards
        for s in sequence[TRIGGER_CHANNEL]:
            if s['dt'] >= (2**31 - 2) / self.clk:
                s['out'] = True
            else:
                s['out'] = False
        sequence[TRIGGER_CHANNEL][0]['out'] = True

        # allow for analog's ramp to zero, last item will not be written
        sequence[TRIGGER_CHANNEL].append({'dt': T_END, 'out': True})

        for c in self.channels:
            total_ticks = 0
            for s in sequence[c.key]:
                dt = time_to_ticks(self.clk, s['dt'])
                s.update({'dt': dt, 't': total_ticks})
                total_ticks += dt

        # each sequence point updates all outs for some number of clock ticks
        # since some channels may have different 'dt's, every time any channel 
        # changes state we need to write all channel outs.
        t_ = sorted(list(set([s['t'] for c in self.channels 
                                     for s in sequence[c.key]])))
        dt_ = [t_[i+1] - t_[i] for i in range(len(t_)-1)] + [time_to_ticks(self.clk, T_END)]

        programmable_sequence = [(dt, [get_output(sequence[c.key], t) 
                for c in self.channels])
                for dt, t in zip(dt_, t_)]
        
        sequence_bytes = []
        for t, l in programmable_sequence:
            # each point in sequence specifies all 64 logic outs with 64 bit number
            # e.g. all off is 0...0, channel 1 on is 10...0
            sequence_bytes += list([sum([2**j for j, b in enumerate(l[i:i+8]) if b]) 
                    for i in range(0, 64, 8)])
            # time to keep these outs is 32 bit number in units of clk ticks
            sequence_bytes += list([int(eval(hex(t)) >> i & 0xff) 
                    for i in range(0, 32, 8)])
        sequence_bytes += [0]*24
        return sequence_bytes
    
    @inlineCallbacks
    def write_channel_modes(self):
        cm_list = [c.mode for c in self.channels]
        values = [sum([2**j for j, m in enumerate(cm_list[i:i+16]) 
                if m == 'manual']) for i in range(0, 64, 16)]
        for value, wire in zip(values, self.channel_mode_wires):
            yield self.okfpga_server.set_wire_in(wire, value)
        yield self.okfpga_server.update_wire_ins()
        yield self.write_channel_manual_outputs()
   
    @inlineCallbacks
    def write_channel_manual_outputs(self): 
        cm_list = [c.mode for c in self.channels]
        cs_list = [c.manual_output for c in self.channels]
        ci_list = [c.invert for c in self.channels]
        values = [sum([2**j for j, (m, s, i) in enumerate(zip(
                cm_list[i:i+16], cs_list[i:i+16], ci_list[i:i+16]))
                if (m=='manual' and s!=i) or (m=='auto' and i==True)]) 
                for i in range(0, 64, 16)]
        for value, wire in zip(values, self.state_invert_wires):
            yield self.okfpga_server.set_wire_in(wire, value)
        yield self.okfpga_server.update_wire_ins()
