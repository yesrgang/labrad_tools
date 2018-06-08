import json
from twisted.internet.defer import inlineCallbacks

class DigitalChannel(object):
    channel_type = 'digital'

    def __init__(self, loc=None, name=None, mode='auto', manual_output=False,
            invert=False):
        self.loc = loc
        self.name = str(name)
        self.mode = str(mode)
        self.manual_output = bool(manual_output)
        self.invert = bool(invert)

    def set_board(self, board):
        self.board = board
        row, column = self.loc
        self.board_loc = str(row) + str(column).zfill(2)
        self.key = self.name + '@' + self.board_loc
   
    @inlineCallbacks
    def set_mode(self, mode):
        if mode not in ('auto', 'manual'):
            message = 'channel mode {} not valid'.format(mode)
            raise Exception(message)
        self.mode = mode
        yield self.board.write_channel_modes()

    @inlineCallbacks
    def set_manual_output(self, state):
        self.manual_output = bool(state)
        yield self.board.write_channel_manual_outputs()
    
    def set_sequence(self, sequence):
        self.sequence = sequence
    
    def channel_info(self):
        device_info = {x: getattr(self, x) for x in dir(self) if x[0] != '_'}
        device_info = json.loads(json.dumps(device_info, default=lambda x: None))
        device_info = {k: v for k, v in device_info.items() if v is not None}
        return device_info
