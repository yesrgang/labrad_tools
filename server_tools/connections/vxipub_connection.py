from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet.threads import deferToThread
from vxi11 import Instrument

class VXIPubConnection(object):
    """ for vxi connections with public addresses """
    @inlineCallbacks
    def initialize(self, device):
        yield None
        self.connection = Instrument(device.address)

    @inlineCallbacks 
    def write(self, value):
        yield deferToThread(self.connection.write, value)
    
    @inlineCallbacks 
    def ask(self, value):
        ans = yield deferToThread(self.connection.ask, value)
        returnValue(ans)
    
    @inlineCallbacks 
    def query(self, value):
        ans = yield deferToThread(self.connection.ask, value)
        returnValue(ans)
