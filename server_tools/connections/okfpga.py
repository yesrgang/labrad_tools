import os

from twisted.internet.defer import inlineCallbacks
from labrad.wrappers import connectAsync

LABRADHOST = os.getenv('LABRADHOST')

class OKFPGAConnection(object):
    @inlineCallbacks
    def initialize(self, device):
        self.connection = yield connectAsync(LABRADHOST)
        self.server = yield self.connection[device.servername]

        yield self.server.select_interface(device.address)
    
    @inlineCallbacks
    def program_bitfile(self, bit_file):
        yield self.server.program_bitfile(bit_file)
    
    @inlineCallbacks
    def write_to_pipe_in(self, wire, byte_array):
        yield self.server.write_to_pipe_in(wire, byte_array)
    
    @inlineCallbacks
    def set_wire_in(self, wire, value):
        yield self.server.set_wire_in(wire, value)
    
    @inlineCallbacks
    def update_wire_ins(self):
        yield self.server.update_wire_ins()


