import os

from twisted.internet.defer import inlineCallbacks, returnValue
from labrad.wrappers import connectAsync

LABRADHOST = os.getenv('LABRADHOST')

class GPIBConnection(object):
    @inlineCallbacks
    def initialize(self, device):
        self.connection = yield connectAsync(LABRADHOST)
        self.server = self.connection[device.servername]
        self.context = yield self.server.context()

        yield self.server.connect(device.address, context=self.context)
#        if hasattr(device, 'timeout'):
#            self.server.timeout(device.timeout, context=self.context)
#        else:
#            self.server.timeout(1 * U.s, context=self.context)
    
    @inlineCallbacks
    def write(self, data):
        yield self.server.write(data, context=self.context)
    
    @inlineCallbacks
    def read(self, n_bytes=None):
        ans = yield self.server.read(n_bytes, context=self.context)
        returnValue(ans)
    
    @inlineCallbacks
    def query(self, data):
        ans = yield self.server.query(data, context=self.context)
        returnValue(ans)

    @inlineCallbacks
    def list_devices(self):
        ans = yield self.server.list_devices(context=self.context)
        returnValue(ans)
