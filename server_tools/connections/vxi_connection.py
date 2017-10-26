import os
from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet.threads import deferToThread
from vxi11 import Instrument
from labrad.wrappers import connectAsync

from server_tools.connections.connection import Connection

class VXIConnection(Connection):
    @inlineCallbacks
    def initialize(self, device):
        yield self.connect(device)
        self.server = self.connection[device.servername]
        yield self.server.select_interface(device.address)

    @inlineCallbacks
    def write(self, data):
        yield self.server.write(data)
    
    @inlineCallbacks
    def read(self):
        ans = yield self.server.read()
        returnValue(ans)
    
    @inlineCallbacks
    def query(self, data):
        ans = yield self.server.query(data)
        returnValue(ans)

    @inlineCallbacks
    def timeout(self, timeout):
        ans = yield self.server.timeout(timeout)
        returnValue(ans)

#class VXIConnection(object):
#    @inlineCallbacks
#    def initialize(self, device):
#        yield None
#        self.connection = Instrument(device.address)
#
#    @inlineCallbacks 
#    def write(self, value):
#        yield deferToThread(self.connection.write, value)
#    
#    @inlineCallbacks 
#    def ask(self, value):
#        ans = yield deferToThread(self.connection.ask, value)
#        returnValue(ans)
#

