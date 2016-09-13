from twisted.internet.defer import inlineCallbacks, returnValue
from lib.analog_ramps import RampMaker

VOLTAGE_RANGE = (-10., 10.)
DAC_BITS = 16

def time_to_ticks(clk, time):
    return int(clk*time)

def voltage_to_signed(voltage):
    voltage_span = float(max(VOLTAGE_RANGE) - min(VOLTAGE_RANGE))
    voltage = sorted([-voltage_span, voltage, voltage_span])[1]
    return int(voltage/voltage_span*(2**DAC_BITS-1))

def voltage_to_unsigned(voltage):
    min_voltage = min(VOLTAGE_RANGE)
    max_voltage = max(VOLTAGE_RANGE)
    voltage_span = float(max(VOLTAGE_RANGE) - min(VOLTAGE_RANGE))
    voltage = sorted([min_voltage, voltage, max_voltage])[1] - min_voltage
    return int(voltage/voltage_span*(2**DAC_BITS-1))

def ramp_rate(voltage_diff, clk, time):
    v = voltage_to_signed(voltage_diff)
    t = time_to_ticks(clk, time)
    signed_ramp_rate = int(v*2.**int(np.log2(t)-1)/t)
    if signed_ramp_rate > 0:
        return signed_ramp_rate
    else:
        return signed_ramp_rate + 2**DAC_BITS

class AnalogChannel(object):
    """ wrapper for single analog channel on yesr dacbord 

    example_config = {
        'loc': 0, # in range(8)
        'name': 'DACA0', # unique string 
        'mode': 'auto', # 'auto' or 'manual'
        'manual_output': 0, # default manual voltage. between -10, 10.
    }
    """
    channel_type = 'analog'
    def __init__(self, config):
        """ defaults """
        self.mode = 'auto'
        self.manual_output = 'manual'
        board_name = config['board_name']
        loc = config['loc']
        self.name = 'DAC'+board_name+str(loc).zfill(2)
        
        """ non-defaults """
        for key, value in config.items():
            setattr(self, key, value)
        
        self.loc = self.board_name + str(self.loc).zfill(2)
        self.key = self.name+'@'+self.loc
   
    @inlineCallbacks
    def set_mode(self, mode):
        self.mode = mode
        yield self.board.write_channel_modes()

    @inlineCallbacks
    def set_manual_output(self, manual_output):
        self.manual_output = manual_output
        yield self.board.write_channel_manual_outputs()


class AnalogBoard(object):
    sequencer_type = 'analog'
    def __init__(self, config):
        """ defaults """
        self.update_parameters = []
        self.init_commands = []

        self.bitfile = 'analog_sequencer.bit'
        self.mode_ints = {'idle': 0, 'load': 1, 'run': 2}
        self.mode_wire = 0x00
        self.sequence_pipe = 0x80
        self.channel_mode_wire = 0x09
        self.manual_voltage_wires = [0x01, 0x02, 0x03, 0x04, 
                                     0x05, 0x06, 0x07, 0x08]
        self.clk = 48e6 / (8.*2. + 2.)
        self.mode = 'idle'

        channel_wrappers = [AnalogChannel({'loc': i, 'board_name': self.name})
                            for i in range(8)]

        """ non-defaults"""
        for key, value in config.items():
            setattr(self, key, value)
        
        for c in self.channels:
            c['board_name'] = self.name
            wrapper = AnalogChannel(c)
            channel_wrappers[c['loc']] = wrapper

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

    def make_sequence_bytes(self, sequence):
        """ 
        take readable {channel: [{}]} to programmable [ramp_rate[16], duration[32]]
        """
        
        # ramp to zero at end
        for c in self.channels:
            sequence[c.key].append({'dt': 10e-3, 'type': 'lin', 'vf': 0})
            sequence[c.key].append({'dt': 10, 'type': 'lin', 'vf': 0})

        # break into smaller pieces [(T, loc, {dt, dv})]
        unsorted_ramps = []
        for c in self.channels:
            ramps = RampMaker(sequence[c.key]).get_programmable()
            T = 0
            for r in ramps:
                unsorted_ramps.append((T, c.loc, r))
                T += time_to_ticks(self.clk, r['dt'])

        # order ramps by when the happen, then physical location on board
        sorted_ramps = sorted(unsorted_ramps)
        
        # ints to bytes
        ba = []
        for r in sorted_ramps:
            ba += [int(eval(hex(self.ramp_rate(board, r[2]['dv'], r[2]['dt']))) 
                       >> i & 0xff) for i in range(0, 16, 8)]
            ba += [int(eval(hex(self.time_to_ticks(board, r[2]['dt']))) 
                       >> i & 0xff) for i in range(0, 32, 8)]
        
        # add dead space
        ba += [0]*24
        return bytearray(ba)
    
    @inlineCallbacks
    def write_channel_modes(self):
        cm_list = [c.mode for c in self.channels]
        value = sum([2**j for j, m in enumerate(cm_list) if m == 'manual'])
        yield self.connection.set_wire_in(self.channel_mode_wire, value)
        yield self.connection.update_wire_ins()
    
    @inlineCallbacks
    def write_channel_manual_outputs(self): 
        for c, w in zip(self.channels, self.manual_voltage_wires):
            v = voltage_to_unsigned(c.manual_output)
            yield self.connection.set_wire_in(w, v)
        yield self.connection.update_wire_ins()

