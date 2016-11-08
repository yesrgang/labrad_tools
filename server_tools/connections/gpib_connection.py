import os

from twisted.internet.defer import inlineCallbacks, returnValue
from labrad.wrappers import connectAsync

LABRADHOST = os.getenv('LABRADHOST')

class GPIBConnection(object):
    @inlineCallbacks
    def initialize(self, device):
        self.connection = yield connectAsync(LABRADHOST)
        self.server = self.connection[device.servername]
        yield self.server.select_interface(device.address)

    @inlineCallbacks
    def write(self, data):
        yield self.server.write(data)
    
    @inlineCallbacks
    def read(self, n_bytes=None):
        ans = yield self.server.read(n_bytes)
        returnValue(ans)
    
    @inlineCallbacks
    def query(self, data):
        ans = yield self.server.query(data)
        returnValue(ans)

    @inlineCallbacks
    def list_devices(self):
        ans = yield self.server.list_devices()
        returnValue(ans)

    @inlineCallbacks
    def timeout(self, timeout):
        ans = yield self.server.timeout(timeout)
        returnValue(ans)
