import os

from twisted.internet.defer import inlineCallbacks
from labrad.wrappers import connectAsync

LABRADHOST = os.getenv('LABRADHOST')

class OKFPGAConnection(object):
    @inlineCallbacks
    def initialize(self, device):
        self.connection = yield connectAsync(LABRADHOST)
        self.server = yield self.connection[device.servername]
        self.context = self.server.context()
        self.ID = self.server.ID

        self.server.open(device.address)

    def load_bit(self, bit_file):
        return self.server.load_bit(bit_file)
        
    def write_to_pipe_in(self, wire, byte_array):
        return self.server.write_to_pipe_in(wire, byte_array)

    def set_wire_in(self, wire, value):
        return self.server.set_wire_in(wire, value)

    def update_wire_ins(self):
        return self.server.update_wire_ins()


