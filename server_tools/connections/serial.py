import os

from twisted.internet.defer import inlineCallbacks, returnValue
from labrad.wrappers import connectAsync

LABRADHOST = os.getenv('LABRADHOST')

class SerialConnection(object):
    @inlineCallbacks
    def initialize(self, device):
        self.connection = yield connectAsync(LABRADHOST)
        self.server = yield self.connection[device.servername]
        self.context = yield self.server.context()
        self.ID = self.server.ID

        yield self.server.open(device.address)
        
        for attr in ['timeout', 'baudrate', 'stopbits', 'bytesize']:
            if hasattr(device, attr): 
                value = getattr(device, attr)
                yield getattr(self.server, attr)(value)
    
    @inlineCallbacks
    def baudrate(self, x=None):
        yield self.server.baudrate(x)
   
    @inlineCallbacks
    def timeout(self, x=None):
        yield self.server.timeout(x)
    
    @inlineCallbacks
    def write(self, x):
        yield self.server.write(x)

    @inlineCallbacks
    def write_line(self, x):
        return self.server.write_line(x)

    def write_lines(self, x):
        return self.server.write_lines(x)

    def read(self, x=0):
        return self.server.read(x)

    def read_line(self):
        return self.server.read_line()

    def read_lines(self):
        return self.server.read()

    def close(self):
        return self.server.close()

    def flushinput(self):
        return self.server.flushinput()

    def flushoutput(self):
        return self.server.flushoutput()
