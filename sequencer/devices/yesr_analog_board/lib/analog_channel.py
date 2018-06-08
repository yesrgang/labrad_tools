import json
from twisted.internet.defer import inlineCallbacks

from analog_ramps import RampMaker

class AnalogChannel(object):
    channel_type = 'analog'
    dac_voltage_range = (-10.0, 10.0)
    dac_bits = 16

    def __init__(self, loc=None, name=None, mode='auto', manual_output=0.0, 
            voltage_range=(-10.0, 10.0)):
        self.loc = int(loc)
        self.name = str(name)
        self.mode = str(mode)
        self.manual_output = float(manual_output)
        self.software_voltage_range = voltage_range
        self.min_voltage = min(voltage_range)
        self.max_voltage = max(voltage_range)

    def set_board(self, board):
        self.board = board
        self.board_loc = board.name.upper() + str(self.loc).zfill(2)
        self.key = self.name + '@' + self.board_loc

    @inlineCallbacks
    def set_mode(self, mode):
        if mode not in ('auto', 'manual'):
            message = 'channel mode {} not valid'.format(mode)
            raise Exception(message)
        self.mode = mode
        yield self.board.write_channel_modes()
    
    @inlineCallbacks
    def set_manual_output(self, manual_output):
        if not (self.min_voltage <= manual_output <= self.max_voltage):
            message = 'channel output {} not in range [{}, {}]'.format(mode, 
                self.min_voltage, self.max_voltage)
            raise Exception(message)
        self.manual_output = manual_output
        yield self.board.write_channel_manual_outputs()

    def set_sequence(self, sequence):
        self.sequence = RampMaker(sequence).get_programmable()

    def channel_info(self):
        device_info = {x: getattr(self, x) for x in dir(self) if x[0] != '_'}
        device_info = json.loads(json.dumps(device_info, default=lambda x: None))
        device_info = {k: v for k, v in device_info.items() if v is not None}
        return device_info

