import os

from twisted.internet.defer import inlineCallbacks
import labrad.units as U
from labrad.wrappers import connectAsync

LABRADHOST = os.getenv('LABRADHOST')

class GPIBConnection(object):
    @inlineCallbacks
    def initialize(self, device):
        self.connection = yield connectAsync(LABRADHOST)
        self.server = self.connection[device.servername]
        self.context = self.server.context()

        self.server.address(device.address, context=self.context)
        if hasattr(device, 'timeout'):
            self.server.timeout(device.timeout, context=self.context)
        else:
            self.server.timeout(1 * U.s, context=self.context)

    def write(self, data):
        return self.server.write(data, context=self.context)

    def read(self, n_bytes=None):
        return self.server.read(n_bytes, context=self.context)

    def query(self, data):
        return self.server.query(data, context=self.context)

    def list_devices(self):
        return self.server.list_devices(context=self.context)
