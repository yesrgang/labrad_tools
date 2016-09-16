from twisted.internet.defer import inlineCallbacks, returnValue

def time_to_ticks(clk, time):
    return int(clk*time)

def get_out(channel_sequence, t):
    for s in channel_sequence[::-1]:
        if s['t'] <= t:
            return s['out']

class DigitalChannel(object):
    channel_type = 'digital'
    def __init__(self, config):
        """ defaults """
        self.mode = 'auto'
        self.manual_output = 0
        self.invert = 0

        row, col = config['loc']
        self.rowcol = [row, col]
        self.name = 'TTL'+row+str(col).zfill(2)
        
        """ non-defaults """
        for key, value in config.items():
            setattr(self, key, value)
         
        self.loc = row+str(col).zfill(2)
        self.key = self.name+'@'+self.loc
   
    @inlineCallbacks
    def set_mode(self, mode):
        self.mode = mode
        yield self.board.write_channel_modes()

    @inlineCallbacks
    def set_manual_output(self, state):
        self.state = state
        yield self.board.write_channel_manual_outputs()

class DigitalBoard(object):
    sequencer_type = 'digital'
    def __init__(self, config):
        """ defaults """
        self.update_parameters = []
        self.init_commands = []

        self.bitfile = 'digital_sequencer.bit'
        self.mode_ints = {'idle': 0, 'load': 1, 'run': 2}
        self.mode_wire = 0x00
        self.sequence_pipe = 0x80
        self.channel_mode_wires = [0x01, 0x03, 0x05, 0x07]
        self.state_invert_wires = [0x02, 0x04, 0x06, 0x08]
        self.clk = 50e6
        self.mode = 'idle'
       
        channel_wrappers = [
                DigitalChannel({'loc': [x, i], 'board_name': self.name})
                for x in self.name for i in range(16)]

        """ non-defaults"""
        for key, value in config.items():
            setattr(self, key, value)
        
        for c in self.channels:
            c['board_name'] = self.name
            wrapper = DigitalChannel(c)
            row, column = wrapper.rowcol
            channel_wrappers[(ord(row)%32-1)*16 + column] = wrapper
        self.channels = channel_wrappers

        for c in self.channels:
            c.board = self

    @inlineCallbacks
    def initialize(self):
        yield self.connection.program_bitfile(self.bitfile)
        yield self.write_channel_modes()
        yield self.write_channel_manual_outputs()

    @inlineCallbacks
    def set_mode(self, mode):
        mode_int = self.mode_ints[mode]
        yield self.connection.set_wire_in(self.mode_wire, mode_int)
        yield self.connection.update_wire_ins()
        self.mode = mode

    @inlineCallbacks
    def program_sequence(self, sequence):
        byte_array = self.make_sequence_bytes(sequence)
        yield self.set_mode('idle')
        yield self.set_mode('load')
        yield self.connection.write_to_pipe_in(self.sequence_pipe, byte_array)
        yield self.set_mode('idle')

    @inlineCallbacks
    def start_sequence(self):
        yield self.set_mode('run')

    def make_sequence(self, sequence):
        # make sure trigger happens on first run
        for c in self.channels:
            sequence[c.key].insert(0, sequence[c.key][0])
        sequence['Trigger@D15'][0]['out'] = 1

        # allow for analog's ramp to zero
        for c in self.channels:
            sequence[c.key].append(sequence[c.key][-1])
        sequence['Trigger@D15'][-1]['out'] = 1

        for c in self.channels:
            total_ticks = 0
            for s in sequence[c.key]:
                dt = time_to_ticks(self.clk, s['dt'])
                s.update({'dt': dt, 't': total_ticks})
                total_ticks += dt

        t_ = sorted(list(set([s['t'] for c in self.channels 
                                     for s in sequence[c.key]])))
        

        # for now, assume each channel_sequence has same timings
        programmable_sequence = [(dt, [sequence[c.key][i] 
                for c in board.channels]) 
                for i, dt in enumerate(sequence[self.timing_channel])]
        
        ba = []
        for t, l in programmable_sequence:
            ba += list([sum([2**j for j, b in enumerate(l[i:i+8]) if b]) 
                    for i in range(0, 64, 8)])
            ba += list([int(eval(hex(self.time_to_ticks(board, t))) 
                    >> i & 0xff) for i in range(0, 32, 8)])
        ba += [0]*96
        return ba
    
    @inlineCallbacks
    def write_channel_modes(self):
        cm_list = [c.mode for c in self.channels]
        values = [sum([2**j for j, m in enumerate(cm_list[i:i+16]) 
                if m == 'manual']) for i in range(0, 64, 16)]
        for value, wire in zip(values, self.channel_mode_wires):
            yield self.connection.set_wire_in(wire, value)
        yield self.connection.update_wire_ins()
   
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
            yield self.connection.set_wire_in(wire, value)
        yield self.connection.update_wire_ins()
