import json

from twisted.internet.defer import inlineCallbacks, returnValue

from server_tools.device_server import Device
from lib.analog_ramps import RampMaker
from lib.helpers import time_to_ticks
from lib.helpers import voltage_to_signed
from lib.helpers import voltage_to_unsigned
from lib.helpers import ramp_rate

T_WAIT_TRIG = 42.94967294


class YeSrAnalogBoard(Device):
    sequencer_type = 'analog'

    okfpga_server_name = None
    okfpga_device_id = None
    
    channels = None

    bitfile = 'analog_sequencer-v2b.bit'
#    bitfile = 'analog_sequencer.bit'

    mode_ints = {'idle': 0, 'load': 1, 'run': 2}
    mode_wire = 0x00
    sequence_pipe = 0x80
    channel_mode_wire = 0x09
    manual_voltage_wires = [0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08]
    clk = 48e6 / (8.*2. + 2.)
    mode = 'idle'

    sequence_bytes = None

    @inlineCallbacks
    def initialize(self):
        self.mode = 'idle'
        assert len(self.channels) ==  8
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
        """ 
        take readable {channel: [{}]} to programmable [ramp_rate[16], duration[32]] + ...
        """

        for channel in self.channels:
            assert channel.key in sequence
            channel_sequence = sequence[channel.key]
            vf = channel_sequence[-1]['vf']
            channel_sequence.append({'dt': 10, 'type': 'lin', 'vf': vf})

            # uncommenting for quto-trigger
            channel_sequence = [cs for cs in channel_sequence if cs['dt'] < T_WAIT_TRIG]

            try:
                channel.set_sequence(channel_sequence)
            except:
                print channel.name
                print channel_sequence

        unsorted_ramps = []
        for channel in self.channels:
            for ramp in channel.sequence:
                vi_bits = voltage_to_signed(ramp['vi'])
                vf_bits = voltage_to_signed(ramp['vf'])
                dv_bits = vf_bits - vi_bits

                ti_ticks = time_to_ticks(self.clk, ramp['ti'])
                tf_ticks = time_to_ticks(self.clk, ramp['tf'])
                dt_ticks = tf_ticks - ti_ticks

                dv_bytes = [int(eval(hex(ramp_rate(dv_bits, dt_ticks))) >> i & 0xff)
                    for i in range(0, 16, 8)]
                dt_bytes = [int(eval(hex(dt_ticks)) >> i & 0xff) 
                    for i in range(0, 32, 8)]

                unsorted_ramps.append((ti_ticks, channel.loc, dv_bytes, dt_bytes))
        
        sorted_ramps = sorted(unsorted_ramps)

        sequence_bytes = []
        for (t, loc, dv, dt) in sorted_ramps:
            sequence_bytes += dv
            sequence_bytes += dt
        sequence_bytes += [0] * 6

        return sequence_bytes
    
    @inlineCallbacks
    def write_channel_modes(self):
        cm_list = [c.mode for c in self.channels]
        value = sum([2**j for j, m in enumerate(cm_list) if m == 'manual'])
        yield self.okfpga_server.set_wire_in(self.channel_mode_wire, value)
        yield self.okfpga_server.update_wire_ins()
    
    @inlineCallbacks
    def write_channel_manual_outputs(self): 
        for c, w in zip(self.channels, self.manual_voltage_wires):
            v = voltage_to_unsigned(c.manual_output)
            yield self.okfpga_server.set_wire_in(w, v)
        yield self.okfpga_server.update_wire_ins()
